"""NLP Engine - spaCy-based text analysis for qualitative research.

Ported and modernized from ATLAS.ti NLP_showcase concepts:
- Lemmatization with frequency analysis
- Lemma-based sentence search (unionised)
- Named Entity Recognition (NER)
- Keyword extraction
- Text similarity
"""

from __future__ import annotations

from collections import Counter
from typing import Optional

import spacy
from spacy.language import Language

from kodingdiagram.models import EntityResult, LemmaResult, SentenceResult


class NLPEngine:
    """Core NLP engine wrapping spaCy for qualitative data analysis."""

    def __init__(self, model_name: str = "en_core_web_sm"):
        self._model_name = model_name
        self._nlp: Optional[Language] = None

    @property
    def nlp(self) -> Language:
        """Lazy-load the spaCy model."""
        if self._nlp is None:
            try:
                self._nlp = spacy.load(self._model_name)
            except OSError:
                # Download if not available
                from spacy.cli import download
                download(self._model_name)
                self._nlp = spacy.load(self._model_name)
        return self._nlp

    def lemmatize(self, text: str) -> list[LemmaResult]:
        """Extract lemmas and their frequencies from text.

        Based on ATLAS.ti's lemmas_for_document() but returns structured data.
        """
        doc = self.nlp(text)
        counter: Counter[str] = Counter()

        for token in doc:
            if not token.is_punct and not token.is_space:
                counter[token.lemma_] += 1

        return sorted(
            [LemmaResult(lemma=lemma, frequency=freq) for lemma, freq in counter.items()],
            key=lambda r: r.frequency,
            reverse=True,
        )

    def named_entities(self, text: str) -> list[EntityResult]:
        """Extract named entities with positions and labels.

        Based on ATLAS.ti's named_entity_sentences_and_types_for_document().
        """
        doc = self.nlp(text)
        return [
            EntityResult(
                text=ent.text,
                label=ent.label_,
                start_char=ent.start_char,
                end_char=ent.end_char,
            )
            for ent in doc.ents
        ]

    def search_sentences_by_lemma(self, search_term: str, text: str) -> list[SentenceResult]:
        """Find sentences containing ALL lemmatized forms of the search term.

        Based on ATLAS.ti's lemma_sentences_for_unionised_request().
        A sentence matches if it contains lemma forms of every token in the search term.
        """
        search_doc = self.nlp(search_term)
        search_lemmas = {
            token.lemma_
            for token in search_doc
            if not token.is_punct and not token.is_space
        }

        if not search_lemmas:
            return []

        doc = self.nlp(text)
        results: list[SentenceResult] = []

        for sent in doc.sents:
            sentence_lemmas = {
                token.lemma_
                for token in sent
                if not token.is_punct and not token.is_space
            }
            if search_lemmas.issubset(sentence_lemmas):
                # Calculate char positions
                start_char = doc[sent.start].idx
                last_token = doc[sent.end - 1]
                end_char = last_token.idx + len(last_token)
                results.append(
                    SentenceResult(
                        text=sent.text.strip(),
                        start_char=start_char,
                        end_char=end_char,
                    )
                )

        return results

    def keywords(self, text: str, top_n: int = 20) -> list[LemmaResult]:
        """Extract top keywords (nouns, proper nouns, adjectives) by frequency."""
        doc = self.nlp(text)
        counter: Counter[str] = Counter()

        for token in doc:
            if token.pos_ in ("NOUN", "PROPN", "ADJ") and not token.is_stop:
                counter[token.lemma_] += 1

        return [
            LemmaResult(lemma=lemma, frequency=freq)
            for lemma, freq in counter.most_common(top_n)
        ]

    def sentences(self, text: str) -> list[SentenceResult]:
        """Split text into sentences with character positions."""
        doc = self.nlp(text)
        results: list[SentenceResult] = []

        for sent in doc.sents:
            start_char = doc[sent.start].idx
            last_token = doc[sent.end - 1]
            end_char = last_token.idx + len(last_token)
            results.append(
                SentenceResult(
                    text=sent.text.strip(),
                    start_char=start_char,
                    end_char=end_char,
                )
            )

        return results

    def similarity(self, text_a: str, text_b: str) -> float:
        """Compute semantic similarity between two texts (0.0 - 1.0)."""
        doc_a = self.nlp(text_a)
        doc_b = self.nlp(text_b)
        return doc_a.similarity(doc_b)

    def auto_code_suggestions(self, text: str, top_n: int = 10) -> list[str]:
        """Suggest potential codes based on frequent meaningful noun phrases and entities.

        Useful for initial open coding in qualitative research.
        """
        doc = self.nlp(text)

        candidates: Counter[str] = Counter()

        # Noun chunks
        for chunk in doc.noun_chunks:
            normalized = chunk.lemma_.lower().strip()
            if len(normalized) > 2 and not all(t.is_stop for t in chunk):
                candidates[normalized] += 1

        # Named entities
        for ent in doc.ents:
            candidates[ent.text.lower().strip()] += 1

        return [term for term, _ in candidates.most_common(top_n)]
