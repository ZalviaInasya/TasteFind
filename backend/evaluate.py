import json
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# =============================
# 1. LOAD DATASET
# =============================
def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

data = load_json("backend/dataset/semua.json")
corpus = [d["Judul"] + " " + d["Isi Berita"] for d in data]

# =============================
# 2. Ground Truth Evaluasi
# =============================
ground_truth = {
    "ayam": [3, 7, 9],
    "soto": [2, 11, 14],
    "es teh": [50, 52],
    "bakso": [22, 25, 27]
}

# =============================
# 3. TF-IDF VECTOR
# =============================
tfidf = TfidfVectorizer()
tfidf_vectors = tfidf.fit_transform(corpus)

# =============================
# 4. SBERT VECTOR
# =============================
sbert_model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
sbert_vectors = sbert_model.encode(corpus, convert_to_numpy=True)

# =============================
# 5. METRIK EVALUASI
# =============================
def precision(relevant, retrieved):
    if len(retrieved) == 0: return 0
    return len(set(relevant) & set(retrieved)) / len(retrieved)

def recall(relevant, retrieved):
    if len(relevant) == 0: return 0
    return len(set(relevant) & set(retrieved)) / len(relevant)

def f1(p, r):
    if p+r == 0: return 0
    return 2 * (p*r) / (p+r)

def average_precision(relevant, ranked_list):
    score = 0
    hits = 0
    for i, doc in enumerate(ranked_list, start=1):
        if doc in relevant:
            hits += 1
            score += hits / i
    if hits == 0:
        return 0
    return score / hits

def mean_average_precision(gt, results):
    ap_scores = []
    for q in gt:
        ap_scores.append(average_precision(gt[q], results[q]))
    return sum(ap_scores) / len(ap_scores)

# =============================
# 6. HITUNG EVALUASI
# =============================
results_tfidf = {}
results_sbert = {}

for query in ground_truth:
    # TF-IDF search
    q_vec = tfidf.transform([query])
    sim = cosine_similarity(q_vec, tfidf_vectors)[0]
    ranked = np.argsort(sim)[::-1][:20]
    results_tfidf[query] = ranked.tolist()

    # SBERT search
    q_vec2 = sbert_model.encode([query])[0]
    sim2 = cosine_similarity([q_vec2], sbert_vectors)[0]
    ranked2 = np.argsort(sim2)[::-1][:20]
    results_sbert[query] = ranked2.tolist()

# =============================
# 7. HASIL EVALUASI
# =============================
print("=== TF-IDF Evaluation ===")
for q in ground_truth:
    p = precision(ground_truth[q], results_tfidf[q])
    r = recall(ground_truth[q], results_tfidf[q])
    f = f1(p, r)
    ap = average_precision(ground_truth[q], results_tfidf[q])
    print(f"Query: {q}")
    print("Precision:", round(p, 4))
    print("Recall:", round(r, 4))
    print("F1-Score:", round(f, 4))
    print("AP:", round(ap, 4))
    print("---")

print("MAP TF-IDF:", mean_average_precision(ground_truth, results_tfidf))

print("\n=== SBERT Evaluation ===")
for q in ground_truth:
    p = precision(ground_truth[q], results_sbert[q])
    r = recall(ground_truth[q], results_sbert[q])
    f = f1(p, r)
    ap = average_precision(ground_truth[q], results_sbert[q])
    print(f"Query: {q}")
    print("Precision:", round(p, 4))
    print("Recall:", round(r, 4))
    print("F1-Score:", round(f, 4))
    print("AP:", round(ap, 4))
    print("---")

print("MAP SBERT:", mean_average_precision(ground_truth, results_sbert))