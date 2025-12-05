import requests
from bs4 import BeautifulSoup
import csv
import time
import re


class BeritaKulinerCrawler:
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

    # ===== LIPUTAN6 (TAG) =====
    def get_links_liputan6(self, max_pages=15):
        print("\n🔍 LIPUTAN6 - Mengambil Link dari Tag Kuliner...")
        links = []
        
        for page in range(1, max_pages + 1):
            try:
                url = f"https://www.liputan6.com/tag/kuliner?page={page}"
                print(f"   Scraping: {url}")
                response = requests.get(url, headers=self.headers, timeout=15)
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Cari semua link artikel
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "liputan6.com" in href and ("/read/" in href or "/lifestyle/" in href):
                        if href not in links:
                            links.append(href)
                
                print(f"   Halaman {page}: Total {len(links)} link terkumpul")
                time.sleep(2)
            except Exception as e:
                print(f"   Error halaman {page}: {e}")
        
        return links

    def scrape_liputan6(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Title
            title = ""
            h1 = soup.find("h1", class_="read-page--header--title")
            if not h1:
                h1 = soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)
            
            # Date
            date = ""
            time_tag = soup.find("time", class_="read-page--header__author__datetime")
            if not time_tag:
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
            content_div = soup.find("div", class_="article-content-body")
            if not content_div:
                content_div = soup.find("div", {"itemprop": "articleBody"})
            
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

    # ===== TRIBUNNEWS (TAG) =====
    def get_links_tribun(self, max_pages=15):
        print("\n🗞️ TRIBUN - Mengambil Link dari Tag Kuliner...")
        links = []
        
        for page in range(1, max_pages + 1):
            try:
                url = f"https://www.tribunnews.com/tag/kuliner?page={page}"
                print(f"   Scraping: {url}")
                response = requests.get(url, headers=self.headers, timeout=15)
                soup = BeautifulSoup(response.text, "html.parser")
                
                # Cari semua link artikel
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "tribunnews.com" in href and len(href) > 30:
                        # Hindari link navigasi/tag
                        if "/tag/" not in href and "?page=" not in href:
                            if href not in links:
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

    # ===== TEMPO.CO =====
    def get_links_tempo(self, max_pages=10):
        print("\n⏰ TEMPO - Mengambil Link Kuliner...")
        links = []
        
        for page in range(1, max_pages + 1):
            try:
                url = f"https://gaya.tempo.co/kuliner/{page}"
                print(f"   Scraping: {url}")
                response = requests.get(url, headers=self.headers, timeout=15)
                soup = BeautifulSoup(response.text, "html.parser")
                
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "tempo.co" in href and "/read/" in href:
                        if href not in links:
                            links.append(href)
                
                print(f"   Halaman {page}: Total {len(links)} link terkumpul")
                time.sleep(2)
            except Exception as e:
                print(f"   Error halaman {page}: {e}")
        
        return links

    def scrape_tempo(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Title
            title = ""
            h1 = soup.find("h1", class_="title")
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
            content_div = soup.find("div", class_="detail-in")
            if not content_div:
                content_div = soup.find("div", {"id": "isi"})
            
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

    # ===== IDN TIMES =====
    def get_links_idntimes(self, max_pages=10):
        print("\n🍔 IDN TIMES - Mengambil Link Food...")
        links = []
        
        for page in range(1, max_pages + 1):
            try:
                url = f"https://www.idntimes.com/food?page={page}"
                print(f"   Scraping: {url}")
                response = requests.get(url, headers=self.headers, timeout=15)
                soup = BeautifulSoup(response.text, "html.parser")
                
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if href.startswith("/food/") and len(href) > 10:
                        full_url = "https://www.idntimes.com" + href
                        if full_url not in links and "?page=" not in full_url:
                            links.append(full_url)
                
                print(f"   Halaman {page}: Total {len(links)} link terkumpul")
                time.sleep(2)
            except Exception as e:
                print(f"   Error halaman {page}: {e}")
        
        return links

    def scrape_idntimes(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")
            
            title = ""
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)
            
            date = ""
            time_tag = soup.find("time")
            if time_tag:
                date = time_tag.get_text(strip=True) or time_tag.get("datetime", "")
            
            image_url = ""
            og_image = soup.find("meta", property="og:image")
            if og_image:
                image_url = og_image.get("content", "")
            
            content = ""
            content_div = soup.find("div", class_="detail-content")
            if not content_div:
                content_div = soup.find("div", {"itemprop": "articleBody"})
            
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

    # ===== DETIK FOOD =====
    def get_links_detikfood(self, max_pages=10):
        print("\n🍜 DETIK FOOD - Mengambil Link...")
        links = []
        
        for page in range(1, max_pages + 1):
            try:
                url = "https://food.detik.com/" if page == 1 else f"https://food.detik.com/indeks/{page}"
                print(f"   Scraping: {url}")
                response = requests.get(url, headers=self.headers, timeout=15)
                soup = BeautifulSoup(response.text, "html.parser")
                
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if "food.detik.com" in href and any(cat in href for cat in ["/berita-boga/", "/info-kuliner/", "/resto-dan-kafe/"]):
                        if href not in links:
                            links.append(href)
                
                print(f"   Halaman {page}: Total {len(links)} link terkumpul")
                time.sleep(2)
            except Exception as e:
                print(f"   Error halaman {page}: {e}")
        
        return links

    def scrape_detikfood(self, url):
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            soup = BeautifulSoup(response.text, "html.parser")
            
            title = ""
            h1 = soup.find("h1")
            if h1:
                title = h1.get_text(strip=True)
            
            date = ""
            date_elem = soup.find("div", class_="detail__date")
            if not date_elem:
                date_elem = soup.find("time")
            if date_elem:
                date = date_elem.get_text(strip=True) or date_elem.get("datetime", "")
            
            image_url = ""
            og_image = soup.find("meta", property="og:image")
            if og_image:
                image_url = og_image.get("content", "")
            
            content = ""
            content_div = soup.find("div", class_="detail__body-text")
            if not content_div:
                content_div = soup.find("div", {"itemprop": "articleBody"})
            
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

    def crawl(self, target=100):
        print("=" * 80)
        print("📰 CRAWLER BERITA KULINER - TAG OPTIMIZED VERSION")
        print("=" * 80)
        print("✨ SUMBER BERITA:")
        print("  ✓ Kompas.com/tag/kuliner")
        print("  ✓ Liputan6.com/tag/kuliner")
        print("  ✓ Tribunnews.com/tag/kuliner")
        print("  ✓ Tempo.co (Gaya-Kuliner)")
        print("  ✓ IDN Times (Food)")
        print("  ✓ Detik Food")
        print("=" * 80)
        print(f"🎯 Target: {target} berita berkualitas")
        print("=" * 80)
        
        articles = []
        
        sources = [
            ("Kompas", self.get_links_kompas, self.scrape_kompas, 15),
            ("Liputan6", self.get_links_liputan6, self.scrape_liputan6, 15),
            ("Tribun", self.get_links_tribun, self.scrape_tribun, 15),
            ("Tempo", self.get_links_tempo, self.scrape_tempo, 10),
            ("IDN Times", self.get_links_idntimes, self.scrape_idntimes, 10),
            ("Detik Food", self.get_links_detikfood, self.scrape_detikfood, 10)
        ]
        
        for source_name, get_links, scrape_func, max_pages in sources:
            if len(articles) >= target:
                break
            
            print(f"\n{'='*80}")
            print(f"🔗 SUMBER: {source_name}")
            print(f"{'='*80}")
            
            links = get_links(max_pages=max_pages)
            print(f"✅ Berhasil mengumpulkan {len(links)} link dari {source_name}")
            
            for idx, url in enumerate(links, 1):
                if len(articles) >= target:
                    break
                
                print(f"\n[{source_name} - {idx}/{len(links)}] Memproses artikel...")
                print(f"   URL: {url[:75]}...")
                
                article = scrape_func(url)
                if not article or not article["title"] or len(article["content"]) < 200:
                    print("   ⚠️  Data tidak lengkap atau terlalu pendek")
                    continue
                
                # Filter berita berkualitas
                if self.is_quality_news(article["title"], article["content"]):
                    articles.append(article)
                    print(f"   ✅ BERITA BERKUALITAS #{len(articles)}")
                    print(f"   📰 {article['title'][:70]}...")
                else:
                    print("   ⏭️  Tidak memenuhi kriteria berita berkualitas")
                
                time.sleep(1)
        
        # Simpan CSV
        print(f"\n{'='*80}")
        print("💾 MENYIMPAN HASIL...")
        print(f"{'='*80}")
        
        filename = "berita_kuliner.csv"
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["No", "Judul", "Tanggal", "Isi Berita", "URL Link", "URL Gambar"])
            writer.writeheader()
            for idx, a in enumerate(articles, 1):
                writer.writerow({
                    "No": idx,
                    "Judul": a["title"],
                    "Tanggal": a["date"],
                    "Isi Berita": a["content"],
                    "URL Link": a["url"],
                    "URL Gambar": a["image_url"]
                })
        
        print(f"\n✅ SELESAI!")
        print(f"📊 Total Berita Berkualitas: {len(articles)}")
        print(f"📁 File: {filename}")
        print(f"{'='*80}")
        
        # Statistik per sumber
        print("\n📈 STATISTIK PER SUMBER:")
        for source_name, _, _, _ in sources:
            count = sum(1 for a in articles if source_name.lower() in a["url"].lower())
            print(f"   {source_name}: {count} berita")
        print(f"{'='*80}")


if __name__ == "__main__":
    crawler = BeritaKulinerCrawler()
    crawler.crawl(target=100)  # Target 100 berita berkualitas