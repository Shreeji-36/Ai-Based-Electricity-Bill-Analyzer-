from fastapi import FastAPI, File, HTTPException, UploadFile
from app.engine import extract_text
from app.extractor import parse_bill

ALLOWED = (".jpg", ".jpeg", ".png", ".pdf")
MAX_BYTES = 8 * 1024 * 1024

app = FastAPI(title="OCR Service")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/extract")
async def extract(file: UploadFile = File(...)):
    name = (file.filename or "").lower()
    if not name.endswith(ALLOWED):
        raise HTTPException(415, "Only JPG, JPEG, PNG or PDF files are supported")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "File too large (max 8 MB)")
    try:
        text = extract_text(data, name)
    except Exception:
        raise HTTPException(422, "Could not read this file")
    return parse_bill(text)