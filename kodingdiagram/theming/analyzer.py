"""Thematic Analyzer - thematic analysis for qualitative research.

Supports Braun & Clarke's 6-phase thematic analysis approach:
1. Familiarization
2. Generating initial codes
3. Searching for themes
4. Reviewing themes
5. Defining and naming themes
6. Producing the report

Provides both manual and auto-suggested theming.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Optional

from kodingdiagram.coding.manager import CodingManager
from kodingdiagram.models import Theme, ThemeLevel


class ThematicAnalyzer:
    """Manages thematic analysis on top of coded data."""

    def __init__(self, coding_manager: CodingManager) -> None:
        self.coding_manager = coding_manager
        self.themes: dict[str, Theme] = {}

    # --- Theme CRUD ---

    def create_theme(
        self,
        name: str,
        level: ThemeLevel = ThemeLevel.INITIAL,
        description: str = "",
        code_ids: Optional[list[str]] = None,
        parent_theme_id: Optional[str] = None,
    ) -> Theme:
        theme = Theme(
            name=name,
            level=level,
            description=description,
            code_ids=code_ids or [],
            parent_theme_id=parent_theme_id,
        )
        self.themes[theme.id] = theme
        return theme

    def get_theme(self, theme_id: str) -> Optional[Theme]:
        return self.themes.get(theme_id)

    def list_themes(self, level: Optional[ThemeLevel] = None) -> list[Theme]:
        if level:
            return [t for t in self.themes.values() if t.level == level]
        return list(self.themes.values())

    def delete_theme(self, theme_id: str) -> bool:
        if theme_id in self.themes:
            # Re-parent children
            for t in self.themes.values():
                if t.parent_theme_id == theme_id:
                    t.parent_theme_id = None
            del self.themes[theme_id]
            return True
        return False

    def assign_code_to_theme(self, theme_id: str, code_id: str) -> bool:
        theme = self.themes.get(theme_id)
        if theme and code_id not in theme.code_ids:
            theme.code_ids.append(code_id)
            return True
        return False

    def remove_code_from_theme(self, theme_id: str, code_id: str) -> bool:
        theme = self.themes.get(theme_id)
        if theme and code_id in theme.code_ids:
            theme.code_ids.remove(code_id)
            return True
        return False

    # --- Hierarchy ---

    def set_parent(self, theme_id: str, parent_id: Optional[str]) -> bool:
        theme = self.themes.get(theme_id)
        if not theme:
            return False
        if parent_id and parent_id not in self.themes:
            return False
        # Prevent circular reference
        if parent_id:
            current = parent_id
            while current:
                if current == theme_id:
                    return False
                parent = self.themes.get(current)
                current = parent.parent_theme_id if parent else None
        theme.parent_theme_id = parent_id
        return True

    def get_children(self, theme_id: str) -> list[Theme]:
        return [t for t in self.themes.values() if t.parent_theme_id == theme_id]

    def get_theme_hierarchy(self) -> dict[str, list[str]]:
        """Return tree as {parent_id: [child_ids]}. Root themes have parent=None."""
        tree: dict[str, list[str]] = defaultdict(list)
        for t in self.themes.values():
            parent_key = t.parent_theme_id or "__root__"
            tree[parent_key].append(t.id)
        return dict(tree)

    # --- Auto-suggestion ---

    def suggest_themes_from_co_occurrence(self, min_co_occurrence: int = 2) -> list[dict]:
        """Suggest potential themes based on code co-occurrence patterns.

        Codes that frequently appear together on the same quotations
        may belong to the same theme.
        """
        co_occ = self.coding_manager.code_co_occurrence()
        codes = self.coding_manager.codes

        # Group codes that co-occur frequently
        clusters: list[set[str]] = []
        for (c1, c2), count in co_occ.items():
            if count >= min_co_occurrence:
                # Find existing cluster or create new
                merged = False
                for cluster in clusters:
                    if c1 in cluster or c2 in cluster:
                        cluster.add(c1)
                        cluster.add(c2)
                        merged = True
                        break
                if not merged:
                    clusters.append({c1, c2})

        suggestions = []
        for cluster in clusters:
            code_names = [codes[cid].name for cid in cluster if cid in codes]
            suggestions.append({
                "suggested_name": " + ".join(sorted(code_names)[:3]),
                "code_ids": list(cluster),
                "code_names": code_names,
                "rationale": "Codes frequently co-occur on same quotations",
            })

        return suggestions

    def suggest_themes_from_keywords(self, nlp_engine=None, top_n: int = 5) -> list[dict]:
        """Suggest themes by analyzing keyword patterns across coded quotations.

        Groups codes whose quotations share similar vocabulary.
        """
        if nlp_engine is None:
            return []

        code_keywords: dict[str, Counter] = {}

        for code_id, code in self.coding_manager.codes.items():
            quotations = self.coding_manager.get_quotations_by_code(code_id)
            combined_text = " ".join(q.text for q in quotations)
            if combined_text.strip():
                keywords = nlp_engine.keywords(combined_text, top_n=10)
                code_keywords[code_id] = Counter({k.lemma: k.frequency for k in keywords})

        # Find codes with overlapping keywords
        suggestions = []
        code_ids = list(code_keywords.keys())

        for i, c1 in enumerate(code_ids):
            for c2 in code_ids[i + 1 :]:
                shared = set(code_keywords[c1].keys()) & set(code_keywords[c2].keys())
                if len(shared) >= 3:
                    codes = self.coding_manager.codes
                    suggestions.append({
                        "suggested_name": f"Theme: {', '.join(list(shared)[:3])}",
                        "code_ids": [c1, c2],
                        "code_names": [
                            codes[c1].name if c1 in codes else c1,
                            codes[c2].name if c2 in codes else c2,
                        ],
                        "shared_keywords": list(shared),
                        "rationale": "Codes share significant keyword overlap",
                    })

        return suggestions[:top_n]

    # --- Analytics ---

    def theme_saturation(self) -> dict[str, dict]:
        """Assess theme saturation: how many quotations support each theme."""
        result = {}
        for theme_id, theme in self.themes.items():
            total_quotations = 0
            for code_id in theme.code_ids:
                total_quotations += len(
                    self.coding_manager.get_quotations_by_code(code_id)
                )
            result[theme_id] = {
                "theme_name": theme.name,
                "num_codes": len(theme.code_ids),
                "num_quotations": total_quotations,
                "level": theme.level.value,
            }
        return result
