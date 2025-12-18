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
from datetime import datetime

class ResepMakananCrawlerKompasFinal:
    def __init__(self, use_selenium=True):
        self.use_selenium = use_selenium
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.9',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        # Keyword Header
        self.bahan_header_keywords = [
            'bahan-bahan', 'bahan:', 'bahan utama', 'resep bahan', 'komposisi', 'bahan :'
        ]
        
        self.langkah_header_keywords = [
            'cara membuat', 'cara memasak', 'langkah-langkah', 'langkah pembuatan', 
            'cara mengolah', 'instruksi', 'urutan memasak'
        ]
        
        # Blacklist konten "sampah"
        self.content_blacklist = [
            'baca juga', 'simak video', 'berita foto', 'kunjungi', 'klik tautan',
            'copyright', 'advertisement', 'promoted', 'shopee', 'tokopedia',
            'beli di sini', 'promo', 'diskon', 'sumber:', 'penulis:', 'editor:',
            'kompas.com', 'dapatkan informasi', 'whatsapp', 'telegram'
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
        """Hapus nomor awal (1. bla bla -> bla bla)"""
        return re.sub(r'^\s*\d+[\.\)\-]\s*', '', text).strip()

    def format_date(self, date_str):
        try:
            match = re.search(r'(\d{1,2})\s+([A-Za-z]+)\s+(\d{4})', date_str)
            if match:
                day, month, year = match.groups()
                # Map bulan sederhana
                return f"{day}-{month}-{year}"
            return date_str
        except: return date_str

    # --- VALIDASI LISTICLE (KUMPULAN RESEP) ---
    def is_listicle_or_compilation(self, title):
        """Mendeteksi apakah artikel ini kumpulan resep (Harus di-SKIP)"""
        t = title.lower()
        
        # Cek 1: Judul dimulai dengan angka > 1 (Contoh: "10 Resep...", "5 Cara...")
        # Regex: Angka di awal + spasi + kata kunci jamak/koleksi
        if re.match(r'^\s*[2-9]\d*\s+', t) or re.match(r'^\s*1\d+\s+', t): 
             # Cek kata kunci setelah angka
             if any(x in t for x in ['resep', 'ide', 'menu', 'masakan', 'cara', 'makanan']):
                 return True

        # Cek 2: Kata kunci kumpulan
        compilation_words = [
            'kumpulan resep', 'daftar resep', 'rekomendasi', 'aneka resep', 
            'variasi', 'serba', 'macam-macam', 'ide bekal', 'ide jualan', 
            'untuk seminggu', 'sehari-hari'
        ]
        if any(w in t for w in compilation_words):
            return True
            
        return False

    def is_header(self, text, keywords):
        text_lower = text.lower()
        if len(text) > 40: return False 
        return any(k in text_lower for k in keywords)

    def is_step_numbered(self, text):
        # Cek apakah teks dimulai dengan angka urut (1., 2., dst)
        return bool(re.match(r'^\s*\d+[\.\)\-]', text))

    # --- VALIDASI BAHAN KETAT ---
    def is_valid_ingredient(self, text):
        """Cek apakah teks ini benar-benar bahan makanan"""
        t_lower = text.lower()
        
        # 1. Cek Blacklist Sampah
        if any(x in t_lower for x in self.content_blacklist):
            return False
            
        # 2. Cek Panjang (Bahan biasanya pendek, < 150 char)
        if len(text) > 150: return False
        
        # 3. Indikator Bahan (Satuan Ukuran)
        units = [
            'gr', 'gram', 'kg', 'sdm', 'sdt', 'ml', 'liter', 'buah', 'siung', 
            'batang', 'lembar', 'potong', 'iris', 'cincang', 'parut', 'secukupnya',
            'sendok', 'cup', 'bawang', 'garam', 'gula', 'minyak', 'air', 'tepung',
            'ikat', 'bungkus', 'kaleng', 'ons', 'cm'
        ]
        
        has_unit = any(u in t_lower for u in units)
        has_digit = any(c.isdigit() for c in text)
        
        # Syarat Bahan: Harus punya Satuan ATAU Angka, ATAU teksnya sangat pendek (<50 char)
        # Teks panjang tanpa angka/satuan biasanya narasi sampah
        if has_unit or has_digit:
            return True
        elif len(text) < 50 and ":" not in text: # Nama bahan tanpa takaran (misal: "Garam", "Merica")
            return True
            
        return False

    def extract_content_smart(self, soup):
        content_div = soup.find("div", class_="read__content")
        if not content_div: return "", [], []

        description = ""
        bahan = []
        langkah = []

        all_elements = content_div.find_all(['p', 'ul', 'ol', 'h2', 'h3', 'strong', 'div'])
        current_mode = "intro" 
        
        for elem in all_elements:
            # Skip elemen iklan/hidden secara eksplisit
            if elem.get('class'):
                cls_str = " ".join(elem.get('class'))
                if any(x in cls_str for x in ['ads', 'inner-link', 'video', 'box']):
                    continue
            
            text = self.clean_text(elem.get_text())
            if not text: continue
            
            # Global Blacklist Check (Sangat Penting untuk membuang "Baca juga")
            if any(bl in text.lower() for bl in self.content_blacklist):
                continue

            # --- MODE SWITCHING ---
            if self.is_header(text, self.bahan_header_keywords):
                current_mode = "bahan"
                continue
            
            if self.is_header(text, self.langkah_header_keywords):
                current_mode = "langkah"
                continue
            
            # --- EXTRACTION ---
            if current_mode == "intro":
                if not description and len(text) > 60 and elem.name == 'p':
                    # Pastikan bukan meta data
                    if ":" not in text[:15]: 
                        description = text
            
            elif current_mode == "bahan":
                # Proteksi: Kalau ketemu angka urut (1.), berarti sudah masuk Langkah tapi header tidak terdeteksi
                if self.is_step_numbered(text):
                    current_mode = "langkah"
                    # Proses sebagai langkah di bawah
                else:
                    items_to_add = []
                    if elem.name in ['ul', 'ol']:
                        items_to_add = [self.clean_text(li.get_text()) for li in elem.find_all('li')]
                    elif elem.name in ['p', 'div']:
                        items_to_add = [text]
                    
                    # VALIDASI ITEM BAHAN SATU PER SATU
                    for item in items_to_add:
                        if self.is_valid_ingredient(item):
                            bahan.append(item)

            if current_mode == "langkah":
                # STRICT: Hanya ambil jika ada nomor (1., 2., 3.)
                if elem.name == 'ol': # Kalau OL, percaya saja isinya langkah
                    items = [self.clean_leading_number(li.get_text()) for li in elem.find_all('li')]
                    langkah.extend([i for i in items if i])
                elif elem.name in ['p', 'div', 'li']:
                    if self.is_step_numbered(text):
                        langkah.append(self.clean_leading_number(text))

        # Deduplikasi
        bahan = list(dict.fromkeys(bahan))
        langkah = list(dict.fromkeys(langkah))
        
        # Validasi Fallback Deskripsi
        if not description and content_div.find('p'):
            candidates = [p.get_text() for p in content_div.find_all('p') if len(p.get_text()) > 50]
            if candidates: description = self.clean_text(candidates[0])

        return description, bahan, langkah

    def get_links(self, page_limit=5):
        links = []
        print("\n🔍 Mengumpulkan Link Resep...")
        for i in range(1, page_limit + 1):
            url = f"https://www.kompas.com/tag/resep-makanan?page={i}"
            try:
                r = requests.get(url, headers=self.headers, timeout=10)
                soup = BeautifulSoup(r.text, "html.parser")
                for a in soup.find_all("a", href=True):
                    href = a['href']
                    if "/food/read/" in href and href not in links:
                        links.append(href)
            except: pass
            print(f"   📄 Page {i} done.")
        return links

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

            # --- FILTER JUDUL DI SINI (Sebelum Extract) ---
            if self.is_listicle_or_compilation(title):
                print(f"   ⏭️  SKIP (Listicle/Kumpulan): {title}")
                return None

            date_elem = soup.find("div", class_="read__time")
            date = self.format_date(self.clean_text(date_elem.get_text())) if date_elem else ""

            img_elem = soup.find("meta", property="og:image")
            img_url = img_elem['content'] if img_elem else ""

            desc, bahan, langkah = self.extract_content_smart(soup)
            
            # --- FINAL LOGIC CHECK ---
            # Jika bahan > 30 item, sangat curiga ini artikel kumpulan resep yang lolos filter judul
            if len(bahan) > 30:
                print(f"   ⏭️  SKIP (Too many ingredients -> Multi Recipe): {len(bahan)} items")
                return None

            return {
                "title": title,
                "date": date,
                "description": desc,
                "url": url,
                "image": img_url,
                "bahan": bahan,
                "langkah": langkah
            }

        except Exception as e:
            return None

    def run(self, target_count=50):
        print("="*60)
        print("🍳 CRAWLER RESEP TUNGGAL - STRICT MODE")
        print("="*60)
        
        links = self.get_links(page_limit=30) # Ambil lebih banyak link karena banyak yg bakal di-skip
        results = []
        
        print(f"\n🚀 Memproses {len(links)} Link...\n")
        
        for i, link in enumerate(links):
            if len(results) >= target_count: break
            
            print(f"[{i+1}/{len(links)}] {link}")
            data = self.scrape_url(link)
            
            if not data: continue # Sudah di-handle skip logic di dalam scrape_url
            
            # Validasi Akhir
            if len(data['bahan']) < 3:
                print("   ⚠️  Skip: Bahan terlalu sedikit")
                continue
            
            if len(data['langkah']) < 2:
                print("   ⚠️  Skip: Langkah tidak valid (kurang dari 2)")
                continue

            results.append(data)
            print(f"   ✅ BERHASIL! {data['title'][:50]}...")
            print(f"      🥗 {len(data['bahan'])} Bahan | 🍳 {len(data['langkah'])} Langkah")

        # Save CSV
        with open('resep_kompas_clean.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["Judul", "Tanggal", "Kategori", "Deskripsi", "URL Gambar", "URL Link", "Bahan", "Langkah"])
            writer.writeheader()
            for r in results:
                writer.writerow({
                    "Judul": r['title'],
                    "Tanggal": r['date'],
                    "Kategori": "resep_makanan",
                    "Deskripsi": r['description'],
                    "URL Gambar": r['image'],
                    "URL Link": r['url'],
                    "Bahan": " | ".join(r['bahan']),
                    "Langkah": " | ".join(r['langkah'])
                })
        
        # Save JSON
        json_output = []
        for idx, r in enumerate(results, 1):
            json_output.append({
                "id": idx,
                "type": "resep_makanan",
                "judul": r['title'],
                "tanggal": r['date'],
                "kategori": "resep_makanan",
                "deskripsi": r['description'],
                "url_gambar": r['image'],
                "url_link": r['url'],
                "bahan": r['bahan'],
                "langkah": r['langkah']
            })
            
        with open('resep_kompas_clean.json', 'w', encoding='utf-8') as f:
            json.dump(json_output, f, ensure_ascii=False, indent=2)
            
        print(f"\n🎉 Selesai! {len(results)} resep tunggal tersimpan.")
        if self.use_selenium and self.driver:
            self.driver.quit()

if __name__ == "__main__":
    crawler = ResepMakananCrawlerKompasFinal()
    crawler.run(target_count=200)