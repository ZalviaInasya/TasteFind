import { useEffect, useState } from "react";

export default function DetailModal({ open, onClose, item }) {
  if (!open || !item) return null;

  const [animateIn, setAnimateIn] = useState(false);
  useEffect(() => {
    setAnimateIn(true);
    const onKey = (e) => {
      if (e.key === "Escape") onClose();
    };
    window.addEventListener("keydown", onKey);
    return () => {
      window.removeEventListener("keydown", onKey);
      document.body.style.overflow = "auto";
    };
  }, [onClose]);

  // --- LOGIKA ASLI ---
  const getText = (keys) => {
    for (const k of keys) {
      if (k in item && item[k]) {
        if (Array.isArray(item[k])) return item[k].join(" ");
        return String(item[k]);
      }
    }
    return "";
  };

  const title = getText(["Judul", "judul", "Judul Resep", "judul_resep"]);
  const date = getText(["Tanggal", "tanggal"]);
  const image = getText(["URL Gambar", "url_gambar", "image"]);
  const link = getText(["URL Link", "url_link", "url"]);
  const deskripsi = getText(["Deskripsi", "deskripsi"]);
  const isiBerita = getText(["Isi Berita", "Isi", "isi"]);
  const bahanRaw = item["Bahan"] || item["bahan"] || item["Ingredients"] || item["ingredients"] || [];
  const langkahRaw = item["Langkah"] || item["langkah"] || item["Steps"] || item["steps"] || [];

  const renderList = (raw) => {
    if (!raw) return null;
    const items = Array.isArray(raw) ? raw : raw.toString().split(/\r?\n|\||;|\./).filter(s => s.trim());
    return items.map((s, i) => (
      <li key={i} className="flex gap-4 mb-4 items-start group">
        <span className="mt-2.5 w-2 h-2 rounded-full bg-[#E4C590] flex-shrink-0 shadow-[0_0_10px_rgba(228,197,144,0.3)]"></span>
        <span className="text-white/80 group-hover:text-white transition-colors text-lg leading-relaxed">{s.trim()}</span>
      </li>
    ));
  };

  const isNews = (item["type"] || item["kategori"] || item["category"] || "").toString().toLowerCase().includes("berita") || (isiBerita && isiBerita.length > 0);
  const hybridScore = item["hybrid_score"] ?? (((item["tfidf_score"] || 0) + (item["sbert_score"] || 0)) / 2);

  return (
    <div className={`fixed inset-0 z-[100] flex items-center justify-center p-4 md:p-8 transition-all duration-700 ${animateIn ? "opacity-100" : "opacity-0"}`}>
      <div className="absolute inset-0 bg-black/95 backdrop-blur-md" onClick={onClose}></div>

      {/* Kontainer Utama 7xl */}
      <div className={`relative w-full max-w-7xl h-[90vh] bg-[#1A1614] rounded-[40px] shadow-[0_50px_100px_rgba(0,0,0,1)] border border-white/5 flex flex-col md:flex-row overflow-hidden transition-all duration-700 transform ${animateIn ? "translate-y-0 scale-100" : "translate-y-12 scale-95"}`}>
        
        <button onClick={onClose} className="absolute right-8 top-8 z-50 bg-white/5 hover:bg-white/10 text-white rounded-full w-14 h-14 flex items-center justify-center backdrop-blur-md border border-white/10 transition-all">
          <svg xmlns="http://www.w3.org/2000/svg" className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M6 18L18 6M6 6l12 12" /></svg>
        </button>

        {/* IMAGE */}
        <div className="md:w-1/2 relative h-80 md:h-full overflow-hidden">
          <img src={image || "/images/placeholder.jpg"} alt={title} className="w-full h-full object-cover" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#1A1614] via-transparent md:bg-gradient-to-r md:from-transparent md:to-[#1A1614]"></div>
        </div>

        {/* CONTENT */}
        <div className="md:w-1/2 flex flex-col h-full bg-[#1A1614]">
          <div className="flex-1 overflow-y-auto p-10 md:p-20 no-scrollbar">
            
            <header className="mb-12">
              <h2 className="text-5xl md:text-6xl font-bold leading-[1.1] mb-6 tracking-tighter" style={{ color: '#E4C590', fontFamily: 'Poppins, serif' }}>
                {title}
              </h2>
              <p className="text-white/40 text-base italic">{date || "TasteFind Premium Selection"}</p>
            </header>

            {/* DASHBOARD SKOR - Biasa aja tapi beda warna selaras */}
            <div className="grid grid-cols-3 gap-6 mb-16">
              
              {/* HYBRID - Gold/Cream */}
              <div className="p-5 rounded-[24px] border border-[#E4C590]/30 bg-[#E4C590]/5">
                <p className="text-[10px] uppercase tracking-[0.2em] mb-2 font-black text-[#E4C590]/60">Hybrid Score</p>
                <p className="text-2xl font-bold text-[#E4C590]">{hybridScore.toFixed(4)}</p>
              </div>

              {/* TF-IDF - Soft Blue/Silver */}
              <div className="p-5 rounded-[24px] border border-blue-400/30 bg-blue-400/5">
                <p className="text-[10px] uppercase tracking-[0.2em] mb-2 font-black text-blue-400/60">TF-IDF</p>
                <p className="text-2xl font-bold text-blue-300">{(item["tfidf_score"] || 0).toFixed(4)}</p>
              </div>

              {/* SBERT - Soft Green */}
              <div className="p-5 rounded-[24px] border border-green-400/30 bg-green-400/5">
                <p className="text-[10px] uppercase tracking-[0.2em] mb-2 font-black text-green-400/60">SBERT</p>
                <p className="text-2xl font-bold text-green-300">{(item["sbert_score"] || 0).toFixed(4)}</p>
              </div>

            </div>

            <div className="space-y-16">
              <section>
                <h3 className="text-sm uppercase tracking-[0.4em] text-[#E4C590] font-black mb-6">Deskripsi</h3>
                <p className="text-white/80 leading-[1.8] text-xl italic" style={{ textAlign: 'justify', fontFamily: 'serif' }}>
                  "{isNews ? isiBerita : (deskripsi || "Hidangan eksklusif yang diracik khusus untuk gaya hidup sehat Anda.")}"
                </p>
              </section>

              {!isNews && (
                <>
                  <section>
                    <h3 className="text-3xl font-bold text-white mb-8 tracking-tight">Bahan Utama</h3>
                    <ul className="text-lg">{renderList(bahanRaw)}</ul>
                  </section>
                  <section>
                    <h3 className="text-3xl font-bold text-white mb-8 tracking-tight">Langkah Pembuatan</h3>
                    <ul className="text-lg">{renderList(langkahRaw)}</ul>
                  </section>
                </>
              )}
            </div>

            <footer className="mt-24 pt-10 border-t border-white/5 flex justify-end">
              <a href={link || "#"} target="_blank" className="bg-[#E4C590] text-[#1A1614] font-black px-12 py-5 rounded-full text-sm uppercase tracking-widest shadow-lg">
                Baca Selengkapnya
              </a>
            </footer>

          </div>
        </div>
      </div>

      <style jsx global>{`
        .no-scrollbar::-webkit-scrollbar { display: none; }
        .no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }
      `}</style>
    </div>
  );
}