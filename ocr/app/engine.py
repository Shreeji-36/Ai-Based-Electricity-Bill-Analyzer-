import io
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image


def _preprocess(rgb: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    gray = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_CUBIC)
    gray = cv2.fastNlMeansDenoising(gray, h=15)
    return cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 31, 15)


def extract_text(data: bytes, filename: str) -> str:
    if filename.lower().endswith(".pdf"):
        pages = [np.array(p.convert("RGB"))
                 for p in convert_from_bytes(data, dpi=200, first_page=1, last_page=3)]
    else:
        pages = [np.array(Image.open(io.BytesIO(data)).convert("RGB"))]
    return "\n".join(pytesseract.image_to_string(_preprocess(p), config="--psm 6")
                     for p in pages)