import requests
from bs4 import BeautifulSoup
import csv
import json
import time
import re
import os
from datetime import datetime


class BeritaKulinerCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        # Buat folder dataset jika belum ada
        self.dataset_folder = "dataset"
        if not os.path.exists(self.dataset_folder):
            os.makedirs(self.dataset_folder)
            print(f"✓ Folder '{self.dataset_folder}' berhasil dibuat")

    def clean_content(self, text):
        """Bersihkan konten dari noise dan format dengan baik"""
        noise_patterns = [
            r'Baca [Jj]uga:.*?(?=\n|$)',
            r'ADVERTISEMENT.*?(?=\n|$)',
            r'Simak [Vv]ideo.*?(?=\n|$)',
            r'Saksikan [Vv]ideo.*?(?=\n|$)',
            r'\([A-Z]{2,}/[A-Z]{2,}\)',
            r'SCROLL TO CONTINUE WITH CONTENT',
            r'Loading...',
            r'\[\s*\]',
            r'\(\s*\)',
        ]
        
        for pattern in noise_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n\s*\n', '\n\n', text)
        
        return text.strip()

    def create_description(self, content):
        """Buat ringkasan singkat 1-2 kalimat dari konten"""
        sentences = re.split(r'[.!?]+', content)
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        if len(sentences) >= 2:
            return f"{sentences[0]}. {sentences[1]}."
        elif len(sentences) == 1:
            return f"{sentences[0]}."
        else:
            return content[:150] + "..."

    def validate_url(self, url):
        """Validasi URL bisa diakses"""
        try:
            response = requests.head(url, headers=self.headers, timeout=10, allow_redirects=True)
            return response.status_code == 200
        except:
            return False

    def is_quality_news(self, title, content):
        """Filter berita kuliner berkualitas dengan kriteria lebih ketat"""
        combined = (title + " " + content).lower()
        
        # 1. WAJIB: Minimal panjang konten
        if len(content) < 200:
            return False
        
        # 2. EXCLUDE: Bukan artikel kuliner sama sekali
        non_food_keywords = [
            'politik', 'pemilu', 'pilkada', 'drama korea', 'film bioskop',
            'musik pop', 'konser band', 'laptop gaming', 'smartphone',
            'gadget review', 'sepatu sneakers', 'tas branded', 'fashion show',
            'skincare routine', 'makeup tutorial', 'pertandingan sepak bola',
            'motor sport', 'mobil luxury', 'properti mewah'
        ]
        
        has_strong_non_food = any(keyword in combined for keyword in non_food_keywords)
        
        culinary_context = [
            'makanan', 'minuman', 'kuliner', 'masakan', 'hidangan', 'menu',
            'restoran', 'cafe', 'kafe', 'warung', 'food', 'chef', 'koki',
            'rasa', 'bumbu', 'masak', 'makan', 'sajian'
        ]
        has_culinary = any(word in combined for word in culinary_context)
        
        if has_strong_non_food and not has_culinary:
            return False
        
        # 3. WAJIB ADA: Indikator berita kuliner berkualitas
        quality_indicators = [
            'viral', 'trending', 'heboh', 'ramai', 'booming', 'hits',
            'rekomendasi', 'rekomen', 'review', 'ulasan', 'daftar',
            'deretan', 'sederet', 'tempat makan', 'restoran', 'cafe',
            'kafe', 'kedai', 'warung', 'kuliner khas', 'wisata kuliner',
            'street food', 'jajanan', 'harga', 'diskon', 'promo', 'murah',
            'bisnis kuliner', 'franchise', 'waralaba', 'menu baru',
            'launching', 'grand opening', 'dibuka', 'hadir di', 'ekspansi',
            'chef', 'koki', 'youtuber', 'selebriti', 'artis', 'influencer',
            'festival kuliner', 'pameran kuliner', 'bazar kuliner',
            'kasus', 'kontroversi', 'insiden', 'viral negatif',
            'halal', 'haram', 'mui', 'mengandung babi', 'bakso babi',
            'keracunan', 'bpom', 'ditarik', 'brand makanan',
            'penghargaan', 'award', 'juara', 'rekor', 'prestasi'
        ]
        
        has_news_indicator = any(indicator in combined for indicator in quality_indicators)
        
        if not has_news_indicator:
            return False
        
        # 4. EXCLUDE: Artikel resep lengkap
        recipe_structure = [
            'bahan-bahan:', 'bahan yang dibutuhkan:', 'ingredients:',
            'langkah-langkah:', 'cara membuat:', 'cara pembuatan:'
        ]
        
        recipe_count = sum(1 for pattern in recipe_structure if pattern in combined)
        if recipe_count >= 2:
            return False
        
        # 5. Harus punya konteks kuliner yang jelas
        if not has_culinary:
            return False
        
        return True

    # ===== KOMPAS.COM (TAG) =====
    def get_links_kompas(self, max_pages=15):
        print("\n📰 KOMPAS - Mengambil Link dari Tag Kuliner...")
        links = []
        
        for page in range(1, max_pages + 1):
            try:
                url = f"https://www.kompas.com/tag/kuliner?page={page}"
                print(f"   Scraping: {url}")
                response = requests.get(url, headers=self.headers, timeout=15)
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Cari semua link artikel
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    # Filter link artikel kompas.com
                    if "kompas.com" in href and "/read/" in href:
                        if href not in links:
                            links.append(href)
                
                print(f"   Halaman {page}: Total {len(links)} link terkumpul")
                time.sleep(2)
            except Exception as e:
                print(f"   Error halaman {page}: {e}")
        
        return links

    def scrape_kompas(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Title
            title = ""
            h1 = soup.find("h1", class_="read__title")
            if not h1:
                h1 = soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)
            
            # Date
            date = ""
            date_elem = soup.find("div", class_="read__time")
            if not date_elem:
                date_elem = soup.find("time")
            if date_elem:
                date_text = date_elem.get_text(strip=True)
                # Coba parse tanggal ke format YYYY-MM-DD
                try:
                    # Contoh: "14/11/2025, 10:30 WIB" -> "2025-11-14"
                    date_parts = date_text.split(',')[0].split('/')
                    if len(date_parts) == 3:
                        date = f"{date_parts[2]}-{date_parts[1].zfill(2)}-{date_parts[0].zfill(2)}"
                    else:
                        date = date_text
                except:
                    date = date_text
            
            # Image
            image_url = ""
            og_image = soup.find("meta", property="og:image")
            if og_image:
                image_url = og_image.get("content", "")
            
            # Content - Pisahkan per paragraf
            paragraphs = []
            content_div = soup.find("div", class_="read__content")
            if content_div:
                for p in content_div.find_all("p"):
                    text = p.get_text(strip=True)
                    text = self.clean_content(text)
                    if len(text) > 20:  # Filter paragraf pendek
                        paragraphs.append(text)
            
            # Gabungkan untuk deskripsi
            full_content = " ".join(paragraphs)
            description = self.create_description(full_content)
            
            return {
                "title": title,
                "date": date,
                "description": description,
                "paragraphs": paragraphs,
                "url": url,
                "image_url": image_url
            }
        except Exception as e:
            print(f"      Error scraping: {e}")
            return None

    def save_to_json(self, articles, filename="berita_kuliner.json"):
        """Simpan ke JSON dengan format custom"""
        filepath = os.path.join(self.dataset_folder, filename)
        
        json_data = []
        for idx, article in enumerate(articles, 1):
            json_data.append({
                "id": idx,
                "type": "berita",
                "judul": article["title"],
                "tanggal": article["date"],
                "kategori": "berita",
                "deskripsi": article["description"],
                "url_gambar": article["image_url"],
                "url_link": article["url"],
                "isi": article["paragraphs"]
            })
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        print(f"✓ File JSON disimpan: {filepath}")
        return filepath

    def save_to_csv(self, articles, filename="berita_kuliner.csv"):
        """Simpan ke CSV dengan format custom"""
        filepath = os.path.join(self.dataset_folder, filename)
        
        with open(filepath, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow([
                "id", "type", "judul", "tanggal", "kategori", 
                "deskripsi", "url_gambar", "url_link", "isi"
            ])
            
            # Data
            for idx, article in enumerate(articles, 1):
                # Gabungkan paragraf dengan separator ||| untuk CSV
                isi_gabungan = " ||| ".join(article["paragraphs"])
                
                writer.writerow([
                    idx,
                    "berita",
                    article["title"],
                    article["date"],
                    "berita",
                    article["description"],
                    article["image_url"],
                    article["url"],
                    isi_gabungan
                ])
        
        print(f"✓ File CSV disimpan: {filepath}")
        return filepath

    def crawl(self, target=100):
        print("=" * 80)
        print("CRAWLER BERITA KULINER")
        print("=" * 80)
        print("SUMBER BERITA:")
        print("  ✓ Kompas.com/tag/kuliner")
        print("=" * 80)
        print(f"Target: {target} berita berkualitas")
        print(f"Output: Folder '{self.dataset_folder}' (CSV + JSON)")
        print("=" * 80)
        
        articles = []
        
        sources = [
            ("Kompas", self.get_links_kompas, self.scrape_kompas, 15),
        ]
        
        for source_name, get_links, scrape_func, max_pages in sources:
            if len(articles) >= target:
                break
            
            print(f"\n{'='*80}")
            print(f"🔗 SUMBER: {source_name}")
            print(f"{'='*80}")
            
            links = get_links(max_pages=max_pages)
            print(f"Berhasil mengumpulkan {len(links)} link dari {source_name}")
            
            for idx, url in enumerate(links, 1):
                if len(articles) >= target:
                    break
                
                print(f"\n[{source_name} - {idx}/{len(links)}] Memproses artikel...")
                print(f"   URL: {url[:75]}...")
                
                article = scrape_func(url)
                if not article or not article["title"] or len(article["paragraphs"]) == 0:
                    print("   ✗ Data tidak lengkap atau terlalu pendek")
                    continue
                
                full_content = " ".join(article["paragraphs"])
                
                # Filter berita berkualitas
                if self.is_quality_news(article["title"], full_content):
                    articles.append(article)
                    print(f"   ✓ BERITA BERKUALITAS #{len(articles)}")
                    print(f"   {article['title'][:70]}...")
                else:
                    print("   ✗ Tidak memenuhi kriteria berita berkualitas")
                
                time.sleep(1)
        
        # Simpan hasil
        print(f"\n{'='*80}")
        print("MENYIMPAN HASIL...")
        print(f"{'='*80}")
        
        # Simpan ke JSON
        self.save_to_json(articles)
        
        # Simpan ke CSV
        self.save_to_csv(articles)
        
        print(f"\n{'='*80}")
        print("SELESAI!")
        print(f"{'='*80}")
        print(f"Total Berita Berkualitas: {len(articles)}")
        print(f"Lokasi File: ./{self.dataset_folder}/")
        print(f"  - berita_kuliner.json")
        print(f"  - berita_kuliner.csv")
        print(f"{'='*80}")
        
        # Statistik per sumber
        print("\n📊 STATISTIK PER SUMBER:")
        for source_name, _, _, _ in sources:
            count = sum(1 for a in articles if source_name.lower() in a["url"].lower())
            print(f"   {source_name}: {count} berita")
        print(f"{'='*80}")


if __name__ == "__main__":
    crawler = BeritaKulinerCrawler()
    crawler.crawl(target=100)