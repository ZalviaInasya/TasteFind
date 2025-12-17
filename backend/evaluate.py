import json
import os
import time
import numpy as np

# Optional heavy imports (graceful fallback)
try:
    from sentence_transformers import SentenceTransformer
    _SBERT_AVAILABLE = True
except Exception:
    SentenceTransformer = None
    _SBERT_AVAILABLE = False

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    _SKLEARN_AVAILABLE = True
except Exception:
    TfidfVectorizer = None
    cosine_similarity = None
    _SKLEARN_AVAILABLE = False


# Utility: load JSON dataset
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# Evaluation metrics
def precision(relevant, retrieved):
    if len(retrieved) == 0:
        return 0.0
    return len(set(relevant) & set(retrieved)) / len(retrieved)


def recall(relevant, retrieved):
    if len(relevant) == 0:
        return 0.0
    return len(set(relevant) & set(retrieved)) / len(relevant)


def f1(p, r):
    if p + r == 0:
        return 0.0
    return 2 * (p * r) / (p + r)


def average_precision(relevant, ranked_list):
    score = 0.0
    hits = 0
    for i, doc in enumerate(ranked_list, start=1):
        if doc in relevant:
            hits += 1
            score += hits / i
    if hits == 0:
        return 0.0
    return score / hits


def mean_average_precision(gt, results):
    ap_scores = []
    for q in gt:
        ap_scores.append(average_precision(gt[q], results.get(q, [])))
    if len(ap_scores) == 0:
        return 0.0
    return sum(ap_scores) / len(ap_scores)


class Evaluator:
    def __init__(self, dataset_path=None, ground_truth=None):
        # Resolve dataset path relative to this file if not provided
        if dataset_path is None:
            base = os.path.dirname(os.path.abspath(__file__))
            dataset_path = os.path.join(base, "metadata", "semua.json")

        if not os.path.exists(dataset_path):
            raise FileNotFoundError(f"Dataset not found at: {dataset_path}")

        try:
            self.data = load_json(dataset_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load dataset: {e}")

        # Build corpus from Judul + Isi Berita/Resep
        self.corpus = []
        for d in self.data:
            judul = d.get("Judul", "") or d.get("Judul Resep", "")
            isi = d.get("Isi Berita", "") or d.get("Isi Resep", "")
            text = (judul + " " + isi).strip()
            if not text:
                text = "unknown"
            self.corpus.append(text)

        # Prepare vectorizers (require sklearn)
        if not _SKLEARN_AVAILABLE:
            raise RuntimeError("scikit-learn is required for TF-IDF; install scikit-learn to enable evaluation")

        self.tfidf = TfidfVectorizer()
        self.tfidf_vectors = self.tfidf.fit_transform(self.corpus)

        # SBERT model and vectors are heavy — create lazily on demand
        self._sbert_model = None
        self._sbert_vectors = None
        self._sbert_available = _SBERT_AVAILABLE

    def _build_ground_truth_for_query(self, query, pool_indices):
        """
        Build REALISTIC ground truth:
        relevance ditentukan oleh konten dokumen,
        BUKAN oleh ranking algorithm
        """
        query_l = query.lower()
        q_terms = [t for t in query_l.split() if len(t) > 2]

        relevant = []

        for idx in pool_indices:
            doc = self.corpus[idx].lower()

            title_hit = 0
            body_hit = 0

            for t in q_terms:
                if t in doc:
                    body_hit += 1

            # Heuristik relevance (realistic)
            if body_hit >= len(q_terms):
                relevant.append(idx)
            elif body_hit >= 1:
                relevant.append(idx)

        return relevant

    def evaluate_query(self, query, algorithms=("tfidf", "sbert"), top_k=20):

        pool = set()

        # Measure runtime for each ranking algorithm when computing the ranks
        start = time.perf_counter()
        tfidf_rank = self._rank_tfidf_cosine(query, top_k=top_k)
        tfidf_runtime_ms = (time.perf_counter() - start) * 1000
        pool.update(tfidf_rank)

        sbert_rank = []
        sbert_runtime_ms = 0.0
        if self._sbert_available:
            start = time.perf_counter()
            sbert_rank = self._rank_cosine_sbert(query, top_k=top_k)
            sbert_runtime_ms = (time.perf_counter() - start) * 1000
            pool.update(sbert_rank)

        pool = list(pool)

        # Ground truth berdasarkan SELURUH KORPUS (agar relevant_count benar-benar representatif)
        relevant_docs = self._build_ground_truth_for_query(query, range(len(self.corpus)))

        if len(relevant_docs) == 0:
            return {
                "query": query,
                "metrics": {
                    algo: {"precision": 0, "recall": 0, "f1": 0, "ap": 0, "map": 0}
                    for algo in algorithms
                }
            }

        result = {"query": query, "metrics": {}}

        for algo in algorithms:
            if algo == "tfidf":
                ranked = tfidf_rank
                runtime_ms = tfidf_runtime_ms
            elif algo == "sbert":
                ranked = sbert_rank if self._sbert_available else []
                runtime_ms = sbert_runtime_ms if self._sbert_available else 0.0
            else:
                raise ValueError(algo)

            p = precision(relevant_docs, ranked)
            r = recall(relevant_docs, ranked)
            f = f1(p, r)
            ap = average_precision(relevant_docs, ranked)

            result["metrics"][algo] = {
                "precision": p,
                "recall": r,
                "f1": f,
                "ap": ap,
                "map": ap,
                "runtime_ms": runtime_ms,
                "runtime_s": runtime_ms / 1000.0,
                "relevant_count": len(relevant_docs),
                "retrieved_count": len(ranked),
                "intersection_count": len(set(relevant_docs) & set(ranked)),
                "relevant_ids": sorted(relevant_docs),
                "retrieved_ids": list(ranked)
            }

        return result


    def _ensure_sbert(self):
        if not self._sbert_available:
            raise RuntimeError("SBERT model not available (sentence-transformers package missing)")
        if self._sbert_model is None or self._sbert_vectors is None:
            # load model and encode corpus
            try:
                self._sbert_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
                self._sbert_vectors = self._sbert_model.encode(self.corpus, convert_to_numpy=True)
            except Exception as e:
                self._sbert_available = False
                raise

    def _rank_tfidf_cosine(self, query, top_k=20):
        q_vec = self.tfidf.transform([query])
        sim = cosine_similarity(q_vec, self.tfidf_vectors)[0]
        ranked = np.argsort(sim)[::-1][:top_k]
        return ranked.tolist()

    def _rank_cosine_sbert(self, query, top_k=20):
        # ensure model and vectors ready
        self._ensure_sbert()
        q_vec = self._sbert_model.encode([query])[0]
        sim = cosine_similarity([q_vec], self._sbert_vectors)[0]
        ranked = np.argsort(sim)[::-1][:top_k]
        return ranked.tolist()

    def evaluate(self, sample_size=50, top_k=20):
        """Aggregate evaluation over a sample of queries to build a quick overview report."""
        # build candidate queries using frequent terms in the corpus
        token_counts = {}
        for doc in self.corpus:
            for tok in doc.split():
                tok = tok.strip().lower()
                if len(tok) <= 3:
                    continue
                token_counts[tok] = token_counts.get(tok, 0) + 1

        # pick most frequent tokens as query candidates
        candidates = sorted(token_counts.items(), key=lambda x: x[1], reverse=True)
        queries = [tok for tok, _ in candidates[: max(sample_size, 10) ]] if candidates else ["makanan"]

        agg = {"tfidf": {"precision": [], "recall": [], "f1": [], "map": [], "runtime_ms": []},
               "sbert": {"precision": [], "recall": [], "f1": [], "map": [], "runtime_ms": []}}

        for q in queries[:sample_size]:
            res = self.evaluate_query(q, algorithms=("tfidf", "sbert"), top_k=top_k)
            for algo in ("tfidf", "sbert"):
                m = res["metrics"].get(algo, {})
                agg[algo]["precision"].append(m.get("precision", 0.0))
                agg[algo]["recall"].append(m.get("recall", 0.0))
                agg[algo]["f1"].append(m.get("f1", 0.0))
                agg[algo]["map"].append(m.get("ap", 0.0))
                agg[algo]["runtime_ms"].append(m.get("runtime_ms", 0.0))

        report = {"metrics": {}}
        for algo in ("tfidf", "sbert"):
            vals = agg[algo]
            report["metrics"][algo] = {
                "precision": float(sum(vals["precision"]) / max(1, len(vals["precision"]))),
                "recall": float(sum(vals["recall"]) / max(1, len(vals["recall"]))),
                "f1": float(sum(vals["f1"]) / max(1, len(vals["f1"]))),
                "map": float(sum(vals["map"]) / max(1, len(vals["map"]))),
                "runtime_ms": float(sum(vals["runtime_ms"]) / max(1, len(vals["runtime_ms"])))
            }

        return report


if __name__ == "__main__":
    # Demo: test dynamic evaluation untuk berbagai queries
    evaluator = Evaluator()
    
    test_queries = ["ayam goreng", "resep sehat", "minuman segar", "berita kuliner", "kue lezat"]
    
    print("=" * 80)
    print("DEMO: DYNAMIC QUERY EVALUATION")
    print("=" * 80)
    
    for query in test_queries:
        result = evaluator.evaluate_query(query)
        print(f"\nQuery: '{query}'")
        print(f"  TF-IDF: P={result['metrics']['tfidf']['precision']:.3f}, "
              f"R={result['metrics']['tfidf']['recall']:.3f}, "
              f"F1={result['metrics']['tfidf']['f1']:.3f}, "
              f"AP={result['metrics']['tfidf']['ap']:.3f}")
        print(f"  SBERT:  P={result['metrics']['sbert']['precision']:.3f}, "
              f"R={result['metrics']['sbert']['recall']:.3f}, "
              f"F1={result['metrics']['sbert']['f1']:.3f}, "
              f"AP={result['metrics']['sbert']['ap']:.3f}")
