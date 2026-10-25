from pathlib import Path
import shutil
import tempfile

from fastapi import (
    FastAPI,
    UploadFile,
    File,
    HTTPException,
)

from api.schemas import (
    QuestionRequest,
    QuestionResponse,
)

from services.rag_pipeline import RAGPipeline

app = FastAPI(
    title="InfoCite AI",
    version="2.0.0",
)

# Initialize once when the server starts
pipeline = RAGPipeline()

# Folder to temporarily store uploaded PDFs
UPLOAD_DIR = Path("uploaded_pdfs")
UPLOAD_DIR.mkdir(exist_ok=True)


@app.get("/")
def root():
    return {
        "message": "InfoCite AI API is running!"
    }


@app.post("/upload")
def upload_pdfs(
    files: list[UploadFile] = File(...)
):
    """
    Upload and index up to 3 PDF documents.
    """

    if len(files) == 0:
        raise HTTPException(
            status_code=400,
            detail="Please upload at least one PDF."
        )

    if len(files) > 3:
        raise HTTPException(
            status_code=400,
            detail="Maximum of 3 PDFs allowed."
        )

    pdf_paths = []
    safe_names = set()

    # Stage and validate all inputs before replacing the active document set.
    with tempfile.TemporaryDirectory(dir=UPLOAD_DIR) as staging_dir:
        for file in files:
            original_name = Path(file.filename or "").name
            if not original_name.lower().endswith(".pdf"):
                raise HTTPException(
                    status_code=400,
                    detail=f"{original_name or 'Uploaded file'} is not a PDF.",
                )
            if not original_name:
                raise HTTPException(status_code=400, detail="A filename is required.")
            if original_name in safe_names:
                raise HTTPException(status_code=400, detail=f"Duplicate filename: {original_name}")
            safe_names.add(original_name)

            destination = Path(staging_dir) / original_name
            with destination.open("wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            if destination.stat().st_size == 0 or destination.read_bytes()[:5] != b"%PDF-":
                raise HTTPException(
                    status_code=400,
                    detail=f"{original_name} is empty or is not a valid PDF file.",
                )
            pdf_paths.append(destination)

        try:
            pipeline.index_documents(pdf_paths)
        except Exception as exc:
            raise HTTPException(
                status_code=422,
                detail=f"Unable to index documents: {exc}",
            )

        # Publish staged files only after the new index has been built.
        for pdf in UPLOAD_DIR.glob("*.pdf"):
            pdf.unlink()
        final_paths = []
        for pdf in pdf_paths:
            final_path = UPLOAD_DIR / pdf.name
            shutil.copy2(pdf, final_path)
            final_paths.append(final_path)
        pdf_paths = final_paths

    return {
        "message": f"Successfully indexed {len(pdf_paths)} PDF(s).",
        "documents": [pdf.name for pdf in pdf_paths],
        "index_stats": pipeline.index_stats,
    }


@app.post(
    "/ask",
    response_model=QuestionResponse,
)
def ask(request: QuestionRequest):

    try:
        result = pipeline.ask(request.question)

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    return QuestionResponse(
        answer=result["answer"],
        sources=result["sources"],
        evidence=result["evidence"],
        evidence_match=result["evidence_match"],
    )
