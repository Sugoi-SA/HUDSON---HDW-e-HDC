import ntpath
import os
import stat
import zipfile


ARCHIVE_EXTS = {".zip", ".rar", ".7z"}


def validate_archive(path):
    MAX_ENTRIES = 100_000
    MAX_FILE_SIZE = 20 * 1024**3
    MAX_TOTAL_SIZE = 50 * 1024**3

    ext = os.path.splitext(path)[1].lower()
    entries = []

    if ext == ".zip":
        with zipfile.ZipFile(path) as archive:
            entries = [
                (
                    info.filename,
                    (info.external_attr >> 16) & 0xFFFF,
                    info.file_size,
                    False,
                )
                for info in archive.infolist()
            ]

    elif ext == ".rar":
        import rarfile
        with rarfile.RarFile(path) as archive:
            entries = [
                (
                    info.filename,
                    getattr(info, "mode", 0) or 0,
                    getattr(info, "file_size", 0) or 0,
                    bool(
                        getattr(info, "file_redir", None)
                        or getattr(info, "is_symlink", lambda: False)()
                    ),
                )
                for info in archive.infolist()
            ]

    elif ext == ".7z":
        import py7zr
        with py7zr.SevenZipFile(path, mode="r") as archive:
            entries = [
                (
                    info.filename,
                    0,
                    getattr(info, "uncompressed", 0) or 0,
                    bool(getattr(info, "is_symlink", False)),
                )
                for info in archive.list()
            ]
    else:
        return

    if len(entries) > MAX_ENTRIES:
        raise ValueError(
            f"Compactado excede o limite de {MAX_ENTRIES:,} entradas"
        )

    total_size = 0

    for name, mode, size, is_link in entries:
        normalized = name.replace("\\", "/")
        parts = normalized.split("/")
        drive, _ = ntpath.splitdrive(normalized)

        if (
            "\x00" in name
            or not normalized.strip("/")
            or normalized.startswith("/")
            or bool(drive)
            or any(part == ".." for part in parts)
            or stat.S_ISLNK(mode)
            or is_link
        ):
            raise ValueError("Caminho inseguro no compactado: " + name)

        if size < 0:
            raise ValueError("Tamanho inválido no compactado: " + name)

        if size > MAX_FILE_SIZE:
            raise ValueError(
                f"Arquivo excede o limite de 20 GiB: {name}"
            )

        total_size += size
        if total_size > MAX_TOTAL_SIZE:
            raise ValueError(
                "Compactado excede o limite total de 50 GiB descompactado"
            )

def extract_archive(path, destination):
    validate_archive(path)
    ext = os.path.splitext(path)[1].lower()

    if ext == ".zip":
        with zipfile.ZipFile(path) as archive:
            bad_file = archive.testzip()
            if bad_file is not None:
                raise zipfile.BadZipFile(
                    "CRC ou cabeçalho inválido no arquivo: " + bad_file
                )
            archive.extractall(destination)
    elif ext == ".rar":
        import rarfile
        with rarfile.RarFile(path) as archive:
            archive.testrar()
            archive.extractall(path=destination)
    elif ext == ".7z":
        import py7zr
        with py7zr.SevenZipFile(path, mode="r") as archive:
            bad_file = archive.testzip()
            if bad_file is not None:
                raise ValueError(
                    "CRC inválido no arquivo 7Z: " + str(bad_file)
                )
            archive.extractall(path=destination)

    root = os.path.realpath(destination)
    files = []

    for current, dirs, names in os.walk(root, followlinks=False):
        dirs[:] = [
            d for d in dirs
            if not os.path.islink(os.path.join(current, d))
        ]
        for name in names:
            candidate = os.path.join(current, name)
            real = os.path.realpath(candidate)
            if os.path.commonpath([root, real]) != root:
                raise ValueError("Arquivo fora do destino temporário")
            if os.path.isfile(candidate) and not os.path.islink(candidate):
                files.append(candidate)

    return sorted(files)
