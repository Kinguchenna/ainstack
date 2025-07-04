# utils.py
from pdf2image import convert_from_path
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
def pdf_to_images(pdf_path):
    return convert_from_path(pdf_path)


def extract_text_from_image(image: Image.Image) -> str:
    return pytesseract.image_to_string(image)
