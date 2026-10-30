from app.services.estante_router import get_extension, is_ignored, route


def test_route_maps_known_extensions():
    assert route("contrato.pdf") == "document_text"
    assert route("foto.jpg") == "image"
    assert route("planilha.xlsx") == "structured_data"
    assert route("desenho.dwg") == "engineering_drawings"
    assert route("gravacao.mp3") == "audio_video"
    assert route("email.eml") == "communication"


def test_route_unknown_extension_returns_none():
    assert route("arquivo.extensao_inexistente") is None


def test_route_is_case_insensitive():
    assert route("CONTRATO.PDF") == "document_text"


def test_msg_dotfile_is_routed_as_communication():
    assert get_extension(".msg") == ".msg"
    assert route(".msg") == "communication"


def test_msg_extension_is_case_insensitive():
    assert get_extension(".MSG") == ".msg"
    assert route(".MSG") == "communication"


def test_ignored_extensions_are_not_routed():
    filenames = (
        "assinatura.p7s",
        "atalho.lnk",
        "arquivo.2023",
        "programa.exe",
        "configuracao.ini",
        "pagina.mht",
        "instalador.msi",
        "certificado.p7b",
        "certificado.pfx",
    )
    for filename in filenames:
        assert is_ignored(filename)
        assert route(filename) is None


def test_new_extension_mappings_and_archives():
    expected = {
        "arquivo.md": "document_text",
        "arquivo.fdf": "document_text",
        "arquivo.log": "document_text",
        "pagina.aspx": "communication",
        "pagina.html": "communication",
        "quadro.loop": "structured_data",
        "quadro.whiteboard": "structured_data",
        "icone.ico": "image",
    }
    for filename, category in expected.items():
        assert route(filename) == category

    for filename in ("arquivo.zip", "arquivo.rar", "arquivo.7z"):
        assert route(filename) is None
