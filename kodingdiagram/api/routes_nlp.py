"""NLP API routes."""

from __future__ import annotations

from fastapi import APIRouter, Request
from pydantic import BaseModel

from kodingdiagram.models import EntityResult, LemmaResult, SentenceResult

router = APIRouter()


class TextInput(BaseModel):
    text: str


class SearchInput(BaseModel):
    search_term: str
    text: str


class SimilarityInput(BaseModel):
    text_a: str
    text_b: str


class KeywordsInput(BaseModel):
    text: str
    top_n: int = 20


@router.post("/lemmatize", response_model=list[LemmaResult])
def lemmatize(body: TextInput, request: Request):
    """Extract lemmas and their frequencies from text."""
    engine = request.app.state.nlp_engine
    return engine.lemmatize(body.text)


@router.post("/entities", response_model=list[EntityResult])
def named_entities(body: TextInput, request: Request):
    """Extract named entities (NER) with positions and labels."""
    engine = request.app.state.nlp_engine
    return engine.named_entities(body.text)


@router.post("/sentences", response_model=list[SentenceResult])
def sentences(body: TextInput, request: Request):
    """Split text into sentences with character positions."""
    engine = request.app.state.nlp_engine
    return engine.sentences(body.text)


@router.post("/search-sentences", response_model=list[SentenceResult])
def search_sentences(body: SearchInput, request: Request):
    """Find sentences containing all lemmatized forms of the search term."""
    engine = request.app.state.nlp_engine
    return engine.search_sentences_by_lemma(body.search_term, body.text)


@router.post("/keywords", response_model=list[LemmaResult])
def keywords(body: KeywordsInput, request: Request):
    """Extract top keywords (nouns, proper nouns, adjectives) by frequency."""
    engine = request.app.state.nlp_engine
    return engine.keywords(body.text, top_n=body.top_n)


@router.post("/similarity")
def similarity(body: SimilarityInput, request: Request):
    """Compute semantic similarity between two texts."""
    engine = request.app.state.nlp_engine
    score = engine.similarity(body.text_a, body.text_b)
    return {"similarity": score}


@router.post("/auto-code-suggestions", response_model=list[str])
def auto_code_suggestions(body: TextInput, request: Request):
    """Suggest potential code labels from text using NLP analysis."""
    engine = request.app.state.nlp_engine
    return engine.auto_code_suggestions(body.text)
