import os
import logging
from config.settings import SCREENSHOT_FOLDER


def save_image(image, filename):
    filepath = os.path.join(SCREENSHOT_FOLDER, filename)
    image.save(filepath)
    logging.debug(f"Processed image saved to {filepath}")
    return filepath
