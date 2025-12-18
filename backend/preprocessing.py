import os
import json
import re
import pandas as pd
import emoji
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory

# =====================
# PATH
# =====================
DATASET_DIR = "dataset"
TOKENS_DIR = "tokens"
METADATA_DIR = "metadata"

os.makedirs(TOKENS_DIR, exist_ok=True)
os.makedirs(METADATA_DIR, exist_ok=True)

# =====================
# NLP SETUP
# =====================
stemmer = StemmerFactory().create_stemmer()
stopwords = set(StopWordRemoverFactory().get_stop_words())

# =====================
# CLEANING FUNCTIONS
# =====================
def clean_text_basic(text):
    text = str(text)
    text = emoji.replace_emoji(text, replace="")
    text = re.sub(r"http\S+", "", text)
    text = re.sub(r"Kompas\.com", "", text, flags=re.I)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def clean_berita(text):
    text = clean_text_basic(text)

    ads_patterns = [
        r"Baca juga.*",
        r"ADVERTISEMENT.*",
        r"Scroll to Continue.*",
        r"Simak berita lainnya.*",
        r"\(adsbygoogle.*?\)"
    ]

    for p in ads_patterns:
        text = re.sub(p, "", text, flags=re.I)

    sentences = [s.strip() for s in text.split(". ") if len(s.strip()) > 40]
    return "\n\n".join(sentences)

def tokenize_text(text):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    tokens = text.split()
    tokens = [t for t in tokens if t not in stopwords and len(t) > 2]
    tokens = [stemmer.stem(t) for t in tokens]
    return tokens

# =====================
# COLLECT ALL TEXT (INI KUNCI FIX TOKEN)
# =====================
def collect_all_text(item):
    texts = []
    for _, value in item.items():
        if isinstance(value, str):
            texts.append(value)
    return " ".join(texts)

# =====================
# MAIN PROCESS
# =====================
def process_category(filename, kategori):
    path = os.path.join(DATASET_DIR, filename)

    # Load data
    if filename.endswith(".csv"):
        df = pd.read_csv(path)
        data = df.fillna("").to_dict(orient="records")
    else:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)

    tokens_output = []
    metadata_output = []

    for i, item in enumerate(data):
        # ===== METADATA =====
        content_meta = (
            item.get("Isi Berita")
            or item.get("Deskripsi")
            or item.get("Isi")
            or ""
        )

        if kategori == "berita":
            content_clean = clean_berita(content_meta)
        else:
            content_clean = clean_text_basic(content_meta)

        meta = item.copy()
        meta["Isi Berita"] = content_clean
        meta["kategori"] = kategori
        metadata_output.append(meta)

        # ===== TOKENS (AMBIL SEMUA KOLOM) =====
        raw_text = collect_all_text(item)
        raw_text = clean_text_basic(raw_text)
        tokens = tokenize_text(raw_text)

        tokens_output.append({
            "index": i,
            "tokens": tokens,
            "tokens_joined": " ".join(tokens)
        })

    # Save tokens
    with open(f"{TOKENS_DIR}/{kategori}_tokens.json", "w", encoding="utf-8") as f:
        json.dump(tokens_output, f, ensure_ascii=False, indent=2)

    # Save metadata
    with open(f"{METADATA_DIR}/{kategori}.json", "w", encoding="utf-8") as f:
        json.dump(metadata_output, f, ensure_ascii=False, indent=2)

    print(f"✅ {kategori} selesai | total data: {len(data)}")

# =====================
# RUN ALL
# =====================
process_category("berita_kuliner.csv", "berita")
process_category("resep_makanan.csv", "makanan")
process_category("resep_minuman.csv", "minuman")
process_category("resep_sehat.csv", "sehat")
process_category("semua.csv", "semua")

print("\n🎉 SEMUA PREPROCESSING BERHASIL")
