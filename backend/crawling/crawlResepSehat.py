import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
import json
import time
import re
import os
import random

class ResepSehatCrawler:
    def __init__(self, use_selenium=True):
        self.use_selenium = use_selenium
        self.driver = None 
        
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        # Buat folder dataset
        self.dataset_folder = "dataset"
        if not os.path.exists(self.dataset_folder):
            os.makedirs(self.dataset_folder)
            
        # Keyword Header
        self.bahan_header_keywords = [
            'bahan-bahan', 'bahan:', 'bahan utama', 'resep bahan', 'komposisi',
            'bahan isian', 'bahan bumbu', 'bahan pelengkap', 'bahan rebusan',
            'bahan jamu', 'bahan ramuan', 'bahan rempah', 'bahan sayur'
        ]
        
        self.langkah_header_keywords = [
            'cara membuat', 'cara memasak', 'langkah-langkah', 'langkah pembuatan', 
            'cara mengolah', 'instruksi', 'urutan', 'cara bikin', 'cara meracik',
            'cara penyajian', 'cara konsumsi'
        ]
        
        # Blacklist Konten Sampah
        self.content_blacklist = [
            'baca juga', 'simak video', 'berita foto', 'kunjungi', 'klik tautan',
            'copyright', 'advertisement', 'promoted', 'shopee', 'tokopedia',
            'beli di sini', 'promo', 'diskon', 'sumber:', 'penulis:', 'editor:',
            'kompas.com', 'dapatkan informasi', 'whatsapp', 'telegram',
            'artikel kompas.id', 'lihat foto', 'buka gambar', 'baca berita',
            'selanjutnya', 'halaman', 'picu', 'tuduhan', 'malapraktik'
        ]

        if self.use_selenium:
            self.setup_selenium()

    def setup_selenium(self):
        try:
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--window-size=1920,1080")
            chrome_options.add_argument(f"user-agent={self.headers['User-Agent']}")
            chrome_options.add_experimental_option("prefs", {
                "profile.default_content_setting_values.notifications": 2
            })
            self.driver = webdriver.Chrome(options=chrome_options)
            print("   ✅ Selenium WebDriver initialized")
        except Exception as e:
            print(f"   ⚠️  Selenium setup failed: {e}")
            self.use_selenium = False
            self.driver = None

    def clean_text(self, text):
        if not text: return ""
        text = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F\x7F-\x9F]', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def clean_leading_number(self, text):
        return re.sub(r'^\s*\d+[\.\)\-]\s*', '', text).strip()

    def format_date(self, date_str):
        try:
            match = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', date_str)
            if match:
                day, month, year = match.groups()
                return f"{day}-{month}-{year}"
            return date_str
        except: return date_str

    # --- FILTER SUPER KETAT (MEDIS & DIET) ---
    def is_strictly_healthy(self, title):
        t = title.lower()
        
        # 1. JUDUL WAJIB MENGANDUNG SALAH SATU KATA INI (Whitelist)
        must_have_keywords = [
            # Kategori Penyakit/Medis
            'kolesterol', 'diabetes', 'asam urat', 'darah tinggi', 'hipertensi',
            'jantung', 'flu', 'batuk', 'masuk angin', 'sakit kepala', 'nyeri',
            'imun', 'daya tahan', 'redakan', 'atasi', 'sembuhkan', 'obat',
            
            # Kategori Diet/Metode Sehat
            'diet', 'rendah kalori', 'low carb', 'tanpa minyak', 'tanpa santan',
            'kukus', 'rebus', 'pepes', 'panggang', 'tim', 'bening',
            'vegetarian', 'vegan', 'sehat', 'detox',
            
            # Kategori Herbal
            'jamu', 'wedang', 'ramuan', 'herbal', 'rimpang', 'empon',
            'jahe', 'kunyit', 'kencur', 'temulawak', 'sereh'
        ]
        
        # Jika tidak ada satupun kata sakti di atas -> SKIP
        if not any(k in t for k in must_have_keywords):
            return False
            
        # 2. BLACKLIST METODE TIDAK SEHAT
        # Tolak jika ada kata "Goreng", "Santan", "Crispy" 
        # KECUALI ada kata penawar "Tanpa", "Bukan", "Sehat"
        bad_keywords = ['goreng', 'santan', 'crispy', 'krispi', 'lemak', 'gajih', 'jeroan', 'kulit ayam']
        
        for bad in bad_keywords:
            if bad in t:
                # Cek penawar
                if any(good in t for good in ['tanpa', 'no', 'non', 'rendah', 'sehat', 'diet', 'bukan']):
                    continue # Lolos (misal: "Ayam Goreng Tanpa Minyak")
                return False # Ditolak (misal: "Ayam Goreng Crispy")

        return True

    def is_listicle_or_compilation(self, title):
        t = title.lower()
        if re.match(r'^\s*[2-9]\d*\s+', t) or re.match(r'^\s*1\d+\s+', t): 
             return True
        compilation_words = ['kumpulan', 'daftar', 'rekomendasi', 'aneka', 'variasi', 'serba', 'gerai', 'promo']
        if any(w in t for w in compilation_words): return True
        return False

    def is_header(self, text, keywords):
        text_lower = text.lower()
        if len(text) > 50: return False 
        return any(k in text_lower for k in keywords)

    def is_step_numbered(self, text):
        return bool(re.match(r'^\s*\d+[\.\)\-]', text))

    def is_valid_ingredient(self, text):
        """Validasi Bahan: Bersih dari Iklan"""
        t_lower = text.lower()
        if any(x in t_lower for x in self.content_blacklist): return False
        
        start_blacklist = ['resep', 'cara', 'tips', 'manfaat', 'baca', 'simak', 'lihat', 'artikel', 'news', 'foto', 'video']
        if any(t_lower.startswith(x + ' ') for x in start_blacklist): return False
        
        if '”' in text or '“' in text or '"' in text: return False
        if "?" in text or "!" in text: return False
        if len(text) > 120: return False

        units = [
            'gr', 'gram', 'kg', 'sdm', 'sdt', 'ml', 'liter', 'buah', 
            'batang', 'lembar', 'potong', 'iris', 'secukupnya',
            'sendok', 'cup', 'gelas', 'cangkir', 'sachet', 'bungkus',
            'siung', 'cm', 'paket', 'ikat', 'genggam', 'ruas', 'rimpang', 
            'jari', 'jempol', 'telunjuk', 'kencur', 'jahe', 'kunyit', 'butir'
        ]
        
        has_unit = any(u in t_lower for u in units)
        has_digit = any(c.isdigit() for c in text)
        
        if has_unit or has_digit:
            return True
        elif len(text) < 60 and ":" not in text:
            if len(text.split()) > 6: return False
            return True
            
        return False

    def extract_content_smart(self, soup):
        content_div = soup.find("div", class_="read__content")
        if not content_div: return "", [], []

        description = ""
        bahan = []
        langkah = []

        all_elements = content_div.find_all(['p', 'ul', 'ol', 'h2', 'h3', 'h4', 'strong', 'b', 'div'])
        current_mode = "intro" 
        
        for elem in all_elements:
            if elem.get('class'):
                cls_str = " ".join(elem.get('class'))
                if any(x in cls_str for x in ['ads', 'inner-link', 'video', 'box', 'photo']):
                    continue
            
            text = self.clean_text(elem.get_text())
            if not text: continue
            if any(bl in text.lower() for bl in self.content_blacklist): continue

            # --- MODE SWITCHING ---
            if self.is_header(text, self.bahan_header_keywords):
                current_mode = "bahan"
                continue
            
            if self.is_header(text, self.langkah_header_keywords):
                current_mode = "langkah"
                continue
            
            # --- EXTRACTION ---
            if current_mode == "intro":
                if not description and len(text) > 50 and elem.name == 'p':
                    if ":" not in text[:15]: description = text
            
            elif current_mode == "bahan":
                if self.is_step_numbered(text):
                    current_mode = "langkah"
                    langkah.append(self.clean_leading_number(text))
                else:
                    items_to_add = []
                    if elem.name in ['ul', 'ol']:
                        items_to_add = [self.clean_text(li.get_text()) for li in elem.find_all('li')]
                    elif elem.name in ['p', 'div']:
                        items_to_add = [text]
                    
                    for item in items_to_add:
                        if self.is_valid_ingredient(item):
                            bahan.append(item)

            elif current_mode == "langkah":
                if elem.name == 'ol':
                    items = [self.clean_leading_number(li.get_text()) for li in elem.find_all('li')]
                    langkah.extend([i for i in items if i])
                elif elem.name in ['p', 'div', 'li']:
                    if self.is_step_numbered(text):
                        langkah.append(self.clean_leading_number(text))

        bahan = list(dict.fromkeys(bahan))
        langkah = list(dict.fromkeys(langkah))
        
        if not description and content_div.find('p'):
            candidates = [p.get_text() for p in content_div.find_all('p') if len(p.get_text()) > 50]
            if candidates: description = self.clean_text(candidates[0])

        return description, bahan, langkah

    def get_links_curated(self, page_limit=20):
        # TAG KHUSUS KESEHATAN/PENYAKIT/METODE SEHAT (Bukan Bahan)
        sources = [
            # 1. Kategori DIET & NUTRISI
            "https://www.kompas.com/tag/resep-diet",
            "https://www.kompas.com/tag/resep-sehat",
            "https://www.kompas.com/tag/makanan-sehat",
            
            # 2. Kategori PENYAKIT (Sehatan)
            "https://www.kompas.com/tag/resep-diabetes",
            "https://www.kompas.com/tag/resep-kolesterol",
            "https://www.kompas.com/tag/resep-asam-urat",
            "https://www.kompas.com/tag/resep-untuk-penderita-diabetes",
            
            # 3. Kategori METODE MASAK SEHAT
            "https://www.kompas.com/tag/resep-kukus",
            "https://www.kompas.com/tag/resep-pepes",
            "https://www.kompas.com/tag/resep-tanpa-minyak",
            "https://www.kompas.com/tag/resep-tanpa-santan",
            "https://www.kompas.com/tag/resep-rebusan",
            
            # 4. Kategori VEGETARIAN/NABATI
            "https://www.kompas.com/tag/resep-vegetarian",
            "https://www.kompas.com/tag/resep-vegan",
            
            # 5. Kategori HERBAL/JAMU
            "https://www.kompas.com/tag/jamu",
            "https://www.kompas.com/tag/minuman-herbal",
            "https://www.kompas.com/tag/wedang"
        ]
        
        all_links = []
        print("\n🔍 Mengumpulkan Link Resep SPESIFIK KESEHATAN (Tanpa Gorengan Biasa)...")
        
        for base_url in sources:
            tag_name = base_url.split('/')[-1]
            print(f"   📂 Scanning tag: {tag_name}...")
            # Scan lebih dalam (20 halaman) karena filter kita sangat ketat
            for i in range(1, 21): 
                url = f"{base_url}?page={i}"
                try:
                    r = requests.get(url, headers=self.headers, timeout=8)
                    soup = BeautifulSoup(r.text, "html.parser")
                    count = 0
                    for a in soup.find_all("a", href=True):
                        href = a['href']
                        if "/food/read/" in href and href not in all_links:
                            all_links.append(href)
                            count += 1
                except: pass
        
        random.shuffle(all_links)
        return all_links

    def scrape_url(self, url):
        try:
            if self.use_selenium and self.driver:
                self.driver.get(url)
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.CLASS_NAME, "read__content")))
                page_source = self.driver.page_source
                soup = BeautifulSoup(page_source, "html.parser")
            else:
                r = requests.get(url, headers=self.headers, timeout=15)
                soup = BeautifulSoup(r.text, "html.parser")

            title_elem = soup.find("h1", class_="read__title")
            title = self.clean_text(title_elem.get_text()) if title_elem else "No Title"

            # 1. CEK JUDUL DULU (Filter Paling Ketat)
            if self.is_listicle_or_compilation(title):
                print(f"   ⏭️  SKIP (Kumpulan/Promo): {title[:40]}...")
                return None
            
            if not self.is_strictly_healthy(title):
                print(f"   ⏭️  SKIP (Tidak Cukup Sehat): {title[:40]}...")
                return None

            date_elem = soup.find("div", class_="read__time")
            date = self.format_date(self.clean_text(date_elem.get_text())) if date_elem else ""

            img_elem = soup.find("meta", property="og:image")
            img_url = img_elem['content'] if img_elem else ""

            desc, bahan, langkah = self.extract_content_smart(soup)
            
            if len(bahan) < 2:
                 print(f"   ⚠️  SKIP: Bahan terlalu sedikit ({len(bahan)})")
                 return None

            return {
                "title": title, "date": date, "description": desc,
                "url": url, "image": img_url, "bahan": bahan, "langkah": langkah
            }

        except Exception as e:
            return None

    def save_results(self, results):
        csv_file = os.path.join(self.dataset_folder, "resep_sehat_strict.csv")
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "id", "type", "judul", "tanggal", "kategori", 
                "deskripsi", "url_gambar", "url_link", "bahan", "langkah"
            ])
            writer.writeheader()
            for i, r in enumerate(results, 1):
                writer.writerow({
                    "id": i, "type": "resep_sehat", "judul": r['title'],
                    "tanggal": r['date'], "kategori": "resep_sehat", "deskripsi": r['description'],
                    "url_gambar": r['image'], "url_link": r['url'],
                    "bahan": " | ".join(r['bahan']), "langkah": " | ".join(r['langkah'])
                })
        
        json_file = os.path.join(self.dataset_folder, "resep_sehat_strict.json")
        json_output = []
        for idx, r in enumerate(results, 1):
            json_output.append({
                "id": idx, "type": "resep_sehat", "judul": r['title'],
                "tanggal": r['date'], "kategori": "resep_sehat", "deskripsi": r['description'],
                "url_gambar": r['image'], "url_link": r['url'],
                "bahan": r['bahan'], "langkah": r['langkah']
            })
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_output, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Data tersimpan di folder '{self.dataset_folder}':")
        print(f"   - {csv_file}")
        print(f"   - {json_file}")

    def run(self, target_count=150):
        print("="*60)
        print("🥗 CRAWLER RESEP Sehat & DIET (STRICT MODE)")
        print("="*60)
        
        # Ambil link dari 15+ SUMBER TAG KESEHATAN (Page 1-20)
        links = self.get_links_curated(page_limit=20) 
        results = []
        
        print(f"\n🚀 Memproses {len(links)} Link Kandidat (Target: {target_count})...\n")
        
        for i, link in enumerate(links):
            if len(results) >= target_count: break
            
            print(f"[{i+1}/{len(links)}] {link}")
            data = self.scrape_url(link)
            
            if not data: continue
            if len(data['langkah']) < 1:
                print("   ⚠️  Skip: Langkah tidak valid")
                continue

            results.append(data)
            print(f"   ✅ BERHASIL! {data['title'][:60]}...")
            print(f"      🌿 {len(data['bahan'])} Bahan | 🍳 {len(data['langkah'])} Langkah")

        self.save_results(results)
        
        if self.use_selenium and self.driver: 
            self.driver.quit()
        print("\n🎉 Selesai!")

if __name__ == "__main__":
    crawler = ResepSehatCrawler()
    crawler.run(target_count=150)