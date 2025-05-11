import fitz
from PIL import Image
import os
import hashlib
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import QSize
import traceback

def get_cache_dir():
    cache_dir = os.path.join(os.path.expanduser("~"), ".pdf_viewer_cache")
    os.makedirs(cache_dir, exist_ok=True)
    return cache_dir

def get_thumbnail_path(pdf_path):
    pdf_hash = hashlib.md5(pdf_path.encode()).hexdigest()
    return os.path.join(get_cache_dir(), f"{pdf_hash}.png")

def create_default_thumbnail(size=(150, 200)):
    img = Image.new('RGB', size, color='#2d2d2d')
    default_path = os.path.join(get_cache_dir(), "default.png")
    img.save(default_path, "PNG")
    return default_path

def generate_thumbnail(pdf_path, size=(150, 200)):
    try:
        if not os.path.exists(pdf_path):
            print(f"PDF file not found: {pdf_path}")
            return create_default_thumbnail(size)

        thumbnail_path = get_thumbnail_path(pdf_path)
        
        # Return cached thumbnail if it exists
        if os.path.exists(thumbnail_path):
            return thumbnail_path

        doc = fitz.open(pdf_path)
        if doc.page_count == 0:
            print(f"PDF has no pages: {pdf_path}")
            return create_default_thumbnail(size)
        
        page = doc[0]
        zoom = 2
        mat = fitz.Matrix(zoom, zoom)
        
        # Try with different color modes if the first attempt fails
        try:
            pix = page.get_pixmap(matrix=mat, alpha=False)
        except Exception:
            try:
                # Try with grayscale
                pix = page.get_pixmap(matrix=mat, alpha=False, colorspace="gray")
            except Exception:
                # Try with minimal settings
                pix = page.get_pixmap(matrix=mat, alpha=False, colorspace="gray", annots=False)
        
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        img.thumbnail(size, Image.Resampling.LANCZOS)
        img.save(thumbnail_path, "PNG", quality=95)
        return thumbnail_path
    except Exception as e:
        print(f"Error generating thumbnail for {pdf_path}:")
        print(traceback.format_exc())
        return create_default_thumbnail(size) 