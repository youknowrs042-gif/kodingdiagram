"""Theming API routes — themes, hierarchy, auto-suggestions, saturation."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from kodingdiagram.models import Theme, ThemeLevel

router = APIRouter()


class ThemeCreate(BaseModel):
    name: str
    level: ThemeLevel = ThemeLevel.INITIAL
    description: str = ""
    code_ids: list[str] = []
    parent_theme_id: Optional[str] = None


class AssignCode(BaseModel):
    code_id: str


class SetParent(BaseModel):
    parent_theme_id: Optional[str] = None


@router.post("/themes", response_model=Theme)
def create_theme(body: ThemeCreate, request: Request):
    analyzer = request.app.state.thematic_analyzer
    return analyzer.create_theme(
        body.name, body.level, body.description, body.code_ids, body.parent_theme_id
    )


@router.get("/themes", response_model=list[Theme])
def list_themes(level: Optional[ThemeLevel] = None, request: Request = None):
    analyzer = request.app.state.thematic_analyzer
    return analyzer.list_themes(level)


@router.get("/themes/{theme_id}", response_model=Theme)
def get_theme(theme_id: str, request: Request):
    theme = request.app.state.thematic_analyzer.get_theme(theme_id)
    if not theme:
        raise HTTPException(404, "Theme not found")
    return theme


@router.delete("/themes/{theme_id}")
def delete_theme(theme_id: str, request: Request):
    if not request.app.state.thematic_analyzer.delete_theme(theme_id):
        raise HTTPException(404, "Theme not found")
    return {"deleted": True}


@router.post("/themes/{theme_id}/assign-code")
def assign_code(theme_id: str, body: AssignCode, request: Request):
    if not request.app.state.thematic_analyzer.assign_code_to_theme(theme_id, body.code_id):
        raise HTTPException(400, "Could not assign code to theme")
    return {"assigned": True}


@router.post("/themes/{theme_id}/remove-code")
def remove_code(theme_id: str, body: AssignCode, request: Request):
    if not request.app.state.thematic_analyzer.remove_code_from_theme(theme_id, body.code_id):
        raise HTTPException(400, "Could not remove code from theme")
    return {"removed": True}


@router.post("/themes/{theme_id}/set-parent")
def set_parent(theme_id: str, body: SetParent, request: Request):
    if not request.app.state.thematic_analyzer.set_parent(theme_id, body.parent_theme_id):
        raise HTTPException(400, "Could not set parent (circular reference or not found)")
    return {"updated": True}


@router.get("/themes/{theme_id}/children", response_model=list[Theme])
def get_children(theme_id: str, request: Request):
    return request.app.state.thematic_analyzer.get_children(theme_id)


@router.get("/hierarchy")
def theme_hierarchy(request: Request):
    return request.app.state.thematic_analyzer.get_theme_hierarchy()


@router.get("/suggestions/co-occurrence")
def suggest_from_co_occurrence(min_co_occurrence: int = 2, request: Request = None):
    """Auto-suggest themes based on code co-occurrence patterns."""
    analyzer = request.app.state.thematic_analyzer
    return analyzer.suggest_themes_from_co_occurrence(min_co_occurrence)


@router.get("/suggestions/keywords")
def suggest_from_keywords(top_n: int = 5, request: Request = None):
    """Auto-suggest themes based on keyword overlap across coded quotations."""
    analyzer = request.app.state.thematic_analyzer
    nlp_engine = request.app.state.nlp_engine
    return analyzer.suggest_themes_from_keywords(nlp_engine, top_n)


@router.get("/saturation")
def theme_saturation(request: Request):
    """Assess theme saturation — how many quotations support each theme."""
    return request.app.state.thematic_analyzer.theme_saturation()
