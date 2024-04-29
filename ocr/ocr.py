import pytesseract
from PIL import Image
import pyautogui


def capture_and_process_image(region, enhance_factor=2):
    img = pyautogui.screenshot(region=region)
    img = img.resize(
        (img.width * enhance_factor, img.height * enhance_factor), Image.BICUBIC
    )
    gray_img = img.convert("L")
    return gray_img


def perform_ocr(image):
    text = pytesseract.image_to_string(image)
    return text.strip()
