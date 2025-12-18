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
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

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
    if (Array.isArray(raw)) return raw.map((x, i) => <li key={i} className="mb-1">{x}</li>);
    return raw.toString().split(/\r?\n|\||;|\./).filter(s=>s.trim()).map((s,i)=> <li key={i} className="mb-1">{s.trim()}</li>);
  };

  const isNews = (item["type"] || item["kategori"] || item["category"] || "").toString().toLowerCase().includes("berita") || (isiBerita && isiBerita.length>0);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center px-4">
      <div className="absolute inset-0 bg-black/60" onClick={onClose}></div>

      <div className="relative max-w-3xl w-full bg-[#6E4A3E]/8 backdrop-blur-md border border-[#6E4A3E]/20 rounded-2xl shadow-2xl max-h-[85vh] overflow-auto text-white">
        {/* top-right close */}
        <button onClick={onClose} aria-label="Tutup" className="absolute right-4 top-4 bg-white/6 hover:bg-white/10 text-white rounded-full w-9 h-9 flex items-center justify-center">✕</button>

        {/* TOP ROW: image left, meta + action right */}
        <div className="flex flex-col md:flex-row items-start gap-4 p-6">
          <div className="md:w-64 flex-shrink-0">
            <div className="w-64 h-64 overflow-hidden rounded-lg">
              <img src={image || "/images/placeholder.jpg"} alt={title || "image"} className="w-full h-full object-cover rounded-lg shadow-lg border border-[#6E4A3E]/20" />
            </div>
          </div>

          <div className="flex-1 flex flex-col justify-start pl-4">
            <h2 className="text-3xl md:text-4xl font-semibold leading-tight mb-2" style={{fontFamily: 'Poppins, serif', color: '#E4C590'}}>{title}</h2>

            <div className="mb-4">
              <span className="text-base font-semibold text-white/85">{date || "N/A"}</span>
            </div>

            <div className="flex items-center gap-3 mt-2 mb-4">
              {item["tfidf_score"] !== undefined && (
                <span className="text-xs md:text-sm bg-[#1E40AF]/20 border border-[#1E40AF]/30 text-white px-2 py-1 rounded-full font-semibold">TF-IDF: {(item["tfidf_score"]||0).toFixed(4)}</span>
              )}

              {item["sbert_score"] !== undefined && (
                <span className="text-xs md:text-sm bg-[#065f46]/20 border border-[#065f46]/30 text-white px-2 py-1 rounded-full font-semibold">SBERT: {(item["sbert_score"]||0).toFixed(4)}</span>
              )}

            </div>
          </div>
        </div>

        {/* BOTTOM: description, bahan, langkah (full width under image) */}
        <div className="border-t border-[#6E4A3E]/16 px-6 pb-6 pt-6 overflow-auto">
          <div className="mb-6">
            <h3 className="text-xl md:text-2xl font-semibold mb-3" style={{fontFamily: 'Poppins, serif', color: '#E4C590'}}>{isNews ? 'Isi Berita' : 'Deskripsi'}</h3>
            <p className="text-base md:text-lg text-white/90 leading-relaxed" style={{textAlign: 'justify'}}>{isNews ? (isiBerita || "Tidak ada isi berita") : (deskripsi || "Tidak ada deskripsi")}</p>
          </div>

          {!isNews && (
            <div className="mb-6">
              <h3 className="text-xl md:text-2xl font-semibold mb-3" style={{fontFamily: 'Poppins, serif', color: '#E4C590'}}>Bahan</h3>
              <ul className="list-disc list-inside text-base md:text-lg leading-relaxed text-white/95" style={{textAlign: 'justify'}}>
                {renderList(bahanRaw)}
              </ul>
            </div>
          )}

          {!isNews && (
            <div className="mb-10">
              <h3 className="text-xl md:text-2xl font-semibold mb-3" style={{fontFamily: 'Poppins, serif', color: '#E4C590'}}>Langkah</h3>
              <ol className="list-decimal list-inside text-base md:text-lg leading-relaxed text-white/95" style={{textAlign: 'justify'}}>
                {renderList(langkahRaw)}
              </ol>
            </div>
          )}

          <div className="flex justify-end">
            <a href={link || "#"} target="_blank" rel="noopener noreferrer" aria-label="Baca Selengkapnya" className="inline-flex items-center gap-2 bg-gradient-to-r from-[#E4C590] to-[#d9b87d] text-[#3b2b1f] font-semibold px-4 py-2 rounded-full shadow-md hover:shadow-lg transform transition-all duration-200 hover:-translate-y-1 hover:scale-105 focus:outline-none focus:ring-2 focus:ring-[#E4C590]/30">
              <span>Baca Selengkapnya</span>
              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M14 3h7v7M10 14L21 3" />
              </svg>
            </a>
          </div>
        </div>
      </div>
    </div>
  );
}
