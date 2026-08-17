from pathlib import Path

from app.parser.models import (
    ParsedProject,
    ParsedFile,
    FunctionSymbol,
)

from app.knowledge.parser_mapper import (
    ParserKnowledgeMapper,
)


def test_parser_symbols_are_persisted():

    parsed = ParsedProject(
        files=[
            ParsedFile(
                path=Path("main.py"),
                language="python",
                functions=[
                    FunctionSymbol(
                        name="hello",
                        start_line=1,
                        end_line=2,
                    )
                ],
            )
        ]
    )

    symbols = ParserKnowledgeMapper.from_parser(
        parsed
    )

    assert len(symbols) == 1
    assert symbols[0].name == "hello"
    assert symbols[0].symbol_type == "function"


def test_parser_symbol_identity_is_stable():

    parsed = ParsedProject(
        files=[
            ParsedFile(
                path=Path("main.py"),
                language="python",
                functions=[
                    FunctionSymbol(
                        name="hello",
                        start_line=1,
                        end_line=2,
                    )
                ],
            )
        ]
    )

    first = ParserKnowledgeMapper.from_parser(
        parsed
    )

    second = ParserKnowledgeMapper.from_parser(
        parsed
    )

    assert first[0].symbol_id == second[0].symbol_id


def test_empty_parser_result_creates_empty_symbols():

    symbols = ParserKnowledgeMapper.from_parser(
        None
    )

    assert symbols == []
