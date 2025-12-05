import pandas as pd
import json
import re
import string
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
import os
import hashlib
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
import nltk

# ---------- Inisialisasi ----------
stemmer = StemmerFactory().create_stemmer()
sw_remover = StopWordRemoverFactory().create_stop_word_remover()

# Pastikan punkt & stopwords NLTK tersedia
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    try:
        nltk.download("punkt")
    except:
        pass

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    try:
        nltk.download("stopwords")
    except:
        pass

# Gabungkan stopword Sastrawi + NLTK Indonesian stopwords
nltk_id_stop = set()
try:
    nltk_id_stop = set(stopwords.words("indonesian"))
except:
    nltk_id_stop = set()

combined_stopwords = set()
combined_stopwords |= nltk_id_stop
# Tambahkan stopword ekstra HTML artifacts
combined_stopwords |= set([
    'nbsp', 'amp', 'quot', 'gt', 'lt', 'www', 'http', 'https', 'com', 'id', 'html'
])

# Daftar kata penting yang TIDAK boleh di-stem (kata kunci kuliner, tempat, dll)
PROTECTED_WORDS = {
    'indonesia', 'indonesian', 'jakarta', 'bali', 'surabaya', 'bandung',
    'kuliner', 'culinary', 'restaurant', 'restoran', 'chef', 'menu',
    'makanan', 'minuman', 'resep', 'masakan', 'hidangan',
    'award', 'awards', 'festival', 'event', 'kompetisi',
    'nasi', 'goreng', 'ayam', 'sate', 'rendang', 'soto', 'gado', 'bakso',
    'sambal', 'rica', 'bumbu', 'rempah', 'pedas', 'manis', 'asin', 'gurih',
    'world', 'best', 'top', 'destination', 'asia', 'asian', 'global', 'international',
    'modern', 'tradisional', 'khas', 'authentic', 'fusion',
    'kota', 'city', 'kawasan', 'daerah', 'wilayah', 'negara',
    'gelar', 'juara', 'pemenang', 'nominasi', 'penghargaan'
}

# ============================================================
# FUNGSI BANTU PEMBERSIHAN TEXT (DIPERBAIKI)
# ============================================================

def clean_text(text):
    """
    Normalisasi teks dengan lebih hati-hati:
    - Jangan pecah kata yang sudah benar
    - Hapus noise tapi pertahankan struktur kata
    """
    if pd.isna(text):
        return ""

    text = str(text)

    # Hapus HTML entities
    text = re.sub(r'&[a-z]+;', ' ', text)
    text = re.sub(r'<[^>]+>', ' ', text)  # Hapus HTML tags
    
    # lowercase
    text = text.lower()

    # Pisahkan angka dari huruf HANYA jika jelas terpisah (contoh: "2024indonesia" -> "2024 indonesia")
    text = re.sub(r'(\d)([a-z])', r'\1 \2', text)
    text = re.sub(r'([a-z])(\d)', r'\1 \2', text)

    # Ganti tanda baca dengan spasi tapi pertahankan kata utuh
    text = text.translate(str.maketrans(string.punctuation, ' ' * len(string.punctuation)))

    # Hapus URL remnants
    text = re.sub(r'\b(www|http|https)\b', ' ', text)
    
    # Hapus angka yang berdiri sendiri
    text = re.sub(r'\b\d+\b', ' ', text)

    # Rapikan spasi berlebih
    text = re.sub(r'\s+', ' ', text).strip()

    return text


def tokenize(text):
    """
    Tokenize dengan word_tokenize, filter token yang valid
    """
    if not text:
        return []
    try:
        toks = word_tokenize(text)
    except Exception:
        toks = text.split()
    
    # Filter: harus punya huruf, minimal 3 karakter, maksimal 30 karakter
    valid_tokens = []
    for t in toks:
        # Skip jika tidak ada huruf sama sekali
        if not re.search('[a-zA-Z]', t):
            continue
        # Skip jika terlalu pendek atau terlalu panjang
        if len(t) < 3 or len(t) > 30:
            continue
        # Skip jika mayoritas bukan huruf (lebih dari 50% angka/simbol)
        letter_count = sum(c.isalpha() for c in t)
        if letter_count < len(t) * 0.5:
            continue
        
        valid_tokens.append(t)
    
    return valid_tokens


def remove_stopwords(tokens):
    """
    Hapus stopwords dengan lebih selektif
    """
    if not tokens:
        return []
    
    # Filter stopwords tapi pertahankan kata penting
    filtered = []
    for t in tokens:
        # Skip stopword kecuali kata tersebut protected
        if t in combined_stopwords and t not in PROTECTED_WORDS:
            continue
        filtered.append(t)
    
    # Gunakan Sastrawi sebagai tahap kedua
    text = " ".join(filtered)
    try:
        text_after = sw_remover.remove(text)
        # Split hasil dan filter lagi
        result = []
        for t in text_after.split():
            if len(t) >= 3:  # Minimal 3 huruf setelah stopword removal
                result.append(t)
        return result
    except Exception:
        return filtered


def smart_stemming(tokens):
    """
    Stemming yang lebih pintar - jangan stem kata yang sudah benar atau protected
    """
    if not tokens:
        return []
    
    result = []
    for token in tokens:
        # Jangan stem kata protected atau kata asing yang sudah benar
        if token in PROTECTED_WORDS:
            result.append(token)
            continue
        
        # Jangan stem kata yang terlalu pendek (kemungkinan sudah root word)
        if len(token) <= 4:
            result.append(token)
            continue
        
        # Stem kata lainnya
        try:
            stemmed = stemmer.stem(token)
            # Validasi hasil stemming: jika hasil terlalu pendek (< 3 huruf), 
            # kembalikan kata asli
            if len(stemmed) < 3:
                result.append(token)
            else:
                result.append(stemmed)
        except Exception:
            result.append(token)
    
    return result


def filter_tokens(tokens):
    """
    Filter final untuk memastikan kualitas token
    """
    hasil = []
    for t in tokens:
        if not t:
            continue
        # Minimal 3 huruf, maksimal 30 huruf
        if len(t) < 3 or len(t) > 30:
            continue
        # Harus punya huruf
        if not re.search('[a-zA-Z]', t):
            continue
        # Skip token yang terdiri dari karakter berulang (aaa, bbb, dll)
        if len(set(t)) <= 2 and len(t) > 3:
            continue
        
        hasil.append(t)
    
    return hasil


def aggregate_tokens_frequency(tokens):
    """
    Return list token unik diurutkan berdasarkan frekuensi turun
    """
    if not tokens:
        return []
    freq = {}
    for t in tokens:
        freq[t] = freq.get(t, 0) + 1
    # Urut berdasarkan frekuensi desc lalu alfabet asc
    sorted_tokens = sorted(freq.items(), key=lambda x: (-x[1], x[0]))
    return [t for t, _ in sorted_tokens]


# ============================================================
# Preprocess helpers
# ============================================================
def preprocess_text(text):
    """Pipeline lengkap untuk preprocessing teks"""
    c = clean_text(text)
    toks = tokenize(c)
    toks = remove_stopwords(toks)
    toks = smart_stemming(toks)
    toks = filter_tokens(toks)
    return " ".join(toks)


def tokenize_document(text):
    """
    Kembalikan daftar token yang sudah dibersihkan, distem, 
    lalu diagregasi menjadi daftar unik terurut berdasarkan frekuensi
    """
    if pd.isna(text) or not text:
        return []

    c = clean_text(text)
    toks = tokenize(c)
    toks = remove_stopwords(toks)
    toks = smart_stemming(toks)
    toks = filter_tokens(toks)
    # Aggregate menjadi token unik yang diurutkan frekuensi
    uniq_sorted = aggregate_tokens_frequency(toks)
    return uniq_sorted


# ============================================================
# CSV -> JSON (STRUKTUR PATH TIDAK DIUBAH)
# ============================================================
def csv_to_json(input_csv, output_json, kategori):
    print(f"Memproses: {input_csv}")

    if not os.path.exists(input_csv):
        print(f"  - ERROR: File CSV {input_csv} tidak ditemukan.")
        return

    # Baca CSV
    df = pd.read_csv(input_csv, sep=';', engine='python', on_bad_lines='skip')
    df_orig = df.copy()

    # Kolom teks yang ingin diproses dengan pipeline 'full'
    text_columns = ['Isi Berita', 'Isi Resep', 'deskripsi', 'resep', 'isi']
    # Kolom yang dilewati preprocessing
    skip_preprocessing = ['Judul', 'Judul Resep', 'URL Link', 'URL Gambar', 'Tanggal']

    # Normalisasi nama kolom dan proses
    for col in df.columns:
        if col in skip_preprocessing:
            continue
        col_lower = col.lower()
        if col in text_columns or any(x in col_lower for x in ['judul', 'isi', 'deskripsi', 'resep']):
            df[col] = df[col].astype(str).apply(preprocess_text)
        else:
            df[col] = df[col].astype(str).apply(clean_text)

    df["kategori"] = kategori
    records = df.to_dict(orient="records")

    # Tambahkan token asli untuk keperluan tokens.json dan .txt
    for i, rec in enumerate(records):
        raw_text = ""
        for cand in ['Isi Resep', 'Isi Berita', 'deskripsi', 'resep', 'isi']:
            if cand in df_orig.columns:
                temp = str(df_orig.iloc[i].get(cand, ""))
                if temp and temp.strip():
                    raw_text = temp
                    break
        tokens = tokenize_document(raw_text)
        rec['tokens'] = tokens
        rec['tokens_joined'] = ' '.join(tokens)

    # ========== SAVE JSON (TANPA TOKENS) ==========
    # Buat copy records tanpa field tokens
    records_without_tokens = []
    for rec in records:
        rec_clean = {k: v for k, v in rec.items() if k not in ['tokens', 'tokens_joined']}
        records_without_tokens.append(rec_clean)

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(records_without_tokens, f, ensure_ascii=False, indent=2)

    # ========== SAVE TOKENS JSON ==========
    os.makedirs("backend/tokens", exist_ok=True)
    tokens_out = [{
        "index": i,
        "tokens": rec.get("tokens", []),
        "tokens_joined": rec.get("tokens_joined", "")
    } for i, rec in enumerate(records)]
    with open(f"backend/tokens/{kategori}_tokens.json", "w", encoding="utf-8") as tf:
        json.dump(tokens_out, tf, ensure_ascii=False, indent=2)

    # ========== SAVE TOKEN TXT ==========
    prep_root = "backend/preprocessing"
    os.makedirs(prep_root, exist_ok=True)
    cat_dir = os.path.join(prep_root, kategori)
    os.makedirs(cat_dir, exist_ok=True)

    used_names = set()
    for i, rec in enumerate(records):
        title = ""
        for tkey in ['Judul Resep', 'Judul', 'Judul Berita']:
            if tkey in rec and rec.get(tkey):
                title = str(rec.get(tkey))
                break

        safe_title = re.sub(r'[^A-Za-z ]', '', title or '').strip()
        safe_title = re.sub(r'\s+', '_', safe_title)[:60].lower()

        if not safe_title:
            h = hashlib.sha1((rec.get('tokens_joined','') or '').encode('utf-8')).hexdigest()[:8]
            safe_title = f"untitled_{h}"

        base_name = safe_title
        counter = 1
        while safe_title in used_names:
            safe_title = f"{base_name}_{counter}"
            counter += 1
        used_names.add(safe_title)

        out_path = os.path.join(cat_dir, f"{safe_title}.txt")
        try:
            with open(out_path, 'w', encoding='utf-8') as cf:
                toks = rec.get('tokens', [])
                if toks:
                    for tok in toks:
                        cf.write(tok + '\n')
                else:
                    cf.write(rec.get('tokens_joined', ''))
        except Exception:
            with open(out_path, 'w', encoding='utf-8', errors='ignore') as cf:
                cf.write(rec.get('tokens_joined', ''))

    print(f"✓ Selesai → {output_json} ({len(df)} baris)\n")


# ============================================================
# MAIN
# ============================================================
if _name_ == "_main_":
    print("=" * 60)
    print("PREPROCESSING DATASET UNTUK TASTEFIND (VERSI DIPERBAIKI)")
    print("=" * 60)
    print()

    csv_to_json("backend/dataset/resep_makanan.csv", "backend/dataset/makanan.json", "makanan")
    csv_to_json("backend/dataset/resep_sehat.csv", "backend/dataset/sehat.json", "sehat")
    csv_to_json("backend/dataset/resep_minuman.csv", "backend/dataset/minuman.json", "minuman")
    csv_to_json("backend/dataset/berita_kuliner.csv", "backend/dataset/berita.json", "berita")
    csv_to_json("backend/dataset/semua.csv", "backend/dataset/semua.json", "semua")

    print("=" * 60)
    print("PREPROCESSING SELESAI!")
    print("=" * 60)