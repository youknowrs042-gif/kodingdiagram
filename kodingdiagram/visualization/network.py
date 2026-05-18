"""Network Builder - generates relationship diagrams for qualitative data.

Creates network graphs showing connections between:
- Codes and quotations
- Codes and themes
- Code co-occurrence
- Documents and codes
- Full project networks

Exports to JSON (for D3/vis.js), GEXF, and PNG.
"""

from __future__ import annotations

import io
import json
from typing import Optional

from kodingdiagram.coding.manager import CodingManager
from kodingdiagram.models import (
    NetworkEdge,
    NetworkGraph,
    NetworkNode,
    NodeType,
)
from kodingdiagram.theming.analyzer import ThematicAnalyzer


class NetworkBuilder:
    """Builds network visualizations from qualitative coding data."""

    def __init__(
        self,
        coding_manager: CodingManager,
        thematic_analyzer: Optional[ThematicAnalyzer] = None,
    ) -> None:
        self.coding = coding_manager
        self.theming = thematic_analyzer

    def code_quotation_network(self, document_id: Optional[str] = None) -> NetworkGraph:
        """Build a bipartite network of codes linked to their quotations."""
        graph = NetworkGraph()
        quotations = (
            self.coding.get_quotations_by_document(document_id)
            if document_id
            else self.coding.list_quotations()
        )

        added_codes: set[str] = set()
        for q in quotations:
            q_node = NetworkNode(
                id=q.id,
                label=q.text[:60] + ("..." if len(q.text) > 60 else ""),
                node_type=NodeType.QUOTATION,
                metadata={"document_id": q.document_id, "start": q.start_char, "end": q.end_char},
            )
            graph.nodes.append(q_node)

            for code_id in q.code_ids:
                code = self.coding.get_code(code_id)
                if code and code_id not in added_codes:
                    graph.nodes.append(
                        NetworkNode(
                            id=code.id,
                            label=code.name,
                            node_type=NodeType.CODE,
                            metadata={"color": code.color},
                        )
                    )
                    added_codes.add(code_id)
                graph.edges.append(
                    NetworkEdge(source=code_id, target=q.id, relation="codes")
                )

        return graph

    def code_co_occurrence_network(self, min_weight: int = 1) -> NetworkGraph:
        """Build network where codes are connected if they co-occur on quotations."""
        graph = NetworkGraph()
        co_occ = self.coding.code_co_occurrence()

        involved_codes: set[str] = set()
        for (c1, c2), count in co_occ.items():
            if count >= min_weight:
                involved_codes.add(c1)
                involved_codes.add(c2)
                graph.edges.append(
                    NetworkEdge(source=c1, target=c2, relation="co-occurs", weight=float(count))
                )

        for code_id in involved_codes:
            code = self.coding.get_code(code_id)
            if code:
                graph.nodes.append(
                    NetworkNode(
                        id=code.id,
                        label=code.name,
                        node_type=NodeType.CODE,
                        metadata={"color": code.color},
                    )
                )

        return graph

    def theme_hierarchy_network(self) -> NetworkGraph:
        """Build a hierarchical network of themes and their codes."""
        if not self.theming:
            return NetworkGraph()

        graph = NetworkGraph()

        for theme in self.theming.list_themes():
            graph.nodes.append(
                NetworkNode(
                    id=theme.id,
                    label=theme.name,
                    node_type=NodeType.THEME,
                    metadata={"level": theme.level.value},
                )
            )
            # Parent-child edges
            if theme.parent_theme_id:
                graph.edges.append(
                    NetworkEdge(
                        source=theme.parent_theme_id,
                        target=theme.id,
                        relation="contains",
                    )
                )
            # Theme-code edges
            for code_id in theme.code_ids:
                code = self.coding.get_code(code_id)
                if code:
                    # Add code node if not present
                    if not any(n.id == code_id for n in graph.nodes):
                        graph.nodes.append(
                            NetworkNode(
                                id=code.id,
                                label=code.name,
                                node_type=NodeType.CODE,
                                metadata={"color": code.color},
                            )
                        )
                    graph.edges.append(
                        NetworkEdge(source=theme.id, target=code_id, relation="groups")
                    )

        return graph

    def full_project_network(self) -> NetworkGraph:
        """Build a comprehensive network showing all entities and relations."""
        graph = NetworkGraph()

        # Documents
        for doc in self.coding.list_documents():
            graph.nodes.append(
                NetworkNode(id=doc.id, label=doc.name, node_type=NodeType.DOCUMENT)
            )

        # Codes
        for code in self.coding.list_codes():
            graph.nodes.append(
                NetworkNode(
                    id=code.id,
                    label=code.name,
                    node_type=NodeType.CODE,
                    metadata={"color": code.color},
                )
            )

        # Quotations + edges
        for q in self.coding.list_quotations():
            q_node = NetworkNode(
                id=q.id,
                label=q.text[:40],
                node_type=NodeType.QUOTATION,
            )
            graph.nodes.append(q_node)
            # quotation -> document
            graph.edges.append(
                NetworkEdge(source=q.document_id, target=q.id, relation="contains")
            )
            # quotation -> codes
            for code_id in q.code_ids:
                graph.edges.append(
                    NetworkEdge(source=code_id, target=q.id, relation="codes")
                )

        # Themes
        if self.theming:
            for theme in self.theming.list_themes():
                graph.nodes.append(
                    NetworkNode(
                        id=theme.id,
                        label=theme.name,
                        node_type=NodeType.THEME,
                        metadata={"level": theme.level.value},
                    )
                )
                for code_id in theme.code_ids:
                    graph.edges.append(
                        NetworkEdge(source=theme.id, target=code_id, relation="groups")
                    )
                if theme.parent_theme_id:
                    graph.edges.append(
                        NetworkEdge(
                            source=theme.parent_theme_id,
                            target=theme.id,
                            relation="contains",
                        )
                    )

        return graph

    # --- Export ---

    def to_networkx(self, graph: NetworkGraph):
        """Convert to a networkx Graph for further analysis or rendering."""
        import networkx as nx
        G = nx.Graph()
        for node in graph.nodes:
            G.add_node(node.id, label=node.label, node_type=node.node_type.value, **node.metadata)
        for edge in graph.edges:
            G.add_edge(edge.source, edge.target, relation=edge.relation, weight=edge.weight)
        return G

    def to_json(self, graph: NetworkGraph) -> str:
        """Export network as JSON suitable for D3.js or vis.js visualization."""
        return json.dumps(
            {
                "nodes": [n.model_dump() for n in graph.nodes],
                "edges": [e.model_dump() for e in graph.edges],
            },
            indent=2,
        )

    def to_gexf(self, graph: NetworkGraph) -> str:
        """Export as GEXF (Gephi compatible)."""
        import networkx as nx
        G = self.to_networkx(graph)
        buffer = io.BytesIO()
        nx.write_gexf(G, buffer)
        return buffer.getvalue().decode("utf-8")

    def to_png_bytes(self, graph: NetworkGraph, figsize: tuple = (12, 8)) -> bytes:
        """Render network as PNG image bytes using matplotlib."""
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        import networkx as nx

        G = self.to_networkx(graph)
        fig, ax = plt.subplots(figsize=figsize)

        pos = nx.spring_layout(G, seed=42)

        # Color by node type
        color_map = {
            "document": "#10b981",
            "code": "#3b82f6",
            "quotation": "#f59e0b",
            "theme": "#8b5cf6",
            "entity": "#ef4444",
        }
        colors = [color_map.get(G.nodes[n].get("node_type", "code"), "#6b7280") for n in G.nodes()]
        labels = {n: G.nodes[n].get("label", n)[:20] for n in G.nodes()}

        nx.draw(
            G,
            pos,
            ax=ax,
            node_color=colors,
            with_labels=True,
            labels=labels,
            node_size=600,
            font_size=7,
            edge_color="#d1d5db",
        )

        buf = io.BytesIO()
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        buf.seek(0)
        return buf.read()
