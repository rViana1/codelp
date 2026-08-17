from __future__ import annotations

import hashlib

from app.parser.models import ParsedProject
from app.knowledge.models import PersistentSymbolIdentity


class ParserKnowledgeMapper:
    """
    Converts parser output into persistent knowledge.

    Responsibilities
    ----------------
    - Extract symbols from parser results.
    - Generate stable symbol identities.
    - Does not modify parser output.
    - Does not persist data.
    """

    @staticmethod
    def from_parser(
        parsed_project: ParsedProject | None,
    ) -> list[PersistentSymbolIdentity]:
        """
        Creates persistent symbol identities from parser knowledge.
        """

        if parsed_project is None:
            return []

        symbols = []

        for parsed_file in parsed_project.files:

            file_id = str(parsed_file.path)

            for function in parsed_file.functions:

                symbols.append(
                    PersistentSymbolIdentity(
                        symbol_id=ParserKnowledgeMapper._create_symbol_id(
                            file_id,
                            function.name,
                            "function",
                        ),
                        file_id=file_id,
                        name=function.name,
                        symbol_type="function",
                    )
                )

            for cls in parsed_file.classes:

                symbols.append(
                    PersistentSymbolIdentity(
                        symbol_id=ParserKnowledgeMapper._create_symbol_id(
                            file_id,
                            cls.name,
                            "class",
                        ),
                        file_id=file_id,
                        name=cls.name,
                        symbol_type="class",
                    )
                )

                for method in cls.methods:

                    symbols.append(
                        PersistentSymbolIdentity(
                            symbol_id=ParserKnowledgeMapper._create_symbol_id(
                                file_id,
                                f"{cls.name}.{method.name}",
                                "method",
                            ),
                            file_id=file_id,
                            name=method.name,
                            symbol_type="method",
                        )
                    )

        return symbols


    @staticmethod
    def _create_symbol_id(
        file_id: str,
        name: str,
        symbol_type: str,
    ) -> str:
        """
        Creates deterministic symbol identity.
        """

        value = (
            f"{file_id}:{name}:{symbol_type}"
        )

        return hashlib.sha256(
            value.encode("utf-8")
        ).hexdigest()
