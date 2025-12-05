"""
Query Engine untuk TasteFind - PRODUCTION VERSION
FIXED: Preprocessing, NaN handling, scoring accuracy
"""

import json
import pickle
import numpy as np
from scipy.sparse import load_npz
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import re

# Load SBERT model once
SBERT_MODEL = None

# ============================================================
# CONFIGURATION
# ============================================================
TFIDF_MIN_SCORE = 0.01  # Very low threshold - let relevance check do the filtering
SBERT_MIN_SCORE = 0.25  # Lower threshold
TFIDF_WEIGHT = 0.5
SBERT_WEIGHT = 0.5

# ============================================================
# SIMPLE TOKENIZER (must be at module level for pickle)
# ============================================================
def simple_tokenizer(text):
    """Simple tokenizer yang bisa di-pickle"""
    return text.split()

# ============================================================
# SBERT MODEL LOADER
# ============================================================
def get_sbert_model():
    """Load SBERT model lazily"""
    global SBERT_MODEL
    if SBERT_MODEL is None:
        print("[INFO] Loading SBERT model...")
        SBERT_MODEL = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    return SBERT_MODEL

# ============================================================
# PREPROCESSING - MINIMAL & SAFE
# ============================================================
def minimal_preprocess(text):
    """
    Minimal preprocessing - HANYA lowercase dan basic cleaning
    TIDAK ada stemming atau stopword removal yang agresif
    """
    if not text:
        return ""
    
    text = str(text).lower().strip()
    
    # Remove extra whitespace only
    text = re.sub(r'\s+', ' ', text)
    
    return text

# ============================================================
# PHRASE MATCHING
# ============================================================
def check_exact_phrase(query, text):
    """Check if exact phrase exists in text"""
    query_clean = minimal_preprocess(query)
    text_clean = minimal_preprocess(text)
    return query_clean in text_clean

def check_all_words_present(query, text):
    """Check if all query words are present in text"""
    query_words = set(minimal_preprocess(query).split())
    text_words = set(minimal_preprocess(text).split())
    return query_words.issubset(text_words)

def calculate_word_overlap(query, text):
    """Calculate percentage of query words present in text"""
    query_words = set(minimal_preprocess(query).split())
    text_words = set(minimal_preprocess(text).split())
    
    if not query_words:
        return 0.0
    
    overlap = len(query_words & text_words)
    return overlap / len(query_words)

# ============================================================
# COOKING METHOD CONFLICT DETECTION
# ============================================================
def has_cooking_conflict(query, text):
    """
    Check if document has conflicting cooking method
    Example: query="ayam bakar" should NOT match "ayam goreng"
    """
    query_lower = minimal_preprocess(query)
    text_lower = minimal_preprocess(text)
    
    # Define cooking method conflicts
    cooking_methods = {
        'bakar': ['goreng', 'rebus', 'kukus', 'tumis'],
        'goreng': ['bakar', 'rebus', 'kukus'],
        'rebus': ['bakar', 'goreng', 'kukus', 'tumis'],
        'kukus': ['bakar', 'goreng', 'rebus', 'tumis'],
        'tumis': ['bakar', 'rebus', 'kukus']
    }
    
    # Check if query contains a cooking method
    query_method = None
    for method in cooking_methods.keys():
        if method in query_lower:
            query_method = method
            break
    
    # If no cooking method in query, no conflict
    if not query_method:
        return False
    
    # If query method is in document, no conflict
    if query_method in text_lower:
        return False
    
    # Check if document has conflicting method
    for conflict_method in cooking_methods[query_method]:
        if conflict_method in text_lower:
            return True  # Conflict found!
    
    return False

# ============================================================
# RELEVANCE SCORING
# ============================================================
def calculate_relevance_score(query, doc):
    """
    Calculate relevance score based on phrase matching
    Returns: float (0-1)
    """
    # Get document text
    title = doc.get('Judul', '')
    content_key = 'Isi Berita' if 'Isi Berita' in doc else 'Isi Resep'
    content = doc.get(content_key, '')
    full_text = f"{title} {content}"
    
    # 1. Exact phrase match in title = highest score
    if check_exact_phrase(query, title):
        return 1.0
    
    # 2. Exact phrase match in content = high score
    if check_exact_phrase(query, full_text):
        return 0.9
    
    # 3. All words present = good score
    if check_all_words_present(query, full_text):
        # But check for cooking method conflicts
        if has_cooking_conflict(query, full_text):
            return 0.0  # REJECT conflicting documents
        return 0.7
    
    # 4. Partial word overlap
    overlap = calculate_word_overlap(query, full_text)
    if overlap > 0.5:  # At least 50% words match
        # Check for conflicts
        if has_cooking_conflict(query, full_text):
            return 0.0
        return 0.4 * overlap
    
    # 5. Low relevance
    return 0.1 * overlap

# ============================================================
# LOAD METADATA - WITH NaN CLEANING
# ============================================================
def load_metadata(category):
    """Load and clean metadata"""
    json_path = f"metadata/{category}.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Clean NaN values
    cleaned = []
    for doc in data:
        clean_doc = {}
        for key, value in doc.items():
            if isinstance(value, float):
                if np.isnan(value) or np.isinf(value):
                    clean_doc[key] = ""  # Empty string instead of null for URLs
                else:
                    clean_doc[key] = value
            elif value is None:
                clean_doc[key] = ""
            else:
                clean_doc[key] = value
        cleaned.append(clean_doc)
    
    return cleaned

# ============================================================
# TF-IDF SEARCH
# ============================================================
def search_tfidf(query, category, top_k=20):
    """TF-IDF search with minimal preprocessing"""
    try:
        # Load vectorizer & matrix
        class PickleUnpickler(pickle.Unpickler):
            def find_class(self, module, name):
                if name == 'simple_tokenizer':
                    return simple_tokenizer
                return super().find_class(module, name)
        
        try:
            with open(f"tfidf/{category}_vectorizer.pkl", "rb") as f:
                vectorizer = PickleUnpickler(f).load()
        except:
            vectorizer = pickle.load(open(f"tfidf/{category}_vectorizer.pkl", "rb"))
        
        tfidf_matrix = load_npz(f"tfidf/{category}_matrix.npz")
        metadata = load_metadata(category)
        
        # Minimal preprocessing - just lowercase and join
        query_processed = minimal_preprocess(query)
        
        print(f"[TF-IDF] Query: '{query}' -> '{query_processed}'")
        
        # Transform query
        q_vec = vectorizer.transform([query_processed])
        
        # Calculate similarity
        scores = cosine_similarity(q_vec, tfidf_matrix).flatten()
        
        # Get top results (with low threshold)
        valid_idx = np.where(scores >= TFIDF_MIN_SCORE)[0]
        
        if len(valid_idx) == 0:
            print(f"[TF-IDF] No results found")
            return {"indices": [], "scores": [], "metadata": []}
        
        # Sort by score
        sorted_idx = valid_idx[np.argsort(scores[valid_idx])[::-1]][:top_k]
        
        results = {
            "indices": [int(i) for i in sorted_idx],
            "scores": [float(scores[i]) for i in sorted_idx],
            "metadata": [metadata[i] for i in sorted_idx]
        }
        
        print(f"[TF-IDF] Found {len(results['indices'])} results, top score: {results['scores'][0]:.4f}")
        return results
        
    except Exception as e:
        print(f"[ERROR TF-IDF] {e}")
        import traceback
        traceback.print_exc()
        return {"indices": [], "scores": [], "metadata": []}

# ============================================================
# SBERT SEARCH
# ============================================================
def search_sbert(query, category, top_k=20):
    """SBERT search with natural query"""
    try:
        embeddings = np.load(f"embeddings/{category}_embeddings.npy")
        metadata = load_metadata(category)
        model = get_sbert_model()
        
        print(f"[SBERT] Query: '{query}'")
        
        # Encode query (natural, no preprocessing)
        query_embedding = model.encode([query], convert_to_numpy=True)[0]
        
        # Calculate similarity
        scores = cosine_similarity([query_embedding], embeddings)[0]
        
        # Get top results
        valid_idx = np.where(scores >= SBERT_MIN_SCORE)[0]
        
        if len(valid_idx) == 0:
            print(f"[SBERT] No results found")
            return {"indices": [], "scores": [], "metadata": []}
        
        # Sort by score
        sorted_idx = valid_idx[np.argsort(scores[valid_idx])[::-1]][:top_k]
        
        results = {
            "indices": [int(i) for i in sorted_idx],
            "scores": [float(scores[i]) for i in sorted_idx],
            "metadata": [metadata[i] for i in sorted_idx]
        }
        
        print(f"[SBERT] Found {len(results['indices'])} results, top score: {results['scores'][0]:.4f}")
        return results
        
    except Exception as e:
        print(f"[ERROR SBERT] {e}")
        import traceback
        traceback.print_exc()
        return {"indices": [], "scores": [], "metadata": []}

# ============================================================
# MAIN SEARCH - WITH RELEVANCE FILTERING
# ============================================================
def search(query, category, top_k=10):
    """
    Main search with hybrid scoring and relevance filtering
    """
    try:
        print(f"\n{'='*80}")
        print(f"SEARCH: '{query}' in category '{category}'")
        print(f"{'='*80}")
        
        # Get results from both methods
        tfidf_results = search_tfidf(query, category, top_k=30)
        sbert_results = search_sbert(query, category, top_k=30)
        
        # Combine results
        score_map = {}
        
        # Add TF-IDF scores
        for i, idx in enumerate(tfidf_results["indices"]):
            score_map[idx] = {
                "tfidf_score": tfidf_results["scores"][i],
                "sbert_score": 0.0,
                "metadata": tfidf_results["metadata"][i]
            }
        
        # Add SBERT scores
        for i, idx in enumerate(sbert_results["indices"]):
            if idx not in score_map:
                score_map[idx] = {
                    "tfidf_score": 0.0,
                    "sbert_score": 0.0,
                    "metadata": sbert_results["metadata"][i]
                }
            score_map[idx]["sbert_score"] = sbert_results["scores"][i]
            if score_map[idx]["metadata"] is None:
                score_map[idx]["metadata"] = sbert_results["metadata"][i]
        
        # Calculate final scores with relevance filtering
        final_results = []
        
        for idx, item in score_map.items():
            doc = item["metadata"]
            if doc is None:
                continue
            
            # Calculate relevance score
            relevance = calculate_relevance_score(query, doc)
            
            # REJECT if relevance is too low
            if relevance < 0.1:
                continue
            
            # Calculate base combined score
            base_score = (
                TFIDF_WEIGHT * item["tfidf_score"] + 
                SBERT_WEIGHT * item["sbert_score"]
            )
            
            # Boost with relevance
            final_score = base_score * (1 + relevance)
            
            # Build result
            result_doc = doc.copy()
            result_doc["index"] = int(idx)
            result_doc["tfidf_score"] = float(item["tfidf_score"])
            result_doc["sbert_score"] = float(item["sbert_score"])
            result_doc["relevance_score"] = float(relevance)
            result_doc["combined_score"] = float(final_score)
            
            final_results.append(result_doc)
        
        # Sort by final score
        final_results.sort(key=lambda x: x["combined_score"], reverse=True)
        
        # Limit results
        final_results = final_results[:top_k]
        
        print(f"\n[FINAL] Found {len(final_results)} relevant results")
        if final_results:
            print(f"[FINAL] Top result: {final_results[0].get('Judul', 'N/A')}")
            print(f"[FINAL] Top score: {final_results[0]['combined_score']:.4f}")
        
        return {
            "query": query,
            "category": category,
            "total_results": len(final_results),
            "results": final_results
        }
        
    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        import traceback
        traceback.print_exc()
        return {
            "query": query,
            "category": category,
            "total_results": 0,
            "results": []
        }

# ============================================================
# HELPER - PRINT RESULTS
# ============================================================
def print_results(results, top_n=5):
    """Print search results"""
    print(f"\n{'='*80}")
    print(f"Query: {results['query']}")
    print(f"Category: {results['category']}")
    print(f"Total Results: {results['total_results']}")
    print(f"{'='*80}\n")
    
    for i, doc in enumerate(results['results'][:top_n], 1):
        print(f"{i}. {doc.get('Judul', 'N/A')}")
        print(f"   TF-IDF: {doc['tfidf_score']:.4f} | SBERT: {doc['sbert_score']:.4f}")
        print(f"   Relevance: {doc['relevance_score']:.4f} | Combined: {doc['combined_score']:.4f}")
        print(f"   URL: {doc.get('URL Link', 'N/A')[:60]}...")
        print()

# ============================================================
# TESTING
# ============================================================
if __name__ == "__main__":
    test_queries = [
        ("ikan", "semua"),
        ("ayam bakar", "makanan"),
        ("ayam goreng", "makanan"),
        ("resep soto ayam", "makanan"),
        ("jus segar", "minuman"),
    ]
    
    for query, category in test_queries:
        results = search(query, category, top_k=5)
        print_results(results, top_n=5)
        print("\n" + "="*80 + "\n")