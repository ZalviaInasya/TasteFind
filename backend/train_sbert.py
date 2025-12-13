import json
import numpy as np
import os
from sentence_transformers import SentenceTransformer

CATEGORIES = ["makanan", "minuman", "sehat", "berita", "semua"]

# Load pre-trained multilingual SBERT model
# Model ini lebih baik untuk Indonesian text
model = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

def load_original_text(cat):
    """
    Load original text (BUKAN tokens) untuk SBERT embeddings.
    SBERT memerlukan natural language text, bukan tokenized text.
    PENTING: Concatenate Judul + Isi agar semantic context lengkap!
    """
    json_path = f"backend/metadata/{cat}.json"
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    # Extract original content dengan CONCATENATION Judul + Isi
    docs = []
    for item in data:
        # Get judul
        judul = item.get("Judul") or item.get("Judul Resep", "")
        
        # Get isi
        if "Isi Berita" in item and item["Isi Berita"]:
            isi = item["Isi Berita"]
        elif "Isi Resep" in item and item["Isi Resep"]:
            isi = item["Isi Resep"]
        else:
            isi = ""
        
        # CONCATENATE: "[Judul] [Isi]" untuk semantic lengkap
        text = f"{judul} {isi}".strip()
        
        if not text:
            text = "unknown"
        
        docs.append(text)
    
    return docs

def train_sbert():
    # Create output directory jika belum ada
    os.makedirs("backend/embeddings", exist_ok=True)
    
    for cat in CATEGORIES:
        print(f"\n{'='*60}")
        print(f"Generating SBERT embeddings for {cat}")
        print(f"{'='*60}")

        docs = load_original_text(cat)
        print(f"Total documents: {len(docs)}")
        print(f"Processing embeddings (this may take a while)...")
        
        # Generate embeddings dari original text (natural language)
        embeddings = model.encode(docs, show_progress_bar=True, convert_to_numpy=True)
        print(f"Embeddings shape: {embeddings.shape}")

        # Simpan embeddings
        np.save(f"backend/embeddings/{cat}_embeddings.npy", embeddings)

        print(f"✓ Saved SBERT embeddings for {cat}")
        print(f"  - Embeddings: backend/embeddings/{cat}_embeddings.npy")

if __name__ == "__main__":
    print("Starting SBERT embeddings generation...")
    train_sbert()
    print("\n" + "="*60)
    print("SBERT Training Complete!")
    print("="*60)