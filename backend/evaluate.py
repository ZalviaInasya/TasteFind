import json
import os
import time
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


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

        # Prepare vectorizers
        self.tfidf = TfidfVectorizer()
        self.tfidf_vectors = self.tfidf.fit_transform(self.corpus)

        # SBERT model and vectors are heavy — create lazily on demand
        self._sbert_model = None
        self._sbert_vectors = None

    def _build_ground_truth_for_query(self, query):
        """
        Build ground truth DINAMIS untuk query tertentu.
        Ini memastikan setiap query punya relevant docs yang berbeda.
        """
        query_lower = query.lower()
        doc_scores = []
        
        # Score setiap dokumen berdasarkan keyword match dengan query
        for idx, doc in enumerate(self.corpus):
            doc_lower = doc.lower()
            score = 0
            
            # Split query into keywords dan score match
            keywords = [kw for kw in query_lower.split() if len(kw) > 2]  # exclude short words
            
            for kw in keywords:
                # Direct keyword match
                count = doc_lower.count(kw)
                score += count * 2
                
                # Phrase match (if query is multi-word)
                if query_lower in doc_lower:
                    score += 10  # High boost untuk exact phrase match
            
            if score > 0:
                doc_scores.append((idx, score))
        
        # Sort by score dan ambil top-20
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        relevant_indices = [idx for idx, score in doc_scores[:20]]
        
        return relevant_indices

    def evaluate_query(self, query, algorithms=("tfidf", "sbert"), top_k=20):
        """
        Evaluate specific query dengan dynamic ground truth.
        Ini memberikan hasil evaluasi yang UNIK untuk setiap query.
        """
        # Build ground truth untuk query ini
        relevant_docs = self._build_ground_truth_for_query(query)
        
        if len(relevant_docs) == 0:
            # Query tidak match dengan dokumen apapun
            return {
                "query": query,
                "metrics": {
                    "tfidf": {
                        "precision": 0.0,
                        "recall": 0.0,
                        "f1": 0.0,
                        "ap": 0.0,
                        "ranked_indices": []
                    },
                    "sbert": {
                        "precision": 0.0,
                        "recall": 0.0,
                        "f1": 0.0,
                        "ap": 0.0,
                        "ranked_indices": []
                    }
                }
            }
        
        result = {"query": query, "metrics": {}}
        
        for algo in algorithms:
            if algo == "tfidf":
                ranked = self._rank_tfidf_cosine(query, top_k=top_k)
            elif algo == "sbert":
                ranked = self._rank_cosine_sbert(query, top_k=top_k)
            else:
                raise ValueError(f"Unknown algorithm: {algo}")
            
            p = precision(relevant_docs, ranked)
            r = recall(relevant_docs, ranked)
            f = f1(p, r)
            ap = average_precision(relevant_docs, ranked)
            
            result["metrics"][algo] = {
                "precision": float(p),
                "recall": float(r),
                "f1": float(f),
                "ap": float(ap),
                "ranked_indices": ranked
            }
        
        return result

    def _ensure_sbert(self):
        if self._sbert_model is None or self._sbert_vectors is None:
            # load model and encode corpus
            self._sbert_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
            self._sbert_vectors = self._sbert_model.encode(self.corpus, convert_to_numpy=True)

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
