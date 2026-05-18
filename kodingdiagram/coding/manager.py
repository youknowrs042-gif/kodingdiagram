"""Coding Manager - qualitative data coding operations.

Supports creating codes, assigning quotations, managing memos and code groups.
Inspired by ATLAS.ti's coding workflow.
"""

from __future__ import annotations

from typing import Optional

from kodingdiagram.models import Code, CodeGroup, Document, Memo, Quotation


class CodingManager:
    """Manages qualitative coding: codes, quotations, memos, groups."""

    def __init__(self) -> None:
        self.documents: dict[str, Document] = {}
        self.codes: dict[str, Code] = {}
        self.quotations: dict[str, Quotation] = {}
        self.memos: dict[str, Memo] = {}
        self.code_groups: dict[str, CodeGroup] = {}

    # --- Documents ---

    def add_document(self, name: str, content: str) -> Document:
        doc = Document(name=name, content=content)
        self.documents[doc.id] = doc
        return doc

    def get_document(self, doc_id: str) -> Optional[Document]:
        return self.documents.get(doc_id)

    def list_documents(self) -> list[Document]:
        return list(self.documents.values())

    # --- Codes ---

    def create_code(
        self,
        name: str,
        color: str = "#3b82f6",
        description: str = "",
        group: Optional[str] = None,
    ) -> Code:
        code = Code(name=name, color=color, description=description, group=group)
        self.codes[code.id] = code
        return code

    def get_code(self, code_id: str) -> Optional[Code]:
        return self.codes.get(code_id)

    def list_codes(self) -> list[Code]:
        return list(self.codes.values())

    def delete_code(self, code_id: str) -> bool:
        if code_id in self.codes:
            del self.codes[code_id]
            # Remove from quotations
            for q in self.quotations.values():
                if code_id in q.code_ids:
                    q.code_ids.remove(code_id)
            # Remove from groups
            for g in self.code_groups.values():
                if code_id in g.code_ids:
                    g.code_ids.remove(code_id)
            return True
        return False

    # --- Quotations ---

    def create_quotation(
        self,
        document_id: str,
        text: str,
        start_char: int,
        end_char: int,
        code_ids: Optional[list[str]] = None,
        comment: str = "",
    ) -> Quotation:
        quotation = Quotation(
            document_id=document_id,
            text=text,
            start_char=start_char,
            end_char=end_char,
            code_ids=code_ids or [],
            comment=comment,
        )
        self.quotations[quotation.id] = quotation
        return quotation

    def assign_code_to_quotation(self, quotation_id: str, code_id: str) -> bool:
        q = self.quotations.get(quotation_id)
        if q and code_id in self.codes and code_id not in q.code_ids:
            q.code_ids.append(code_id)
            return True
        return False

    def remove_code_from_quotation(self, quotation_id: str, code_id: str) -> bool:
        q = self.quotations.get(quotation_id)
        if q and code_id in q.code_ids:
            q.code_ids.remove(code_id)
            return True
        return False

    def get_quotations_by_code(self, code_id: str) -> list[Quotation]:
        return [q for q in self.quotations.values() if code_id in q.code_ids]

    def get_quotations_by_document(self, document_id: str) -> list[Quotation]:
        return [q for q in self.quotations.values() if q.document_id == document_id]

    def list_quotations(self) -> list[Quotation]:
        return list(self.quotations.values())

    # --- Memos ---

    def create_memo(
        self,
        title: str,
        content: str,
        linked_codes: Optional[list[str]] = None,
        linked_quotations: Optional[list[str]] = None,
    ) -> Memo:
        memo = Memo(
            title=title,
            content=content,
            linked_codes=linked_codes or [],
            linked_quotations=linked_quotations or [],
        )
        self.memos[memo.id] = memo
        return memo

    def list_memos(self) -> list[Memo]:
        return list(self.memos.values())

    # --- Code Groups ---

    def create_code_group(self, name: str, code_ids: Optional[list[str]] = None) -> CodeGroup:
        group = CodeGroup(name=name, code_ids=code_ids or [])
        self.code_groups[group.id] = group
        return group

    def add_code_to_group(self, group_id: str, code_id: str) -> bool:
        group = self.code_groups.get(group_id)
        if group and code_id in self.codes and code_id not in group.code_ids:
            group.code_ids.append(code_id)
            return True
        return False

    def list_code_groups(self) -> list[CodeGroup]:
        return list(self.code_groups.values())

    # --- Analytics ---

    def code_frequency(self) -> dict[str, int]:
        """Count how many quotations each code is applied to."""
        freq: dict[str, int] = {}
        for code_id in self.codes:
            freq[code_id] = len(self.get_quotations_by_code(code_id))
        return freq

    def code_co_occurrence(self) -> dict[tuple[str, str], int]:
        """Count how often pairs of codes co-occur on the same quotation."""
        co: dict[tuple[str, str], int] = {}
        for q in self.quotations.values():
            codes = sorted(q.code_ids)
            for i, c1 in enumerate(codes):
                for c2 in codes[i + 1 :]:
                    pair = (c1, c2)
                    co[pair] = co.get(pair, 0) + 1
        return co
