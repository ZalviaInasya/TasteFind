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
from datetime import datetime

class ResepMinumanCrawlerFinal:
    def __init__(self, use_selenium=True):
        self.use_selenium = use_selenium
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        }
        
        self.dataset_folder = "dataset"
        if not os.path.exists(self.dataset_folder):
            os.makedirs(self.dataset_folder)
        
        # Keyword Header
        self.bahan_header_keywords = [
            'bahan-bahan', 'bahan:', 'bahan utama', 'resep bahan', 'komposisi',
            'bahan isian', 'bahan sirup', 'bahan kuah', 'bahan pelengkap',
            'bahan jelly', 'bahan agar', 'bahan toping', 'topping',
            'bahan biang', 'bahan campuran', 'bahan es', 'bahan jus', 'bahan:'
        ]
        
        self.langkah_header_keywords = [
            'cara membuat', 'cara memasak', 'langkah-langkah', 'langkah pembuatan', 
            'cara mengolah', 'instruksi', 'urutan', 'cara bikin', 'cara meracik',
            'cara penyajian'
        ]
        
        # Blacklist Konten (Global)
        self.content_blacklist = [
            'baca juga', 'simak video', 'berita foto', 'kunjungi', 'klik tautan',
            'copyright', 'advertisement', 'promoted', 'shopee', 'tokopedia',
            'beli di sini', 'promo', 'diskon', 'sumber:', 'penulis:', 'editor:',
            'kompas.com', 'dapatkan informasi', 'whatsapp', 'telegram',
            'artikel kompas.id', 'buka gambar', 'lihat foto'
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

    # --- FILTER KHUSUS MINUMAN ---
    def is_drink_recipe(self, title):
        t = title.lower()
        drink_keywords = [
            'es ', 'ice', 'jus ', 'juice', 'smoothie', 'kopi', 'coffee', 
            'teh', 'tea', 'latte', 'wedang', 'sirup', 'syrup', 'minuman', 
            'cokelat panas', 'bajigur', 'bandrek', 'sekoteng', 'bir', 
            'soda', 'squash', 'mojito', 'cocktail', 'mocktail', 'susu', 
            'milk', 'yogurt', 'cendol', 'dawet', 'kolak', 'sop buah',
            'es buah', 'es campur', 'es teler', 'es doger', 'dalgona',
            'thai tea', 'lemonade', 'bir pletok'
        ]
        
        # Makanan padat yang sering salah masuk
        food_keywords = [
            'ayam', 'daging', 'ikan', 'nasi', 'mie', 'soto', 'rawon', 
            'tumis', 'goreng', 'bakar', 'pepes', 'sambal', 'kue', 'roti',
            'puding', 'cake', 'bolu', 'lontong', 'ketupat'
        ]
        
        if any(k in t for k in drink_keywords):
            # Tolak jika mengandung kata makanan padat (misal: "Ayam Masak Cola")
            if any(f in t for f in food_keywords):
                # Kecuali "Es Krim Goreng" atau "Es Kue"
                if "es krim" in t or "es gabus" in t: return True
                return False
            return True
        return False

    def is_listicle_or_compilation(self, title):
        t = title.lower()
        if re.match(r'^\s*[2-9]\d*\s+', t) or re.match(r'^\s*1\d+\s+', t): 
             if any(x in t for x in ['resep', 'ide', 'menu', 'minuman', 'cara']):
                 return True
        compilation_words = ['kumpulan', 'daftar', 'rekomendasi', 'aneka', 'variasi', 'serba', 'macam-macam']
        if any(w in t for w in compilation_words): return True
        return False

    def is_header(self, text, keywords):
        text_lower = text.lower()
        if len(text) > 40: return False 
        return any(k in text_lower for k in keywords)

    def is_step_numbered(self, text):
        return bool(re.match(r'^\s*\d+[\.\)\-]', text))

    def is_valid_ingredient(self, text):
        """Validasi Bahan SANGAT KETAT untuk membuang iklan baris"""
        t_lower = text.lower()
        
        # 1. Cek Blacklist Umum
        if any(x in t_lower for x in self.content_blacklist): return False
        
        # 2. Cek Pola Iklan Artikel Lain (Ini yang sering bocor)
        # Jika baris dimulai dengan "Resep", "Cara", "Tips", "Manfaat" -> DIBUANG
        # Kecuali "Resep ini menggunakan" (jarang di list bahan)
        if re.match(r'^(resep|cara|tips|manfaat|5 tips|6 manfaat)\s+', t_lower):
            return False
            
        # 3. Cek Artikel Kompas.id (SPESIFIK)
        if "artikel kompas.id" in t_lower: return False
        if "baca juga:" in t_lower: return False

        # 4. Validasi Panjang
        # Bahan itu pendek. Kalau > 100 char, kemungkinan besar paragraf iklan/deskripsi
        if len(text) > 100: return False

        # 5. Cek Unit/Takaran (Prioritas Utama)
        units = [
            'gr', 'gram', 'kg', 'sdm', 'sdt', 'ml', 'liter', 'buah', 
            'batang', 'lembar', 'potong', 'iris', 'secukupnya',
            'sendok', 'cup', 'gelas', 'cangkir', 'botol', 'kaleng',
            'sachet', 'bungkus', 'keping', 'kotak', 'es batu', 'air',
            'tetes', 'ruas', 'genggam', 'siung', 'cm', 'paket'
        ]
        has_unit = any(u in t_lower for u in units)
        has_digit = any(c.isdigit() for c in text)
        
        # SYARAT LOLOS:
        # A. Punya Unit ATAU Angka
        if has_unit or has_digit:
            return True
        
        # B. Jika tidak punya unit/angka, teks harus PENDEK (< 60 char)
        # Contoh: "Garam", "Gula pasir", "Es batu" -> Lolos
        # Contoh: "Resep Mocktail untuk Imlek 2025..." -> Tidak Lolos (Panjang & gak ada unit)
        elif len(text) < 60 and ":" not in text:
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
            # Skip elemen iklan visual
            if elem.get('class'):
                cls_str = " ".join(elem.get('class'))
                if any(x in cls_str for x in ['ads', 'inner-link', 'video', 'box', 'photo']):
                    continue
            
            text = self.clean_text(elem.get_text())
            if not text: continue
            
            # Global Blacklist (langsung skip elemen ini)
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
                    # Pastikan bukan metadata (Penulis: ...)
                    if ":" not in text[:15]: description = text
            
            elif current_mode == "bahan":
                # Jika ketemu angka urut "1." di mode bahan, kemungkinan ini langkah yang nyasar
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
                        # FILTER LAGI DI SINI
                        if self.is_valid_ingredient(item):
                            bahan.append(item)
                        # Jangan 'break' atau stop kalau ketemu item tidak valid.
                        # Mungkin setelah iklan "Artikel Kompas" ada "Es batu"

            elif current_mode == "langkah":
                if elem.name == 'ol':
                    items = [self.clean_leading_number(li.get_text()) for li in elem.find_all('li')]
                    langkah.extend([i for i in items if i])
                elif elem.name in ['p', 'div', 'li']:
                    if self.is_step_numbered(text):
                        langkah.append(self.clean_leading_number(text))

        # Deduplikasi dan pembersihan akhir
        bahan = list(dict.fromkeys(bahan))
        langkah = list(dict.fromkeys(langkah))
        
        # Fallback Deskripsi
        if not description and content_div.find('p'):
            candidates = [p.get_text() for p in content_div.find_all('p') if len(p.get_text()) > 50]
            if candidates: description = self.clean_text(candidates[0])

        return description, bahan, langkah

    def get_links(self, page_limit=5):
        links = []
        print("\n🔍 Mengumpulkan Link Resep Minuman...")
        for i in range(1, page_limit + 1):
            url = f"https://www.kompas.com/tag/resep-minuman?page={i}"
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

            # Filter Judul
            if self.is_listicle_or_compilation(title):
                print(f"   ⏭️  SKIP (Kumpulan): {title[:40]}...")
                return None
            
            if not self.is_drink_recipe(title):
                print(f"   ⏭️  SKIP (Bukan Minuman): {title[:40]}...")
                return None

            date_elem = soup.find("div", class_="read__time")
            date = self.format_date(self.clean_text(date_elem.get_text())) if date_elem else ""

            img_elem = soup.find("meta", property="og:image")
            img_url = img_elem['content'] if img_elem else ""

            desc, bahan, langkah = self.extract_content_smart(soup)
            
            # --- FINAL VALIDATION CHECK ---
            # Jika bahan < 2, jangan-jangan ke-skip semua?
            if len(bahan) < 2:
                 print(f"   ⚠️  SKIP: Bahan terlalu sedikit ({len(bahan)})")
                 return None
                 
            # Cek apakah bahan masih mengandung kata "Artikel Kompas" (Double check)
            bahan_clean = [b for b in bahan if "kompas" not in b.lower()]
            
            return {
                "title": title, "date": date, "description": desc,
                "url": url, "image": img_url, "bahan": bahan_clean, "langkah": langkah
            }

        except Exception as e:
            return None

    def save_results(self, results):
        # 1. Save CSV
        csv_file = os.path.join(self.dataset_folder, "resep_minuman.csv")
        with open(csv_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                "id", "type", "judul", "tanggal", "kategori", 
                "deskripsi", "url_gambar", "url_link", "bahan", "langkah"
            ])
            writer.writeheader()
            for i, r in enumerate(results, 1):
                writer.writerow({
                    "id": i,
                    "type": "resep_minuman",
                    "judul": r['title'],
                    "tanggal": r['date'],
                    "kategori": "resep_minuman",
                    "deskripsi": r['description'],
                    "url_gambar": r['image'],
                    "url_link": r['url'],
                    "bahan": " | ".join(r['bahan']),
                    "langkah": " | ".join(r['langkah'])
                })
        
        # 2. Save JSON
        json_file = os.path.join(self.dataset_folder, "resep_minuman.json")
        json_output = []
        for idx, r in enumerate(results, 1):
            json_output.append({
                "id": idx,
                "type": "resep_minuman",
                "judul": r['title'],
                "tanggal": r['date'],
                "kategori": "resep_minuman",
                "deskripsi": r['description'],
                "url_gambar": r['image'],
                "url_link": r['url'],
                "bahan": r['bahan'],
                "langkah": r['langkah']
            })
            
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(json_output, f, ensure_ascii=False, indent=2)

        print(f"\n💾 Data tersimpan di folder '{self.dataset_folder}':")
        print(f"   - {csv_file}")
        print(f"   - {json_file}")

    def run(self, target_count=200):
        print("="*60)
        print("🍹 CRAWLER RESEP MINUMAN - FINAL CLEAN")
        print("="*60)
        
        links = self.get_links(page_limit=30) 
        results = []
        
        print(f"\n🚀 Memproses {len(links)} Link (Target: {target_count})...\n")
        
        for i, link in enumerate(links):
            if len(results) >= target_count: break
            
            print(f"[{i+1}/{len(links)}] {link}")
            data = self.scrape_url(link)
            
            if not data: continue
            
            if len(data['langkah']) < 1:
                print("   ⚠️  Skip: Langkah tidak valid")
                continue

            results.append(data)
            print(f"   ✅ BERHASIL! {data['title'][:50]}...")
            print(f"      🍹 {len(data['bahan'])} Bahan | 🥤 {len(data['langkah'])} Langkah")

        self.save_results(results)
        
        if self.use_selenium and self.driver:
            self.driver.quit()
        print("\n🎉 Selesai!")

if __name__ == "__main__":
    crawler = ResepMinumanCrawlerFinal()
    crawler.run(target_count=200)