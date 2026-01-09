"""
Full-Text Engine - Hybrid semantic/keyword search.

Provides full-text indexing with hybrid semantic and keyword search,
ranking fusion, and snippet generation.
"""
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass
from collections import defaultdict
import re


@dataclass
class Document:
    """Text document."""
    doc_id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[List[float]] = None


@dataclass
class SearchResult:
    """Search result with score and snippet."""
    doc_id: str
    score: float
    snippet: str
    metadata: Dict[str, Any]


class FullTextEngine:
    """
    Full-text search engine with hybrid semantic/keyword search.

    Combines traditional keyword search with semantic similarity
    for improved relevance ranking.
    """

    def __init__(self):
        self.documents: Dict[str, Document] = {}
        self.inverted_index: Dict[str, Set[str]] = defaultdict(set)  # term -> doc_ids
        self.term_frequencies: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))  # doc_id -> term -> count

    def index_document(self, doc_id: str, content: str,
                      metadata: Optional[Dict[str, Any]] = None,
                      embedding: Optional[List[float]] = None) -> None:
        """
        Index document for search.

        Args:
            doc_id: Document identifier
            content: Document content
            metadata: Optional metadata
            embedding: Optional semantic embedding
        """
        doc = Document(
            doc_id=doc_id,
            content=content,
            metadata=metadata or {},
            embedding=embedding
        )

        self.documents[doc_id] = doc

        # Tokenize and build inverted index
        terms = self._tokenize(content)

        for term in terms:
            self.inverted_index[term].add(doc_id)
            self.term_frequencies[doc_id][term] += 1

    def search(self, query: str, k: int = 10,
               mode: str = "hybrid",
               query_embedding: Optional[List[float]] = None) -> List[SearchResult]:
        """
        Search documents.

        Args:
            query: Search query
            k: Number of results to return
            mode: Search mode (keyword, semantic, hybrid)
            query_embedding: Query embedding for semantic search

        Returns:
            List of search results
        """
        if mode == "keyword":
            return self._keyword_search(query, k)
        elif mode == "semantic" and query_embedding:
            return self._semantic_search(query_embedding, k)
        elif mode == "hybrid" and query_embedding:
            return self._hybrid_search(query, query_embedding, k)
        else:
            return self._keyword_search(query, k)

    def _keyword_search(self, query: str, k: int) -> List[SearchResult]:
        """Keyword-based search using TF-IDF."""
        query_terms = self._tokenize(query)

        if not query_terms:
            return []

        # Compute IDF for query terms
        num_docs = len(self.documents)
        idf = {}
        for term in query_terms:
            doc_freq = len(self.inverted_index.get(term, set()))
            idf[term] = math.log((num_docs + 1) / (doc_freq + 1)) if doc_freq > 0 else 0

        # Score documents
        scores = defaultdict(float)

        for term in query_terms:
            for doc_id in self.inverted_index.get(term, set()):
                tf = self.term_frequencies[doc_id][term]
                scores[doc_id] += tf * idf[term]

        # Sort by score
        ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]

        # Generate results with snippets
        results = []
        for doc_id, score in ranked:
            doc = self.documents[doc_id]
            snippet = self._generate_snippet(doc.content, query_terms)

            results.append(SearchResult(
                doc_id=doc_id,
                score=score,
                snippet=snippet,
                metadata=doc.metadata
            ))

        return results

    def _semantic_search(self, query_embedding: List[float], k: int) -> List[SearchResult]:
        """Semantic search using embeddings."""
        scores = []

        for doc_id, doc in self.documents.items():
            if doc.embedding:
                similarity = self._cosine_similarity(query_embedding, doc.embedding)
                scores.append((doc_id, similarity))

        # Sort by similarity
        scores.sort(key=lambda x: x[1], reverse=True)

        # Generate results
        results = []
        for doc_id, score in scores[:k]:
            doc = self.documents[doc_id]
            snippet = doc.content[:200] + "..." if len(doc.content) > 200 else doc.content

            results.append(SearchResult(
                doc_id=doc_id,
                score=score,
                snippet=snippet,
                metadata=doc.metadata
            ))

        return results

    def _hybrid_search(self, query: str, query_embedding: List[float], k: int) -> List[SearchResult]:
        """Hybrid search combining keyword and semantic."""
        # Get keyword results
        keyword_results = self._keyword_search(query, k * 2)
        keyword_scores = {r.doc_id: r.score for r in keyword_results}

        # Get semantic results
        semantic_results = self._semantic_search(query_embedding, k * 2)
        semantic_scores = {r.doc_id: r.score for r in semantic_results}

        # Normalize scores
        if keyword_scores:
            max_keyword = max(keyword_scores.values())
            keyword_scores = {k: v / max_keyword for k, v in keyword_scores.items()}

        if semantic_scores:
            max_semantic = max(semantic_scores.values())
            semantic_scores = {k: v / max_semantic for k, v in semantic_scores.items()}

        # Combine scores (weighted average)
        combined_scores = {}
        all_doc_ids = set(keyword_scores.keys()) | set(semantic_scores.keys())

        for doc_id in all_doc_ids:
            kw_score = keyword_scores.get(doc_id, 0)
            sem_score = semantic_scores.get(doc_id, 0)
            combined_scores[doc_id] = 0.5 * kw_score + 0.5 * sem_score

        # Sort by combined score
        ranked = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)[:k]

        # Generate results
        query_terms = self._tokenize(query)
        results = []

        for doc_id, score in ranked:
            doc = self.documents[doc_id]
            snippet = self._generate_snippet(doc.content, query_terms)

            results.append(SearchResult(
                doc_id=doc_id,
                score=score,
                snippet=snippet,
                metadata=doc.metadata
            ))

        return results

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into terms."""
        # Simple tokenization (lowercase, alphanumeric)
        text = text.lower()
        terms = re.findall(r'\w+', text)

        # Remove stop words (simplified)
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for'}
        terms = [t for t in terms if t not in stop_words and len(t) > 2]

        return terms

    def _generate_snippet(self, content: str, query_terms: List[str], context_chars: int = 100) -> str:
        """Generate snippet highlighting query terms."""
        content_lower = content.lower()

        # Find first occurrence of any query term
        first_pos = len(content)
        for term in query_terms:
            pos = content_lower.find(term)
            if pos != -1 and pos < first_pos:
                first_pos = pos

        if first_pos == len(content):
            # No terms found, return beginning
            return content[:200] + "..." if len(content) > 200 else content

        # Extract context around first term
        start = max(0, first_pos - context_chars)
        end = min(len(content), first_pos + context_chars)

        snippet = content[start:end]

        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."

        return snippet

    def _cosine_similarity(self, v1: List[float], v2: List[float]) -> float:
        """Compute cosine similarity between vectors."""
        if len(v1) != len(v2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(x**2 for x in v1))
        norm2 = math.sqrt(sum(x**2 for x in v2))

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        return {
            "num_documents": len(self.documents),
            "num_terms": len(self.inverted_index),
            "avg_doc_length": sum(len(doc.content) for doc in self.documents.values()) / max(len(self.documents), 1)
        }


import math
