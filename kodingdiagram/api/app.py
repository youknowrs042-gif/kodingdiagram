"""FastAPI application factory and shared state."""

from __future__ import annotations

from fastapi import FastAPI

from kodingdiagram.coding.manager import CodingManager
from kodingdiagram.nlp.engine import NLPEngine
from kodingdiagram.theming.analyzer import ThematicAnalyzer
from kodingdiagram.visualization.network import NetworkBuilder


def create_app() -> FastAPI:
    app = FastAPI(
        title="KodingDiagram",
        description="Qualitative Data Analysis API — NLP, Coding, Theming, Network Visualization",
        version="0.1.0",
    )

    # Shared state (in-memory for now; swap for DB later)
    app.state.nlp_engine = NLPEngine()
    app.state.coding_manager = CodingManager()
    app.state.thematic_analyzer = ThematicAnalyzer(app.state.coding_manager)
    app.state.network_builder = NetworkBuilder(
        app.state.coding_manager, app.state.thematic_analyzer
    )

    # Register routers
    from kodingdiagram.api.routes_coding import router as coding_router
    from kodingdiagram.api.routes_nlp import router as nlp_router
    from kodingdiagram.api.routes_theming import router as theming_router
    from kodingdiagram.api.routes_visualization import router as viz_router

    app.include_router(nlp_router, prefix="/api/nlp", tags=["NLP"])
    app.include_router(coding_router, prefix="/api/coding", tags=["Coding"])
    app.include_router(theming_router, prefix="/api/theming", tags=["Theming"])
    app.include_router(viz_router, prefix="/api/visualization", tags=["Visualization"])

    @app.get("/", tags=["Health"])
    def root():
        return {
            "service": "KodingDiagram",
            "version": "0.1.0",
            "docs": "/docs",
            "endpoints": ["/api/nlp", "/api/coding", "/api/theming", "/api/visualization"],
        }

    return app
