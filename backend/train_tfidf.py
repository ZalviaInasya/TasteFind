import json
import pickle
import numpy as np
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import save_npz

CATEGORIES = ["makanan", "minuman", "sehat", "berita", "semua"]

def simple_tokenizer(text):
    """Simple tokenizer yang bisa di-pickle"""
    return text.split()

def load_json_file(cat):
    """Load JSON file dan extract tokens_joined untuk TF-IDF"""
    json_path = f"backend/dataset/{cat}.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Extract tokens_joined dari setiap dokumen
    # tokens_joined sudah berupa string dengan tokens yang dipisahkan spasi
    docs = []
    for item in data:
        tokens_text = item.get("tokens_joined", "")
        if tokens_text:
            docs.append(tokens_text)
    
    return docs

def train_tfidf():
    # Create output directory jika belum ada
    os.makedirs("backend/tfidf", exist_ok=True)
    
    for cat in CATEGORIES:
        print(f"\n{'='*60}")
        print(f"Training TF-IDF for category: {cat}")
        print(f"{'='*60}")

        docs = load_json_file(cat)
        print(f"Total documents: {len(docs)}")

        vectorizer = TfidfVectorizer(
            tokenizer=simple_tokenizer,       # Gunakan custom tokenizer (pickle-able)
            preprocessor=None,                # Jangan pre-process ulang
            lowercase=False,                  # Tokens sudah lowercase saat preprocessing
            max_features=5000,
            ngram_range=(1, 2)
        )

        matrix = vectorizer.fit_transform(docs)
        print(f"TF-IDF matrix shape: {matrix.shape}")
        print(f"Vocabulary size: {len(vectorizer.get_feature_names_out())}")

        # Simpan vectorizer
        with open(f"backend/tfidf/{cat}_vectorizer.pkl", "wb") as f:
            pickle.dump(vectorizer, f)

        # Simpan matrix TF-IDF
        save_npz(f"backend/tfidf/{cat}_matrix.npz", matrix)

        print(f"✓ Saved TF-IDF model for {cat}")
        print(f"  - Vectorizer: backend/tfidf/{cat}_vectorizer.pkl")
        print(f"  - Matrix: backend/tfidf/{cat}_matrix.npz")

if __name__ == "__main__":
    print("Starting TF-IDF model training...")
    train_tfidf()
    print("\n" + "="*60)
    print("TF-IDF Training Complete!")
    print("="*60)
