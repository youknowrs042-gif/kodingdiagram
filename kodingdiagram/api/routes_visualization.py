"""Visualization API routes — network graph generation and export."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Request
from fastapi.responses import Response

router = APIRouter()


@router.get("/code-quotation")
def code_quotation_network(document_id: Optional[str] = None, request: Request = None):
    """Get code-quotation bipartite network as JSON."""
    builder = request.app.state.network_builder
    graph = builder.code_quotation_network(document_id)
    return {"nodes": [n.model_dump() for n in graph.nodes], "edges": [e.model_dump() for e in graph.edges]}


@router.get("/co-occurrence")
def co_occurrence_network(min_weight: int = 1, request: Request = None):
    """Get code co-occurrence network as JSON."""
    builder = request.app.state.network_builder
    graph = builder.code_co_occurrence_network(min_weight)
    return {"nodes": [n.model_dump() for n in graph.nodes], "edges": [e.model_dump() for e in graph.edges]}


@router.get("/theme-hierarchy")
def theme_hierarchy_network(request: Request):
    """Get theme hierarchy network as JSON."""
    builder = request.app.state.network_builder
    graph = builder.theme_hierarchy_network()
    return {"nodes": [n.model_dump() for n in graph.nodes], "edges": [e.model_dump() for e in graph.edges]}


@router.get("/full-project")
def full_project_network(request: Request):
    """Get full project network (all entities and relations) as JSON."""
    builder = request.app.state.network_builder
    graph = builder.full_project_network()
    return {"nodes": [n.model_dump() for n in graph.nodes], "edges": [e.model_dump() for e in graph.edges]}


@router.get("/export/gexf")
def export_gexf(network_type: str = "full-project", request: Request = None):
    """Export network as GEXF (Gephi compatible).

    network_type: full-project | co-occurrence | theme-hierarchy | code-quotation
    """
    builder = request.app.state.network_builder
    graph = _get_graph(builder, network_type)
    gexf_str = builder.to_gexf(graph)
    return Response(content=gexf_str, media_type="application/xml", headers={
        "Content-Disposition": f"attachment; filename=kodingdiagram_{network_type}.gexf"
    })


@router.get("/export/png")
def export_png(network_type: str = "full-project", request: Request = None):
    """Export network as PNG image.

    network_type: full-project | co-occurrence | theme-hierarchy | code-quotation
    """
    builder = request.app.state.network_builder
    graph = _get_graph(builder, network_type)
    png_bytes = builder.to_png_bytes(graph)
    return Response(content=png_bytes, media_type="image/png", headers={
        "Content-Disposition": f"attachment; filename=kodingdiagram_{network_type}.png"
    })


def _get_graph(builder, network_type: str):
    """Helper to select graph by type name."""
    if network_type == "co-occurrence":
        return builder.code_co_occurrence_network()
    elif network_type == "theme-hierarchy":
        return builder.theme_hierarchy_network()
    elif network_type == "code-quotation":
        return builder.code_quotation_network()
    else:
        return builder.full_project_network()
