import requests
from bs4 import BeautifulSoup
import csv
import time
import re


class ResepSehatCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7',
        }

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

    def is_recipe_healthy(self, title, content):
        """Filter resep/tips SEHAT saja - WAJIB ada kata 'sehat' dan keyword kesehatan"""
        combined = (title + " " + content).lower()
        
        # 1. WAJIB: Kata "SEHAT" harus ada
        if "sehat" not in combined:
            return False
        
        # 2. WAJIB: Minimal salah satu keyword kesehatan/manfaat
        health_keywords = [
            # Kata sehat dan variasinya
            'sehat', 'menyehatkan', 'kesehatan', 'healthy',
            
            # Diet dan penurunan berat badan
            'diet', 'menurunkan berat badan', 'langsing', 'kurus', 'slim',
            'rendah kalori', 'low calori', 'tanpa lemak', 'fat free',
            
            # Manfaat kesehatan
            'berkhasiat', 'bermanfaat', 'khasiat', 'manfaat', 'benefit',
            'bergizi', 'nutrisi', 'gizi seimbang', 'nutritious',
            
            # Penyakit dan kesembuhan
            'kolesterol', 'kolestrol', 'diabetes', 'diabetic', 'gula darah',
            'darah tinggi', 'hipertensi', 'tekanan darah', 'jantung sehat',
            'stroke', 'asam urat', 'maag', 'lambung',
            
            # Detox dan pembersihan
            'detox', 'detoksifikasi', 'membersihkan', 'cleansing',
            'antioksidan', 'antioxidant',
            
            # Organik dan alami
            'organik', 'organic', 'alami', 'natural', 'herbal',
            
            # Daya tahan tubuh
            'imun', 'imunitas', 'daya tahan tubuh', 'immunity',
            'antibodi', 'vitamin', 'mineral',
            
            # Kondisi kesehatan
            'sembuh', 'penyembuhan', 'healing', 'obat alami',
            'mengurangi', 'mencegah', 'melawan', 'fight',
            
            # Tips kesehatan
            'tips sehat', 'cara sehat', 'hidup sehat', 'lifestyle sehat',
            'pola hidup sehat', 'gaya hidup sehat'
        ]
        
        has_health_keyword = any(keyword in combined for keyword in health_keywords)
        
        if not has_health_keyword:
            return False
        
        # 3. EXCLUDE: Resep biasa tanpa konten kesehatan
        # Jika hanya menyebut nama makanan/minuman tanpa pembahasan sehat
        if len(content) < 100:
            return False
        
        # Hitung berapa banyak kata kesehatan yang muncul
        health_count = sum(1 for keyword in health_keywords if keyword in combined)
        
        # Minimal ada 2 kata kesehatan berbeda
        if health_count < 2:
            return False
        
        # 4. WAJIB: Harus ada indikator artikel/resep
        content_indicators = [
            'resep', 'cara membuat', 'cara bikin', 'bahan-bahan',
            'ingredients', 'langkah', 'tips', 'manfaat', 'khasiat',
            'mengolah', 'sajian', 'hidangan', 'menu', 'ramuan'
        ]
        
        has_content_indicator = any(indicator in combined for indicator in content_indicators)
        
        if not has_content_indicator:
            return False
        
        return True

    # ===== KOMPAS TAG RESEP SEHAT / MAKANAN SEHAT =====
    def get_links_kompas_sehat(self, max_pages=15):
        print("\n📰 KOMPAS TAG - Mengambil Link Resep Sehat...")
        links = []
        
        # Gunakan beberapa tag terkait kesehatan
        tags = ["makanan-sehat", "resep-sehat", "diet-sehat"]
        
        for tag in tags:
            for page in range(1, max_pages + 1):
                if len(links) >= 120:
                    break
                    
                try:
                    url = f"https://www.kompas.com/tag/{tag}?page={page}"
                    print(f"   Scraping [{tag}]: {url}")
                    response = requests.get(url, headers=self.headers, timeout=15)
                    soup = BeautifulSoup(response.text, "html.parser")
                    
                    for a in soup.find_all("a", href=True):
                        href = a["href"]
                        if "kompas.com" in href and "/read/" in href:
                            if href not in links:
                                links.append(href)
                    
                    print(f"   [{tag}] Hal {page}: Total {len(links)} link")
                    time.sleep(2)
                except Exception as e:
                    print(f"   Error [{tag}] hal {page}: {e}")
        
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
                date = date_elem.get_text(strip=True)
            
            # Image
            image_url = ""
            og_image = soup.find("meta", property="og:image")
            if og_image:
                image_url = og_image.get("content", "")
            
            # Content
            content = ""
            content_div = soup.find("div", class_="read__content")
            if content_div:
                paragraphs = content_div.find_all("p")
                content_parts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 20:
                        content_parts.append(text)
                content = " ".join(content_parts)
                content = self.clean_content(content)
            
            return {"title": title, "date": date, "content": content, "url": url, "image_url": image_url}
        except Exception as e:
            print(f"      Error scraping: {e}")
            return None

    # ===== TRIBUNNEWS RESEP MASAKAN (FILTER SEHAT) =====
    def get_links_tribun_resep(self, max_pages=15):
        print("\n🗞️ TRIBUN RESEP MASAKAN - Mengambil Link...")
        links = []
        
        for page in range(1, max_pages + 1):
            try:
                url = f"https://www.tribunnews.com/resep-masakan?page={page}"
                print(f"   Scraping: {url}")
                response = requests.get(url, headers=self.headers, timeout=15)
                soup = BeautifulSoup(response.text, "html.parser")
                
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "tribunnews.com" in href and len(href) > 30:
                        if "/resep-masakan" not in href or "?page=" not in href:
                            if href not in links and href != url:
                                links.append(href)
                
                print(f"   Halaman {page}: Total {len(links)} link terkumpul")
                time.sleep(2)
            except Exception as e:
                print(f"   Error halaman {page}: {e}")
        
        return links

    def scrape_tribun(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Title
            title = ""
            h1 = soup.find("h1", id="arttitle")
            if not h1:
                h1 = soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)
            
            # Date
            date = ""
            time_tag = soup.find("time")
            if time_tag:
                date = time_tag.get("datetime", "") or time_tag.get_text(strip=True)
            
            # Image
            image_url = ""
            og_image = soup.find("meta", property="og:image")
            if og_image:
                image_url = og_image.get("content", "")
            
            # Content
            content = ""
            content_div = soup.find("div", class_="side-article")
            if not content_div:
                content_div = soup.find("div", {"id": "article-body"})
            
            if content_div:
                paragraphs = content_div.find_all("p")
                content_parts = []
                for p in paragraphs:
                    text = p.get_text(strip=True)
                    if len(text) > 20:
                        content_parts.append(text)
                content = " ".join(content_parts)
                content = self.clean_content(content)
            
            return {"title": title, "date": date, "content": content, "url": url, "image_url": image_url}
        except Exception as e:
            print(f"      Error scraping: {e}")
            return None

    def crawl(self, target=200):
        print("=" * 80)
        print("🥗 CRAWLER RESEP SEHAT - KOMPAS + TRIBUN")
        print("=" * 80)
        print("✨ SUMBER RESEP:")
        print("  ✓ Kompas.com/tag/makanan-sehat, resep-sehat, diet-sehat")
        print("  ✓ Tribunnews.com/resep-masakan (filter: sehat)")
        print("=" * 80)
        print(f"🎯 Target: {target} resep/tips sehat")
        print("🥗 Filter: WAJIB ADA kata 'SEHAT' + keyword kesehatan")
        print("=" * 80)
        print("\n📋 KEYWORD KESEHATAN:")
        print("  ✓ Sehat, menyehatkan, kesehatan")
        print("  ✓ Diet, menurunkan berat badan, rendah kalori")
        print("  ✓ Berkhasiat, bermanfaat, bergizi, nutrisi")
        print("  ✓ Kolesterol, diabetes, darah tinggi, jantung")
        print("  ✓ Detox, antioksidan, imun, daya tahan tubuh")
        print("  ✓ Sembuh, mencegah penyakit, obat alami")
        print("=" * 80)
        
        recipes = []
        
        sources = [
            ("Kompas Sehat", self.get_links_kompas_sehat, self.scrape_kompas, 10),
            ("Tribun Resep", self.get_links_tribun_resep, self.scrape_tribun, 15),
        ]
        
        for source_name, get_links, scrape_func, max_pages in sources:
            if len(recipes) >= target:
                break
            
            print(f"\n{'='*80}")
            print(f"🔗 SUMBER: {source_name}")
            print(f"{'='*80}")
            
            links = get_links(max_pages=max_pages)
            print(f"✅ Berhasil mengumpulkan {len(links)} link dari {source_name}")
            
            for idx, url in enumerate(links, 1):
                if len(recipes) >= target:
                    break
                
                print(f"\n[{source_name} - {idx}/{len(links)}] Memproses resep...")
                print(f"   URL: {url[:75]}...")
                
                recipe = scrape_func(url)
                if not recipe or not recipe["title"] or len(recipe["content"]) < 100:
                    print("   ⚠️  Data tidak lengkap atau terlalu pendek")
                    continue
                
                # Filter HANYA resep/tips SEHAT
                if self.is_recipe_healthy(recipe["title"], recipe["content"]):
                    recipes.append(recipe)
                    print(f"   ✅ RESEP SEHAT #{len(recipes)}")
                    print(f"   🥗 {recipe['title'][:70]}...")
                else:
                    print("   ⏭️  Bukan konten sehat (tidak ada kata 'sehat'/keyword kesehatan)")
                
                time.sleep(1.5)
        
        print(f"\n{'='*80}")
        print("💾 MENYIMPAN HASIL...")
        print(f"{'='*80}")
        
        filename = "resep_sehat.csv"
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["No", "Judul Resep", "Tanggal", "Isi Resep", "URL Link", "URL Gambar"])
            writer.writeheader()
            for idx, r in enumerate(recipes, 1):
                writer.writerow({
                    "No": idx,
                    "Judul Resep": r["title"],
                    "Tanggal": r["date"],
                    "Isi Resep": r["content"],
                    "URL Link": r["url"],
                    "URL Gambar": r["image_url"]
                })
        
        print(f"\n✅ SELESAI!")
        print(f"🥗 Total Resep/Tips Sehat: {len(recipes)}")
        print(f"📁 File: {filename}")
        print(f"{'='*80}")
        
        print("\n📈 STATISTIK PER SUMBER:")
        for source_name, _, _, _ in sources:
            count = sum(1 for r in recipes if any(x in r["url"].lower() for x in source_name.lower().split()))
            print(f"   {source_name}: {count} resep")
        
        print(f"\n🥗 KATEGORI KESEHATAN:")
        categories = {
            "Diet & Penurunan BB": ["diet", "menurunkan", "langsing", "rendah kalori"],
            "Anti Penyakit": ["kolesterol", "diabetes", "darah tinggi", "jantung", "stroke"],
            "Detox & Antioksidan": ["detox", "antioksidan", "membersihkan"],
            "Imun & Daya Tahan": ["imun", "imunitas", "daya tahan", "vitamin"],
            "Organik & Alami": ["organik", "alami", "herbal", "natural"]
        }
        
        for cat_name, keywords in categories.items():
            count = sum(1 for r in recipes if any(kw in (r["title"] + " " + r["content"]).lower() for kw in keywords))
            if count > 0:
                print(f"   {cat_name}: {count} resep")
        
        print(f"{'='*80}")


if __name__ == "__main__":
    crawler = ResepSehatCrawler()
    crawler.crawl(target=200)