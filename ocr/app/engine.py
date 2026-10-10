"""OCR: read a bill image/PDF into text. Tries cheap options first and stops early."""
import io
import shutil
import subprocess
from typing import Iterator

import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image, ImageOps

from app.extractor import FIELDS, finalize, parse_bill, parse_fields

MAX_SIDE = 2400   # downscale huge phone photos (keeps memory and time low)
MIN_SIDE = 1500   # upscale tiny images so small text is readable


def _pdf_text_layer(data: bytes) -> str:
    """Digital PDFs already contain text: read it directly (fast and exact)."""
    if not shutil.which("pdftotext"):
        return ""
    try:
        p = subprocess.run(["pdftotext", "-layout", "-l", "3", "-", "-"], input=data,
                           capture_output=True, timeout=20)
        return p.stdout.decode("utf-8", "ignore")
    except Exception:
        return ""


def _load_pages(data: bytes, filename: str) -> list[np.ndarray]:
    if filename.lower().endswith(".pdf"):
        return [np.array(p.convert("RGB"))
                for p in convert_from_bytes(data, dpi=170, first_page=1, last_page=2)]
    img = ImageOps.exif_transpose(Image.open(io.BytesIO(data))).convert("RGB")  # phone rotation
    return [np.array(img)]


def _resize(gray: np.ndarray) -> np.ndarray:
    h, w = gray.shape
    side = max(h, w)
    if side > MAX_SIDE:
        f = MAX_SIDE / side
        return cv2.resize(gray, None, fx=f, fy=f, interpolation=cv2.INTER_AREA)
    if side < MIN_SIDE:
        f = MIN_SIDE / side
        return cv2.resize(gray, None, fx=f, fy=f, interpolation=cv2.INTER_CUBIC)
    return gray


def _deskew(gray: np.ndarray) -> np.ndarray:
    """Straighten slightly tilted photos (up to about 10 degrees)."""
    inv = cv2.threshold(cv2.GaussianBlur(gray, (5, 5), 0), 0, 255,
                        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    pts = cv2.findNonZero(inv)
    if pts is None or len(pts) < 500:
        return gray
    angle = cv2.minAreaRect(pts)[-1]
    angle = angle - 90 if angle > 45 else angle
    angle = angle + 90 if angle < -45 else angle
    if abs(angle) < 0.4 or abs(angle) > 10:
        return gray
    h, w = gray.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), angle, 1.0)
    return cv2.warpAffine(gray, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)


def _variants(rgb: np.ndarray) -> list[tuple[str, np.ndarray]]:
    gray = _resize(cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY))
    gray = _deskew(gray)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(gray)   # fixes uneven light
    thr = cv2.adaptiveThreshold(cv2.medianBlur(clahe, 3), 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                cv2.THRESH_BINARY, 41, 12)
    return [("clahe", clahe), ("threshold", thr), ("plain", gray)]


def _ocr(img: np.ndarray, psm: int) -> str:
    return pytesseract.image_to_string(img, config=f"--oem 3 --psm {psm}", timeout=45)


def text_candidates(data: bytes, filename: str) -> Iterator[str]:
    """Yields progressively more expensive text readings of the file."""
    if filename.lower().endswith(".pdf"):
        t = _pdf_text_layer(data)
        if len(t.strip()) > 80:
            yield t
    pages = _load_pages(data, filename)
    prepared = [_variants(p) for p in pages]
    # (preprocessing variant, tesseract page-segmentation mode)
    for v, psm in ((0, 6), (1, 6), (2, 6), (0, 4)):
        yield "\n".join(_ocr(pv[v][1], psm) for pv in prepared)


def best_parse(data: bytes, filename: str) -> dict:
    """Read the file several ways and merge what each reading found.

    A line missed in one reading is often found in another, so fields that are
    still empty are filled from later readings. Stops as soon as the result is good.
    """
    merged: dict = {k: None for k in FIELDS}
    out = finalize(dict(merged))
    for text in text_candidates(data, filename):
        found = parse_fields(text)
        for k in FIELDS:
            if merged[k] is None and found[k] is not None:
                merged[k] = found[k]
        out = finalize(dict(merged))
        if out["units"] and out["amount"] and out["days"]:
            break
    return out