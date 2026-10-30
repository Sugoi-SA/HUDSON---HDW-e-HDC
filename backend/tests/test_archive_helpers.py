import os
import zipfile

import pytest

from app.services.archive_helpers import extract_archive


def test_extract_valid_zip_and_preserve_contents(tmp_path):
    archive_path = tmp_path / "documentos.zip"
    destination = tmp_path / "extraido"

    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("docs/contrato.txt", "conteudo do contrato")
        archive.writestr("foto.txt", "conteudo da foto")

    destination.mkdir()
    extracted = extract_archive(str(archive_path), str(destination))

    relative_paths = sorted(
        os.path.relpath(path, destination).replace(os.sep, "/")
        for path in extracted
    )

    assert relative_paths == ["docs/contrato.txt", "foto.txt"]
    assert (destination / "docs/contrato.txt").read_text(
        encoding="utf-8"
    ) == "conteudo do contrato"
    assert (destination / "foto.txt").read_text(
        encoding="utf-8"
    ) == "conteudo da foto"


def test_reject_zip_with_parent_traversal(tmp_path):
    archive_path = tmp_path / "inseguro.zip"
    destination = tmp_path / "extraido"

    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("../fora.txt", "nao deve ser extraido")

    destination.mkdir()

    with pytest.raises(ValueError, match="Caminho inseguro"):
        extract_archive(str(archive_path), str(destination))

    assert not (tmp_path / "fora.txt").exists()


def test_extraction_returns_only_files_inside_destination(tmp_path):
    archive_path = tmp_path / "arquivos.zip"
    destination = tmp_path / "destino"

    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("sub/presente.txt", "conteudo")

    destination.mkdir()
    extracted = extract_archive(str(archive_path), str(destination))
    root = os.path.realpath(destination)

    assert extracted
    for path in extracted:
        real_path = os.path.realpath(path)
        assert os.path.commonpath([root, real_path]) == root
        assert os.path.isfile(real_path)


def test_reject_invalid_zip(tmp_path):
    archive_path = tmp_path / "invalido.zip"
    destination = tmp_path / "destino"
    archive_path.write_text("isto nao e um ZIP", encoding="utf-8")
    destination.mkdir()

    with pytest.raises(zipfile.BadZipFile):
        extract_archive(str(archive_path), str(destination))


def test_reject_zip_with_symlink_entry(tmp_path):
    import stat

    archive_path = tmp_path / "symlink.zip"
    destination = tmp_path / "extraido"

    info = zipfile.ZipInfo("link.txt")
    info.create_system = 3
    info.external_attr = (stat.S_IFLNK | 0o777) << 16

    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(info, "../fora.txt")

    destination.mkdir()

    with pytest.raises(ValueError, match="Caminho inseguro"):
        extract_archive(str(archive_path), str(destination))

    assert not (tmp_path / "fora.txt").exists()


@pytest.mark.parametrize(
    "member_name",
    [
        "/tmp/fora.txt",
        r"C:\Windows\Temp\fora.txt",
        r"\\servidor\compartilhamento\fora.txt",
    ],
)
def test_reject_zip_with_absolute_or_windows_path(tmp_path, member_name):
    archive_path = tmp_path / "caminho_inseguro.zip"
    destination = tmp_path / "extraido"

    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr(member_name, "nao deve ser extraido")

    destination.mkdir()

    with pytest.raises(ValueError, match="Caminho inseguro"):
        extract_archive(str(archive_path), str(destination))

    assert list(destination.iterdir()) == []


def test_reject_corrupt_zip_before_extracting_any_file(tmp_path):
    archive_path = tmp_path / "crc_invalido.zip"
    destination = tmp_path / "extraido"

    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("primeiro.txt", "conteudo original")
        archive.writestr("segundo.txt", "outro conteudo")

    data = bytearray(archive_path.read_bytes())
    offset = data.find(b"conteudo original")
    assert offset >= 0
    data[offset] ^= 1
    archive_path.write_bytes(data)

    destination.mkdir()

    with pytest.raises(zipfile.BadZipFile):
        extract_archive(str(archive_path), str(destination))

    assert list(destination.iterdir()) == []
