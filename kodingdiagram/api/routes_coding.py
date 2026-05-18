"""Coding API routes — documents, codes, quotations, memos, groups."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from kodingdiagram.models import Code, CodeGroup, Document, Memo, Quotation

router = APIRouter()


# --- Request schemas ---

class DocumentCreate(BaseModel):
    name: str
    content: str


class CodeCreate(BaseModel):
    name: str
    color: str = "#3b82f6"
    description: str = ""
    group: Optional[str] = None


class QuotationCreate(BaseModel):
    document_id: str
    text: str
    start_char: int
    end_char: int
    code_ids: list[str] = []
    comment: str = ""


class MemoCreate(BaseModel):
    title: str
    content: str
    linked_codes: list[str] = []
    linked_quotations: list[str] = []


class CodeGroupCreate(BaseModel):
    name: str
    code_ids: list[str] = []


class AssignCode(BaseModel):
    code_id: str


# --- Documents ---

@router.post("/documents", response_model=Document)
def create_document(body: DocumentCreate, request: Request):
    mgr = request.app.state.coding_manager
    return mgr.add_document(body.name, body.content)


@router.get("/documents", response_model=list[Document])
def list_documents(request: Request):
    return request.app.state.coding_manager.list_documents()


@router.get("/documents/{doc_id}", response_model=Document)
def get_document(doc_id: str, request: Request):
    doc = request.app.state.coding_manager.get_document(doc_id)
    if not doc:
        raise HTTPException(404, "Document not found")
    return doc


# --- Codes ---

@router.post("/codes", response_model=Code)
def create_code(body: CodeCreate, request: Request):
    mgr = request.app.state.coding_manager
    return mgr.create_code(body.name, body.color, body.description, body.group)


@router.get("/codes", response_model=list[Code])
def list_codes(request: Request):
    return request.app.state.coding_manager.list_codes()


@router.delete("/codes/{code_id}")
def delete_code(code_id: str, request: Request):
    if not request.app.state.coding_manager.delete_code(code_id):
        raise HTTPException(404, "Code not found")
    return {"deleted": True}


# --- Quotations ---

@router.post("/quotations", response_model=Quotation)
def create_quotation(body: QuotationCreate, request: Request):
    mgr = request.app.state.coding_manager
    return mgr.create_quotation(
        body.document_id, body.text, body.start_char, body.end_char, body.code_ids, body.comment
    )


@router.get("/quotations", response_model=list[Quotation])
def list_quotations(request: Request):
    return request.app.state.coding_manager.list_quotations()


@router.get("/quotations/by-code/{code_id}", response_model=list[Quotation])
def quotations_by_code(code_id: str, request: Request):
    return request.app.state.coding_manager.get_quotations_by_code(code_id)


@router.get("/quotations/by-document/{doc_id}", response_model=list[Quotation])
def quotations_by_document(doc_id: str, request: Request):
    return request.app.state.coding_manager.get_quotations_by_document(doc_id)


@router.post("/quotations/{quotation_id}/assign-code")
def assign_code(quotation_id: str, body: AssignCode, request: Request):
    mgr = request.app.state.coding_manager
    if not mgr.assign_code_to_quotation(quotation_id, body.code_id):
        raise HTTPException(400, "Could not assign code")
    return {"assigned": True}


@router.post("/quotations/{quotation_id}/remove-code")
def remove_code(quotation_id: str, body: AssignCode, request: Request):
    mgr = request.app.state.coding_manager
    if not mgr.remove_code_from_quotation(quotation_id, body.code_id):
        raise HTTPException(400, "Could not remove code")
    return {"removed": True}


# --- Memos ---

@router.post("/memos", response_model=Memo)
def create_memo(body: MemoCreate, request: Request):
    mgr = request.app.state.coding_manager
    return mgr.create_memo(body.title, body.content, body.linked_codes, body.linked_quotations)


@router.get("/memos", response_model=list[Memo])
def list_memos(request: Request):
    return request.app.state.coding_manager.list_memos()


# --- Code Groups ---

@router.post("/groups", response_model=CodeGroup)
def create_group(body: CodeGroupCreate, request: Request):
    mgr = request.app.state.coding_manager
    return mgr.create_code_group(body.name, body.code_ids)


@router.get("/groups", response_model=list[CodeGroup])
def list_groups(request: Request):
    return request.app.state.coding_manager.list_code_groups()


@router.post("/groups/{group_id}/add-code")
def add_code_to_group(group_id: str, body: AssignCode, request: Request):
    mgr = request.app.state.coding_manager
    if not mgr.add_code_to_group(group_id, body.code_id):
        raise HTTPException(400, "Could not add code to group")
    return {"added": True}


# --- Analytics ---

@router.get("/analytics/code-frequency")
def code_frequency(request: Request):
    mgr = request.app.state.coding_manager
    freq = mgr.code_frequency()
    # Map IDs to names for readability
    return {
        mgr.codes[cid].name if cid in mgr.codes else cid: count
        for cid, count in freq.items()
    }


@router.get("/analytics/co-occurrence")
def co_occurrence(request: Request):
    mgr = request.app.state.coding_manager
    co = mgr.code_co_occurrence()
    results = []
    for (c1, c2), count in co.items():
        name1 = mgr.codes[c1].name if c1 in mgr.codes else c1
        name2 = mgr.codes[c2].name if c2 in mgr.codes else c2
        results.append({"code_a": name1, "code_b": name2, "count": count})
    return results
