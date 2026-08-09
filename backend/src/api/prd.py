import os
import tempfile
from pathlib import Path

import httpx
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from src.engines.prd_parser import PRDParser

router = APIRouter()


class GoogleDocRequest(BaseModel):
    doc_url: str


class PRDUploadResponse(BaseModel):
    filename: str
    content: str
    requirements: list[dict]


@router.post("/upload", response_model=PRDUploadResponse)
async def upload_prd_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    suffix = Path(file.filename).suffix.lower()
    if suffix not in (".md", ".txt", ".pdf"):
        raise HTTPException(status_code=400, detail="Only .md, .txt, and .pdf files are supported")

    content_bytes = await file.read()
    content = ""

    if suffix == ".pdf":
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(content_bytes)
            tmp_path = tmp.name
        try:
            parser = PRDParser()
            requirements = parser.parse_file(tmp_path)
            from PyPDF2 import PdfReader
            reader = PdfReader(tmp_path)
            content = "\n".join(page.extract_text() or "" for page in reader.pages)
        finally:
            os.unlink(tmp_path)
    else:
        content = content_bytes.decode("utf-8")
        parser = PRDParser()
        requirements = parser.parse_text(content, file.filename)

    return PRDUploadResponse(
        filename=file.filename,
        content=content,
        requirements=requirements,
    )


@router.post("/google-doc")
async def ingest_google_doc(req: GoogleDocRequest):
    doc_url = req.doc_url.strip()

    export_url = ""
    if "/document/d/" in doc_url:
        doc_id = doc_url.split("/document/d/")[1].split("/")[0].split("?")[0]
        export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    elif "/document/" in doc_url and "/edit" in doc_url:
        doc_id = doc_url.split("/document/")[1].split("/")[0]
        export_url = f"https://docs.google.com/document/d/{doc_id}/export?format=txt"
    else:
        raise HTTPException(status_code=400, detail="Invalid Google Doc URL. Expected format: https://docs.google.com/document/d/DOC_ID/...")

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            resp = await client.get(export_url, timeout=30.0)
            if resp.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to fetch Google Doc: HTTP {resp.status_code}",
                )
            content = resp.text
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="Timed out fetching Google Doc")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch Google Doc: {str(e)}")

    if not content.strip():
        raise HTTPException(
            status_code=400,
            detail="Google Doc is empty or not publicly accessible",
        )

    parser = PRDParser()
    requirements = parser.parse_text(content, f"google-doc-{doc_id}")

    return {
        "doc_id": doc_id,
        "content": content,
        "requirements": requirements,
    }
