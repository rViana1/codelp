import hashlib

from app.knowledge.parser_mapper import ParserKnowledgeMapper
from app.knowledge.hash import FileContentHasher


def test_file_hash_is_deterministic(tmp_path):

    file = tmp_path / "main.py"

    file.write_text(
        "def hello():\n"
        "    return 42\n"
    )

    first = FileContentHasher.hash_file(
        file
    )

    second = FileContentHasher.hash_file(
        file
    )

    assert first == second



def test_symbol_identity_is_deterministic():

    first = (
        ParserKnowledgeMapper._create_symbol_id(
            "src/main.py",
            "hello",
            "function",
        )
    )

    second = (
        ParserKnowledgeMapper._create_symbol_id(
            "src/main.py",
            "hello",
            "function",
        )
    )

    assert first == second



def test_different_symbols_have_different_identity():

    function_id = (
        ParserKnowledgeMapper._create_symbol_id(
            "src/main.py",
            "hello",
            "function",
        )
    )

    other_id = (
        ParserKnowledgeMapper._create_symbol_id(
            "src/main.py",
            "goodbye",
            "function",
        )
    )

    assert function_id != other_id