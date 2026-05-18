# KodingDiagram

**Qualitative Data Analysis Toolkit** — integrating NLP, coding, thematic analysis, and network visualization for researchers.

Inspired by [ATLAS.ti](https://atlasti.com)'s NLP architecture, modernized as a Python REST API.

## Features

### NLP Engine (spaCy)
- **Lemmatization** — extract lemmas with frequency counts
- **Named Entity Recognition (NER)** — detect persons, places, organizations, etc.
- **Sentence Search** — find sentences by lemmatized search terms (unionised)
- **Keyword Extraction** — top nouns/adjectives by frequency
- **Text Similarity** — semantic similarity scoring
- **Auto-Code Suggestions** — NLP-powered initial coding suggestions

### Qualitative Coding
- Create and manage **codes** with colors and descriptions
- Assign **quotations** (text segments) to codes
- Write **memos** linked to codes/quotations
- Organize codes into **groups**
- **Code frequency** and **co-occurrence** analytics

### Thematic Analysis
- Create hierarchical **themes** (initial → organizing → global)
- Map codes to themes
- **Auto-suggest themes** from co-occurrence patterns
- **Keyword-based theme suggestions** across coded data
- **Theme saturation** assessment

### Network Visualization
- **Code-Quotation** bipartite networks
- **Code Co-occurrence** networks
- **Theme Hierarchy** networks
- **Full Project** networks (all entities)
- Export to **JSON** (D3.js/vis.js), **GEXF** (Gephi), **PNG**

## Quick Start

```bash
# Install
pip install -e .

# Download spaCy model
python -m spacy download en_core_web_sm

# Start the API server
kodingdiagram --port 8000

# Or run directly
python -m kodingdiagram
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## API Endpoints

| Prefix | Description |
|--------|-------------|
| `POST /api/nlp/lemmatize` | Lemmatize text |
| `POST /api/nlp/entities` | Named Entity Recognition |
| `POST /api/nlp/search-sentences` | Lemma-based sentence search |
| `POST /api/nlp/keywords` | Keyword extraction |
| `POST /api/nlp/similarity` | Text similarity |
| `POST /api/nlp/auto-code-suggestions` | AI code suggestions |
| `POST /api/coding/documents` | Add document |
| `POST /api/coding/codes` | Create code |
| `POST /api/coding/quotations` | Create quotation |
| `POST /api/coding/memos` | Create memo |
| `GET /api/coding/analytics/co-occurrence` | Code co-occurrence |
| `POST /api/theming/themes` | Create theme |
| `GET /api/theming/suggestions/co-occurrence` | Auto-suggest themes |
| `GET /api/theming/saturation` | Theme saturation |
| `GET /api/visualization/full-project` | Full network JSON |
| `GET /api/visualization/export/png` | Export as PNG |
| `GET /api/visualization/export/gexf` | Export as GEXF |

## Architecture

```
kodingdiagram/
├── models.py              # Shared Pydantic data models
├── main.py                # CLI entry point
├── nlp/
│   └── engine.py          # spaCy NLP engine
├── coding/
│   └── manager.py         # Qualitative coding operations
├── theming/
│   └── analyzer.py        # Thematic analysis
├── visualization/
│   └── network.py         # Network graph builder
└── api/
    ├── app.py             # FastAPI app factory
    ├── routes_nlp.py      # NLP endpoints
    ├── routes_coding.py   # Coding endpoints
    ├── routes_theming.py  # Theming endpoints
    └── routes_visualization.py  # Visualization endpoints
```

## Acknowledgments

NLP architecture concepts adapted from [ATLAS.ti NLP_showcase](https://github.com/atlasti/NLP_showcase).

## License

MIT
