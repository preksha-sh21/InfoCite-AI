from pathlib import Path
import shutil

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

    # Remove previously uploaded PDFs
    for pdf in UPLOAD_DIR.glob("*.pdf"):
        pdf.unlink()

    # Save uploaded PDFs
    for file in files:

        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(
                status_code=400,
                detail=f"{file.filename} is not a PDF."
            )

        destination = UPLOAD_DIR / file.filename

        with destination.open("wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        pdf_paths.append(destination)

    # Index uploaded PDFs
    pipeline.index_documents(pdf_paths)

    return {
        "message": f"Successfully indexed {len(pdf_paths)} PDF(s).",
        "documents": [pdf.name for pdf in pdf_paths],
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
        confidence=result["confidence"],
    )