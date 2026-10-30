import os
from typing import Dict, Optional

IGNORED_EXTENSIONS = {
    ".p7s",
    ".lnk",
    ".2023",
    ".exe",
    ".ini",
    ".mht",
    ".msi",
    ".p7b",
    ".pfx",
}

EXTENSION_MAP: Dict[str, str] = {
    ".pdf": "document_text",
    ".doc": "document_text",
    ".docx": "document_text",
    ".one": "document_text",
    ".odt": "document_text",
    ".rtf": "document_text",
    ".md": "document_text",
    ".fdf": "document_text",
    ".log": "document_text",
    ".txt": "document_text",
    ".eml": "communication",
    ".msg": "communication",
    ".pst": "communication",
    ".aspx": "communication",
    ".html": "communication",
    ".dwg": "engineering_drawings",
    ".dxf": "engineering_drawings",
    ".rvt": "engineering_drawings",
    ".ifc": "engineering_drawings",
    ".xls": "structured_data",
    ".xlsx": "structured_data",
    ".xlsm": "structured_data",
    ".xlsb": "structured_data",
    ".odc": "structured_data",
    ".vsdx": "structured_data",
    ".csv": "structured_data",
    ".xml": "structured_data",
    ".json": "structured_data",
    ".loop": "structured_data",
    ".whiteboard": "structured_data",
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
    ".pptx": "image",
    ".ico": "image",
    ".tif": "image",
    ".tiff": "image",
    ".bmp": "image",
    ".gif": "image",
    ".mp3": "audio_video",
    ".wav": "audio_video",
    ".mp4": "audio_video",
    ".avi": "audio_video",
    ".mov": "audio_video",
    ".mkv": "audio_video",
}


def get_extension(filename: str) -> str:
    """Retorna a extensao em minusculas, inclusive para o nome isolado '.msg'."""
    if os.path.basename(filename).lower() == ".msg":
        return ".msg"
    return os.path.splitext(filename)[1].lower()


def is_ignored(filename: str) -> bool:
    return get_extension(filename) in IGNORED_EXTENSIONS


def route(filename: str) -> Optional[str]:
    ext = get_extension(filename)
    if ext in IGNORED_EXTENSIONS:
        return None
    return EXTENSION_MAP.get(ext)
