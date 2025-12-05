import requests
from bs4 import BeautifulSoup
import csv
import time
import re


class ResepMinumanCrawler:
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

    def is_recipe_drink(self, title, content):
        """Filter resep MINUMAN saja (bukan makanan)"""
        combined = (title + " " + content).lower()
        
        # 1. WAJIB: Kata kunci minuman
        drink_keywords = [
            'minuman', 'jus', 'juice', 'smoothie', 'kopi', 'coffee', 'teh', 'tea',
            'sirup', 'syrup', 'mocktail', 'cocktail', 'infused water',
            'es buah', 'es campur', 'es teler', 'es kelapa', 'es doger',
            'es kuwud', 'es cendol', 'es cincau', 'es dawet', 'es puter',
            'wedang', 'bajigur', 'bandrek', 'sekoteng', 'soda', 'float',
            'milkshake', 'shake', 'boba', 'bubble tea', 'milk tea',
            'latte', 'cappuccino', 'espresso', 'americano', 'frappe',
            'lemonade', 'squash', 'punch', 'segar', 'fresh', 'dingin',
            'susu', 'milk', 'yogurt', 'lassi', 'air', 'drink', 'beverage',
            'cendol', 'cincau', 'kolak cair', 'bir', 'wine', 'sake',
            'matcha', 'cokelat panas', 'hot chocolate', 'chocolate drink',
            'thai tea', 'green tea', 'herbal tea', 'ginger ale',
            'lime', 'lemon', 'orange juice', 'strawberry drink', 'mango juice',
            'avocado juice', 'alpukat', 'jambu', 'melon', 'semangka'
        ]
        
        has_drink_keyword = any(keyword in combined for keyword in drink_keywords)
        
        if not has_drink_keyword:
            return False
        
        # 2. EXCLUDE: Makanan padat yang mungkin salah masuk
        food_excludes = [
            'nasi', 'mie', 'bakso', 'soto', 'rendang', 'ayam goreng', 
            'ikan bakar', 'daging', 'sayur tumis', 'sambal goreng',
            'roti isi', 'kue kering', 'cake kukus', 'martabak telur',
            'pizza', 'burger', 'sandwich isi', 'pasta rebus'
        ]
        
        if any(food in combined for food in food_excludes):
            return False
        
        # 3. WAJIB: Indikator resep
        recipe_indicators = [
            'resep', 'cara membuat', 'cara bikin', 'bahan-bahan',
            'ingredients', 'langkah', 'tips membuat', 'kreasi',
            'sajian', 'minuman', 'segar', 'pembuatan', 'campuran'
        ]
        
        has_recipe_indicator = any(indicator in combined for indicator in recipe_indicators)
        
        if not has_recipe_indicator:
            return False
        
        # 4. Minimal panjang konten
        if len(content) < 100:
            return False
        
        return True

    # ===== KOMPAS TAG RESEP MINUMAN =====
    def get_links_kompas_minuman(self, max_pages=15):
        print("\n📰 KOMPAS TAG RESEP MINUMAN - Mengambil Link...")
        links = []
        
        for page in range(1, max_pages + 1):
            try:
                url = f"https://www.kompas.com/tag/resep-minuman?page={page}"
                print(f"   Scraping: {url}")
                response = requests.get(url, headers=self.headers, timeout=15)
                soup = BeautifulSoup(response.text, "html.parser")
                
                for a in soup.find_all("a", href=True):
                    href = a["href"]
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

    def crawl(self, target=200):
        print("=" * 80)
        print("🍹 CRAWLER RESEP MINUMAN - KOMPAS ")
        print("=" * 80)
        print("✨ SUMBER RESEP:")
        print("  ✓ Kompas.com/tag/resep-minuman")
        print("=" * 80)
        print(f"🎯 Target: {target} resep minuman")
        print("🍹 Filter: HANYA MINUMAN (Makanan padat otomatis difilter)")
        print("=" * 80)
        
        recipes = []
        
        sources = [
            ("Kompas Minuman", self.get_links_kompas_minuman, self.scrape_kompas, 15),
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
                if not recipe or not recipe["title"] or len(recipe["content"]) < 80:
                    print("   ⚠️  Data tidak lengkap atau terlalu pendek")
                    continue
                
                if self.is_recipe_drink(recipe["title"], recipe["content"]):
                    recipes.append(recipe)
                    print(f"   ✅ RESEP MINUMAN #{len(recipes)}")
                    print(f"   🍹 {recipe['title'][:70]}...")
                else:
                    print("   ⏭️  Bukan resep minuman (makanan padat/tidak relevan)")
                
                time.sleep(1.5)
        
        print(f"\n{'='*80}")
        print("💾 MENYIMPAN HASIL...")
        print(f"{'='*80}")
        
        filename = "resep_minuman.csv"
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
        print(f"🍹 Total Resep Minuman: {len(recipes)}")
        print(f"📁 File: {filename}")
        print(f"{'='*80}")
        
        print("\n📈 STATISTIK PER SUMBER:")
        for source_name, _, _, _ in sources:
            count = sum(1 for r in recipes if any(x in r["url"].lower() for x in source_name.lower().split()))
            print(f"   {source_name}: {count} resep")
        
        print(f"\n🍹 KATEGORI MINUMAN:")
        categories = {
            "Jus & Smoothie": ["jus", "juice", "smoothie"],
            "Kopi & Teh": ["kopi", "coffee", "teh", "tea", "latte", "cappuccino"],
            "Es & Dingin": ["es ", "dingin", "fresh", "segar", "cold"],
            "Susu & Milkshake": ["susu", "milk", "milkshake", "yogurt"],
            "Tradisional": ["wedang", "bajigur", "bandrek", "sekoteng", "cendol"]
        }
        
        for cat_name, keywords in categories.items():
            count = sum(1 for r in recipes if any(kw in r["title"].lower() for kw in keywords))
            if count > 0:
                print(f"   {cat_name}: {count} resep")
        
        print(f"{'='*80}")


if __name__ == "__main__":
    crawler = ResepMinumanCrawler()
    crawler.crawl(target=200)