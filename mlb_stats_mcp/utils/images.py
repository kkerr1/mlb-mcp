"""
Image support for tests
"""

import base64
import io

from PIL import Image

from .logging_config import setup_logging

logger = setup_logging("images")


def display_base64_image(base64_string: str):
    """Display a base64 encoded image using PIL."""
    if base64_string.startswith("data:image"):
        base64_data = base64_string.split(",")[1]
    else:
        base64_data = base64_string

    try:
        image_bytes = base64.b64decode(base64_data)
        image = Image.open(io.BytesIO(image_bytes))
        image.show()
    except Exception as e:
        logger.error(f"Exception occured while displaying image: {e}")
