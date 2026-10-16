import os
from typing import Dict, Optional

EXTENSION_MAP: Dict[str, str] = {
    ".pdf": "document_text",
    ".doc": "document_text",
    ".docx": "document_text",
    ".one": "document_text",
    ".odt": "document_text",
    ".rtf": "document_text",
    ".zip": "document_text",
    ".rar": "document_text",
    ".7z": "document_text",
    ".txt": "document_text",
    ".eml": "communication",
    ".msg": "communication",
    ".pst": "communication",
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
    ".jpg": "image",
    ".jpeg": "image",
    ".png": "image",
    ".pptx": "image",
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


def route(filename: str) -> Optional[str]:
    ext = os.path.splitext(filename)[1].lower()
    return EXTENSION_MAP.get(ext)
