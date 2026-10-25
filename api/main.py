from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
import os
import shutil
import tempfile
import threading
import time
import uuid

import fitz
from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from fastapi.responses import Response

from api.schemas import QuestionRequest, QuestionResponse
from services.rag_pipeline import RAGPipeline
from services.vector_store import VectorStore

app = FastAPI(title="InfoCite AI", version="2.1.0")

UPLOAD_DIR = Path("uploaded_pdfs")
UPLOAD_DIR.mkdir(exist_ok=True)
WORKSPACE_TTL_SECONDS = 24 * 60 * 60
MAX_ACTIVE_WORKSPACES = 50


@dataclass
class Workspace:
    workspace_id: str
    directory: Path
    pipeline: RAGPipeline
    last_access: float = field(default_factory=time.monotonic)
    lock: threading.RLock = field(default_factory=threading.RLock)


_workspaces: dict[str, Workspace] = {}
_workspaces_lock = threading.RLock()
_last_orphan_cleanup = 0.0


def _new_workspace(workspace_id: str) -> Workspace:
    directory = UPLOAD_DIR / workspace_id
    collection_name = f"ic_{uuid.UUID(workspace_id).hex}"
    if directory.exists() and time.time() - directory.stat().st_mtime > WORKSPACE_TTL_SECONDS:
        VectorStore(collection_name=collection_name).delete_collection()
        shutil.rmtree(directory, ignore_errors=True)
    directory.mkdir(parents=True, exist_ok=True)
    pipeline = RAGPipeline(collection_name=collection_name)
    pdfs = sorted(directory.glob("*.pdf"))
    if pdfs:
        pipeline.restore_documents(pdfs)
    return Workspace(workspace_id, directory, pipeline)


def _remove_expired_workspaces(now: float) -> None:
    expired = [
        key for key, workspace in _workspaces.items()
        if now - workspace.last_access > WORKSPACE_TTL_SECONDS
    ]
    for key in expired:
        workspace = _workspaces[key]
        if not workspace.lock.acquire(blocking=False):
            continue
        try:
            workspace.pipeline.vector_store.delete_collection()
            shutil.rmtree(workspace.directory, ignore_errors=True)
            del _workspaces[key]
        finally:
            workspace.lock.release()


def _remove_expired_orphan_directories(now: float) -> None:
    global _last_orphan_cleanup
    if now - _last_orphan_cleanup < 60 * 60:
        return
    _last_orphan_cleanup = now

    for directory in UPLOAD_DIR.iterdir():
        if not directory.is_dir() or directory.name in _workspaces:
            continue
        try:
            workspace_uuid = uuid.UUID(directory.name)
        except ValueError:
            continue
        if workspace_uuid.version != 4:
            continue
        if time.time() - directory.stat().st_mtime <= WORKSPACE_TTL_SECONDS:
            continue
        collection_name = f"ic_{workspace_uuid.hex}"
        try:
            VectorStore(collection_name=collection_name).delete_collection()
        except Exception:
            pass
        shutil.rmtree(directory, ignore_errors=True)


@contextmanager
def _workspace_for_request(workspace_id: str):
    try:
        parsed_id = uuid.UUID(workspace_id)
    except (ValueError, TypeError, AttributeError) as exc:
        raise HTTPException(status_code=400, detail="A valid workspace ID is required.") from exc
    if parsed_id.version != 4:
        raise HTTPException(status_code=400, detail="Workspace ID must be a UUID v4.")

    key = str(parsed_id)
    now = time.monotonic()
    with _workspaces_lock:
        _remove_expired_workspaces(now)
        _remove_expired_orphan_directories(now)
        workspace = _workspaces.get(key)
        if workspace is None:
            if len(_workspaces) >= MAX_ACTIVE_WORKSPACES:
                raise HTTPException(
                    status_code=429,
                    detail="The server is at its active workspace limit. Try again later.",
                )
            try:
                workspace = _new_workspace(key)
            except Exception as exc:
                raise HTTPException(
                    status_code=500,
                    detail=f"Unable to initialize this workspace: {exc}",
                ) from exc
            _workspaces[key] = workspace
        workspace.lock.acquire()
        workspace.last_access = now

    try:
        yield workspace
    finally:
        workspace.last_access = time.monotonic()
        os.utime(workspace.directory, None)
        workspace.lock.release()


@app.get("/")
def root():
    return {"message": "InfoCite AI API is running!"}


@app.post("/upload")
def upload_pdfs(
    files: list[UploadFile] = File(...),
    mode: str = Form("replace"),
    workspace_id: str = Header(..., alias="X-Workspace-ID"),
):
    if not files:
        raise HTTPException(status_code=400, detail="Please upload at least one PDF.")
    if mode not in {"replace", "add"}:
        raise HTTPException(status_code=400, detail="Mode must be 'replace' or 'add'.")
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum of 10 PDFs allowed per workspace.")

    with _workspace_for_request(workspace_id) as workspace:
        staged_paths = []
        safe_names = set()
        existing_pdfs = sorted(workspace.directory.glob("*.pdf")) if mode == "add" else []
        if len(existing_pdfs) + len(files) > 10:
            raise HTTPException(status_code=400, detail="Maximum of 10 PDFs allowed per workspace.")
        existing_names = {path.name.casefold() for path in existing_pdfs}
        with tempfile.TemporaryDirectory(dir=workspace.directory) as staging_dir:
            for file in files:
                original_name = Path(file.filename or "").name
                if not original_name or not original_name.lower().endswith(".pdf"):
                    raise HTTPException(status_code=400, detail="All uploads must be named PDF files.")
                if original_name.casefold() in safe_names:
                    raise HTTPException(status_code=400, detail=f"Duplicate filename: {original_name}")
                if original_name.casefold() in existing_names:
                    raise HTTPException(
                        status_code=400,
                        detail=f"{original_name} is already in this workspace. Remove it first or use Replace all.",
                    )
                safe_names.add(original_name.casefold())

                destination = Path(staging_dir) / original_name
                with destination.open("wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)
                if destination.stat().st_size == 0 or destination.read_bytes()[:5] != b"%PDF-":
                    raise HTTPException(
                        status_code=400,
                        detail=f"{original_name} is empty or is not a valid PDF file.",
                    )
                staged_paths.append(destination)

            try:
                workspace.pipeline.index_documents(existing_pdfs + staged_paths)
            except Exception as exc:
                raise HTTPException(status_code=422, detail=f"Unable to index documents: {exc}") from exc

            if mode == "replace":
                for pdf in workspace.directory.glob("*.pdf"):
                    if pdf.is_file():
                        pdf.unlink()
            for pdf in staged_paths:
                shutil.copy2(pdf, workspace.directory / pdf.name)

        return {
            "message": f"Successfully indexed {len(existing_pdfs) + len(staged_paths)} PDF(s).",
            "documents": [pdf.name for pdf in (existing_pdfs + [workspace.directory / path.name for path in staged_paths])],
            "index_stats": workspace.pipeline.index_stats,
        }


@app.post("/ask", response_model=QuestionResponse)
def ask(
    request: QuestionRequest,
    workspace_id: str = Header(..., alias="X-Workspace-ID"),
):
    with _workspace_for_request(workspace_id) as workspace:
        try:
            result = workspace.pipeline.ask(
                request.question,
                history=[turn.model_dump() for turn in request.history],
            )
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return QuestionResponse(**result)


@app.delete("/documents/{filename}")
def delete_document(
    filename: str,
    workspace_id: str = Header(..., alias="X-Workspace-ID"),
):
    if Path(filename).name != filename:
        raise HTTPException(status_code=400, detail="Invalid document name.")

    with _workspace_for_request(workspace_id) as workspace:
        target = workspace.directory / filename
        if not target.is_file() or target.suffix.lower() != ".pdf":
            raise HTTPException(status_code=404, detail="Document not found.")
        remaining = sorted(
            path for path in workspace.directory.glob("*.pdf") if path != target
        )
        if remaining:
            try:
                workspace.pipeline.index_documents(remaining)
            except Exception as exc:
                raise HTTPException(status_code=422, detail=f"Unable to rebuild index: {exc}") from exc
        else:
            workspace.pipeline.vector_store.reset()
            workspace.pipeline.bm25 = None
            workspace.pipeline.hybrid = None
            workspace.pipeline.index_stats = {
                "documents": 0,
                "chunks": 0,
                "retriever": "Hybrid",
                "embeddings": "sentence-transformers/all-MiniLM-L6-v2",
                "reranker": "cross-encoder/ms-marco-MiniLM-L6-v2",
                "llm": workspace.pipeline.llm.model,
            }
        target.unlink()
        return {
            "message": f"Removed {filename}.",
            "documents": [path.name for path in remaining],
            "index_stats": workspace.pipeline.index_stats,
        }


@app.delete("/documents")
def clear_documents(workspace_id: str = Header(..., alias="X-Workspace-ID")):
    with _workspace_for_request(workspace_id) as workspace:
        for path in workspace.directory.glob("*.pdf"):
            if path.is_file():
                path.unlink()
        workspace.pipeline.vector_store.reset()
        workspace.pipeline.bm25 = None
        workspace.pipeline.hybrid = None
        workspace.pipeline.index_stats = {
            "documents": 0,
            "chunks": 0,
            "retriever": "Hybrid",
            "embeddings": "sentence-transformers/all-MiniLM-L6-v2",
            "reranker": "cross-encoder/ms-marco-MiniLM-L6-v2",
            "llm": workspace.pipeline.llm.model,
        }
        return {"message": "Workspace documents cleared.", "documents": [], "index_stats": workspace.pipeline.index_stats}


@app.get("/documents/{filename}/pages/{page_number}/preview")
def preview_document_page(
    filename: str,
    page_number: int,
    workspace_id: str = Header(..., alias="X-Workspace-ID"),
):
    if Path(filename).name != filename:
        raise HTTPException(status_code=400, detail="Invalid document name.")

    with _workspace_for_request(workspace_id) as workspace:
        path = workspace.directory / filename
        if not path.is_file() or path.suffix.lower() != ".pdf":
            raise HTTPException(status_code=404, detail="Document not found in this workspace.")
        try:
            with fitz.open(path) as document:
                if page_number < 1 or page_number > len(document):
                    raise HTTPException(status_code=404, detail="Page not found.")
                page = document.load_page(page_number - 1)
                image = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).tobytes("png")
        except fitz.FileDataError as exc:
            raise HTTPException(status_code=422, detail="Unable to read this PDF.") from exc
        return Response(content=image, media_type="image/png")
