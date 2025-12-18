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

    Perubahan penting:
    - Untuk kategori resep (makanan, minuman, sehat) -> gunakan `Bahan` + `Langkah` jika ada
    - Untuk `berita` -> gunakan `Isi` (atau `Isi Berita` / `isi`)
    - Untuk `semua` -> deteksi berdasarkan field `type` / `kategori` pada item

    Fungsi ini juga lebih toleran terhadap variasi key pada metadata ("Judul" vs "judul",
    "Bahan" sebagai string yang dipisah dengan "|" vs list, "Isi Berita" vs "isi", dll.).
    """
    import re

    json_path = f"metadata/{cat}.json"

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        print(f"Warning: metadata file not found: {json_path}")
        return []

    def _get(item, *keys):
        for k in keys:
            if k in item and item[k] not in (None, ""):
                return item[k]
        return ""

    def _flatten(value):
        # Convert lists to string and split strings with common delimiters
        if isinstance(value, list):
            return " ".join([str(x).strip() for x in value if str(x).strip()])
        if isinstance(value, str):
            # remove simple HTML tags if present
            s = re.sub(r'<[^>]+>', ' ', value)
            parts = [p.strip() for p in re.split(r"\||\n|;|\\.|\r", s) if p.strip()]
            return " ".join(parts)
        return ""

    docs = []
    unknown_count = 0

    for item in data:
        judul = _get(item, "Judul", "judul", "title")
        deskripsi = _get(item, "Deskripsi", "deskripsi", "description")

        # Detect type/kategori on item for 'semua' handling
        raw_type = _get(item, "type", "kategori", "category", "jenis")
        item_type = raw_type.lower() if isinstance(raw_type, str) else ""

        # Decide which fields to use based on category
        content = ""
        if cat in ("makanan", "minuman", "sehat"):
            bahan_field = _get(item, "Bahan", "bahan", "Ingredients", "ingredients")
            langkah_field = _get(item, "Langkah", "langkah", "Langkah", "Steps", "steps")

            bahan = _flatten(bahan_field)
            langkah = _flatten(langkah_field)

            if bahan or langkah:
                content = f"{bahan} {langkah}".strip()
            else:
                # fallback to generic content fields
                isi_field = _get(item, "Isi Resep", "Isi Berita", "isi", "Isi", "content")
                content = _flatten(isi_field) or _flatten(deskripsi)
        elif cat == "berita":
            isi_field = _get(item, "Isi Berita", "isi", "Isi", "content", "Isi_Berita")
            content = _flatten(isi_field) or _flatten(deskripsi)
        else:  # cat == 'semua' -> inspect item type
            if "berita" in item_type or "news" in item_type:
                isi_field = _get(item, "Isi Berita", "isi", "Isi", "content", "Isi_Berita")
                content = _flatten(isi_field) or _flatten(deskripsi)
            else:
                # assume recipe-like
                bahan_field = _get(item, "Bahan", "bahan", "Ingredients", "ingredients")
                langkah_field = _get(item, "Langkah", "langkah", "Langkah", "Steps", "steps")

                bahan = _flatten(bahan_field)
                langkah = _flatten(langkah_field)

                if bahan or langkah:
                    content = f"{bahan} {langkah}".strip()
                else:
                    isi_field = _get(item, "Isi Resep", "Isi Berita", "isi", "Isi", "content")
                    content = _flatten(isi_field) or _flatten(deskripsi)

        # Combine with safe punctuation and strip excessive whitespace
        parts = [p.strip() for p in [judul, deskripsi, content] if p and p.strip()]
        text = ". ".join(parts)

        if not text:
            unknown_count += 1
            docs.append("unknown")
        else:
            docs.append(text)

    if unknown_count:
        print(f"[INFO] {unknown_count} documents lacked usable text and were filled with 'unknown'")

    return docs

def train_sbert():
    # Create output directory jika belum ada
    os.makedirs("embeddings", exist_ok=True)
    
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
        np.save(f"embeddings/{cat}_embeddings.npy", embeddings)

        print(f"✓ Saved SBERT embeddings for {cat}")
        print(f"  - Embeddings: embeddings/{cat}_embeddings.npy")

if __name__ == "__main__":
    print("Starting SBERT embeddings generation...")
    train_sbert()
    print("\n" + "="*60)
    print("SBERT Training Complete!")
    print("="*60)