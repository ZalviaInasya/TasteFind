import { useState, useEffect } from "react";
import DetailModal from "../components/DetailModal";

export default function All() {
  const [searchValue, setSearchValue] = useState("");
  const [hasSearched, setHasSearched] = useState(false);
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSearch = async () => {
    if (!searchValue.trim()) {
      setError("Silakan masukkan query pencarian");
      return;
    }

    setLoading(true);
    setError("");
    setHasSearched(true);
    // record last search query so Eval modal can auto-run
    try { localStorage.setItem("tastefind:last_search", searchValue); } catch (e) {}

    try {
      const response = await fetch("http://localhost:5000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: searchValue,
          category: "semua",
          top_k: 5,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data.results || []);

      // Background evaluation request (cached for modal)
      fetch("http://localhost:5000/evaluate/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: searchValue, top_k: 20 }),
      })
        .then((r) => (r.ok ? r.json() : null))
        .then((evalRes) => {
          if (evalRes) {
            try {
              localStorage.setItem("tastefind:last_eval", JSON.stringify({ query: searchValue, result: evalRes, ts: Date.now() }));
            } catch (e) {
              console.warn("Failed to cache eval:", e);
            }
          }
        })
        .catch(() => {});
    } catch (err) {
      console.error("Search error:", err);
      setError(`Terjadi kesalahan: ${err.message}`);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  // Separate results by scoring method
  const getTFIDFResults = () => {
    return [...results].sort((a, b) => (b.tfidf_score || 0) - (a.tfidf_score || 0)).slice(0, 5);
  };

  const getSBERTResults = () => {
    return [...results].sort((a, b) => (b.sbert_score || 0) - (a.sbert_score || 0)).slice(0, 5);
  };

  const getHybridResults = () => {
    return [...results]
      .sort((a, b) => {
        const as = a.hybrid_score ?? ((a.tfidf_score || 0) + (a.sbert_score || 0)) / 2;
        const bs = b.hybrid_score ?? ((b.tfidf_score || 0) + (b.sbert_score || 0)) / 2;
        return bs - as;
      })
      .slice(0, 5);
  };

  const [scoreType, setScoreType] = useState("hybrid");
  const [selectedItem, setSelectedItem] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const formatDate = (raw) => {
    if (!raw) return "N/A";
    try {
      const d = new Date(raw);
      if (!isNaN(d)) {
        return d.toLocaleDateString("id-ID", { day: "numeric", month: "short", year: "numeric" });
      }
    } catch (e) {}
    const match = raw.match(/(\d{1,2}\s+\w+\s+\d{4})/);
    if (match) return match[1];
    return raw.length > 30 ? raw.substring(0, 30) + "..." : raw;
  };

  const getDescription = (item, maxLen = 120) => {
    const getText = (val) => {
      if (!val) return "";
      if (Array.isArray(val)) return val.join(" ");
      return String(val);
    };

    const text = (
      getText(item["Isi Berita"]) ||
      getText(item["Isi Resep"]) ||
      getText(item["deskripsi"]) ||
      getText(item["Deskripsi"]) ||
      getText(item["isi"]) ||
      ""
    ).trim();

    if (!text) return "Tidak ada deskripsi";
    if (text.length <= maxLen) return text;
    return text.substring(0, maxLen) + ".....";
  };

  if (!hasSearched) {
    return (
      <div
        className="relative w-full min-h-screen flex flex-col items-center justify-center"
        style={{
          backgroundImage: "url(/images/all.jpg)",
          backgroundSize: "cover",
          backgroundPosition: "center",
        }}
      >
        {/* DARK LUXURY OVERLAY */}
        <div className="absolute inset-0 bg-gradient-to-b from-black/75 via-black/60 to-black/85"></div>

        {/* CONTENT */}
        <div className="relative flex flex-col items-center justify-center text-center px-6 w-full z-10">
          {/* TITLE */}
          <h1
            className="text-4xl md:text-5xl font-semibold text-white drop-shadow-2xl mb-4 opacity-0 animate-fade-in"
            style={{ fontFamily: "Poppins, serif", animationDelay: "0.2s" }}
          >
            Semua <span className="text-[#E4C590]">Konten Kuliner</span> Dalam
            Satu Tempat
          </h1>

          {/* SUBTEXT */}
          <p
            className="text-lg md:text-xl text-white/85 max-w-2xl leading-relaxed mb-10 opacity-0 animate-fade-in"
            style={{ fontFamily: "Georgia, serif", animationDelay: "0.5s" }}
          >
            Dari resep makanan, minuman, hidangan sehat, hingga berita kuliner
            terbaru.
            <span className="text-[#F1D8AA] font-semibold">
              {" "}
              Jelajahi semuanya dengan mudah.
            </span>
          </p>

          {/* SEARCH BOX */}
          <div
            className="flex bg-white/90 backdrop-blur-xl rounded-full overflow-hidden shadow-[0_4px_35px_rgba(0,0,0,0.3)] w-full max-w-2xl opacity-0 animate-fade-in-up"
            style={{ animationDelay: "0.8s" }}
          >
            <input
              type="text"
              placeholder="Cari semua konten kuliner..."
              className="px-6 py-3 w-full bg-transparent text-[#6E4A3E] outline-none text-lg"
              style={{ fontFamily: "Georgia, serif" }}
              value={searchValue}
              onChange={(e) => setSearchValue(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSearch()}
            />
            <button
              className="px-8 bg-[#6E4A3E] text-white font-semibold hover:bg-[#5b3d33] transition-all text-lg"
              style={{ fontFamily: "Poppins, serif" }}
              onClick={handleSearch}
            >
              Cari
            </button>
          </div>
        </div>

        {/* ANIMATION */}
        <style>
          {`
            @keyframes fade-in {
              from { opacity: 0; transform: translateY(10px); }
              to { opacity: 1; transform: translateY(0); }
            }
            @keyframes fade-in-up {
              from { opacity: 0; transform: translateY(25px); }
              to { opacity: 1; transform: translateY(0); }
            }
            .animate-fade-in {
              animation: fade-in 0.8s forwards ease-out;
            }
            .animate-fade-in-up {
              animation: fade-in-up 0.9s forwards ease-out;
            }
          `}
        </style>
      </div>
    );
  }

  // Jika ada hasil pencarian, tampilkan hasil dengan transisi scroll
  return (
    <div
      className="relative w-full min-h-screen"
      style={{
        backgroundImage: "url(/images/all.jpg)",
        backgroundSize: "cover",
        backgroundPosition: "center",
        backgroundAttachment: "fixed",
      }}
    >
      {/* DARK LUXURY OVERLAY */}
      <div className="absolute inset-0 bg-gradient-to-b from-black/75 via-black/60 to-black/85 pointer-events-none"></div>

      {/* RESULTS SECTION - FULL SCREEN */}
      <div
        className="relative flex flex-col items-center justify-start text-center px-6 py-16 z-10 min-h-screen w-full"
        style={{ animation: "slideDown 0.6s ease-out" }}
      >
        {/* TITLE */}
        <h1
          className="text-3xl md:text-4xl font-semibold text-white drop-shadow-2xl mb-4 opacity-0 animate-fade-in"
          style={{ fontFamily: "Poppins, serif", animationDelay: "0.1s" }}
        >
          Hasil Pencarian: <span className="text-[#E4C590]">"{searchValue}"</span>
        </h1>

        {/* SEARCH BOX */}
        <div
          className="flex bg-white/80 backdrop-blur-lg rounded-full overflow-hidden shadow-[0_4px_35px_rgba(0,0,0,0.3)] w-full max-w-2xl mb-10 opacity-0 animate-fade-in"
          style={{ animationDelay: "0.2s" }}
        >
          <input
            type="text"
            placeholder="Cari semua konten kuliner..."
            className="px-6 py-3 w-full bg-transparent text-[#6E4A3E] outline-none text-lg"
            style={{ fontFamily: "Georgia, serif" }}
            value={searchValue}
            onChange={(e) => setSearchValue(e.target.value)}
            onKeyPress={(e) => e.key === "Enter" && handleSearch()}
          />
          <button
            className="px-8 bg-[#6E4A3E] text-white font-semibold hover:bg-[#5b3d33] transition-all text-lg"
            style={{ fontFamily: "Poppins, serif" }}
            onClick={handleSearch}
            disabled={loading}
          >
            {loading ? "Mencari..." : "Cari"}
          </button>
        </div>

        {/* ERROR MESSAGE */}
        {error && (
          <div className="w-full max-w-7xl mb-6 p-4 bg-red-500/30 border border-red-300/50 rounded-lg text-red-200">
            {error}
          </div>
        )}

        {/* LOADING STATE */}
        {loading && (
          <div className="w-full max-w-7xl flex items-center justify-center py-16">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-white"></div>
          </div>
        )}

        {/* HASIL CONTAINER - SIDE BY SIDE */}
        {!loading && (
          <div className="w-full max-w-7xl">
            <div className="space-y-6">
              <div className="flex items-center gap-3 justify-center mb-4">
                <button
                  onClick={() => setScoreType("hybrid")}
                  className={`px-4 py-2 rounded-full font-semibold text-sm transition-all ${scoreType === "hybrid" ? "bg-[#6E4A3E] text-white" : "bg-white/6 text-white/80"}`}
                >
                  Hybrid
                </button>
                <button
                  onClick={() => setScoreType("tfidf")}
                  className={`px-4 py-2 rounded-full font-semibold text-sm transition-all ${scoreType === "tfidf" ? "bg-[#6E4A3E] text-white" : "bg-white/6 text-white/80"}`}
                >
                  TF-IDF
                </button>
                <button
                  onClick={() => setScoreType("sbert")}
                  className={`px-4 py-2 rounded-full font-semibold text-sm transition-all ${scoreType === "sbert" ? "bg-[#6E4A3E] text-white" : "bg-white/6 text-white/80"}`}
                >
                  SBERT
                </button>
              </div>

              {/* RESULTS LIST */}
              <div className="backdrop-blur-lg bg-white/[0.02] border border-white/20 rounded-2xl p-8 shadow-lg hover:bg-white/[0.05] transition-all opacity-0 animate-fade-in-up" style={{ animationDelay: "0.3s" }}>
                <h2 className="text-2xl font-semibold text-white mb-6 drop-shadow-lg" style={{ fontFamily: "Poppins, serif" }}>
                  {scoreType === "tfidf" ? "TF-IDF" : scoreType === "sbert" ? "SBERT" : "HYBRID"}
                </h2>
                {(
                  scoreType === "tfidf" ? getTFIDFResults() : scoreType === "sbert" ? getSBERTResults() : getHybridResults()
                ).length > 0 ? (
                  <div className="space-y-6">
                    {(
                      scoreType === "tfidf" ? getTFIDFResults() : scoreType === "sbert" ? getSBERTResults() : getHybridResults()
                    ).map((item, idx) => (
                      <div
                        key={`res-${scoreType}-${idx}`}
                        className="relative bg-white/[0.03] backdrop-blur-lg border border-white/15 rounded-xl shadow-md hover:shadow-lg hover:bg-white/[0.08] transition-all group min-h-[17rem] flex flex-col"
                      >
                        <div className="flex flex-col sm:flex-row items-start gap-4 p-4 pb-4 flex-1 h-full overflow-hidden">
                          {/* IMAGE WITH ROUNDED WRAPPER */}
                          <div className="w-full sm:w-64 h-64 flex-shrink-0 rounded-lg overflow-hidden bg-white/5">
                            <img
                              src={item["URL Gambar"] || "/images/placeholder.jpg"}
                              alt={item["Judul"] || item["Judul Resep"] || "Item"}
                              className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                              onError={(e) => {
                                e.target.src = "/images/placeholder.jpg";
                              }}
                            />
                          </div>



                          {/* CONTENT */}
                          <div className="flex-1 flex flex-col min-w-0 sm:h-64">
                            <div className="mb-3">
                              <h3 className="font-semibold text-white mb-3 line-clamp-2 drop-shadow text-left text-xl md:text-2xl">
                                {item["Judul"] || item["Judul Resep"] || "N/A"}
                              </h3>
                              <p className="text-xs md:text-sm text-white/70 mb-2 text-left">
                                {formatDate(item["Tanggal"]) }
                              </p>
                              <p className="text-sm md:text-base text-white/80 text-left line-clamp-3 mb-3">
                                {getDescription(item, 180)}
                              </p>
                            </div>

                              <div className="mt-10 md:mt-12 flex items-center gap-4 flex-wrap w-full justify-between">
                                <div className="flex items-center gap-4 flex-wrap">
                                  {scoreType === "hybrid" ? (
                                    <>
                                      <span className="text-sm md:text-base bg-blue-400/25 backdrop-blur-sm border border-blue-300/40 text-white px-3 py-1.5 rounded-full font-semibold whitespace-nowrap">
                                        tf-idf: {(item["tfidf_score"] || 0).toFixed(4)}
                                      </span>
                                      <span className="text-sm md:text-base bg-green-400/25 backdrop-blur-sm border border-green-300/40 text-white px-3 py-1.5 rounded-full font-semibold whitespace-nowrap">
                                        sbert: {(item["sbert_score"] || 0).toFixed(4)}
                                      </span>
                                      <span className="text-sm md:text-base bg-purple-500/25 backdrop-blur-sm border border-purple-400/40 text-white px-3 py-1.5 rounded-full font-semibold whitespace-nowrap">
                                        hybrid: {(item["hybrid_score"] ?? (((item["tfidf_score"]||0)+(item["sbert_score"]||0))/2)).toFixed(4)}
                                      </span>
                                    </>
                                  ) : scoreType === "tfidf" ? (
                                    <span className="text-sm md:text-base bg-blue-400/30 backdrop-blur-sm border border-blue-300/50 text-white px-3 py-1.5 rounded-full font-semibold whitespace-nowrap">
                                      tf-idf: {(item["tfidf_score"] || 0).toFixed(4)}
                                    </span>
                                  ) : (
                                    <span className="text-sm md:text-base bg-green-400/30 backdrop-blur-sm border border-green-300/50 text-white px-3 py-1.5 rounded-full font-semibold whitespace-nowrap">
                                      sbert: {(item["sbert_score"] || 0).toFixed(4)}
                                    </span>
                                  )}

                                  <span className="text-sm md:text-base bg-amber-800/30 backdrop-blur-sm border border-amber-600/30 text-white px-3 py-1.5 rounded-full font-semibold whitespace-nowrap mr-4">
                                    { (item["category"] || "semua").toString().toLowerCase() }
                                  </span>
                                </div>

                                <button
                                  onClick={() => { setSelectedItem(item); setShowModal(true); }}
                                  className="bg-amber-800/40 hover:bg-amber-700/50 text-white text-sm md:text-base font-semibold px-3 py-1.5 rounded-md transition-all drop-shadow whitespace-nowrap border border-amber-600/30"
                                >
                                  Selengkapnya
                                </button>
                              </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-white/80">Tidak ada hasil</p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>

      {/* DETAIL MODAL */}
      <DetailModal open={showModal} onClose={() => { setShowModal(false); setSelectedItem(null); }} item={selectedItem} />

      {/* ANIMATION */}
      <style>
        {`
          @keyframes fade-in {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
          }
          @keyframes fade-in-up {
            from { opacity: 0; transform: translateY(25px); }
            to { opacity: 1; transform: translateY(0); }
          }
          @keyframes slideDown {
            from { transform: translateY(100vh); }
            to { transform: translateY(0); }
          }
          .animate-fade-in {
            animation: fade-in 0.8s forwards ease-out;
          }
          .animate-fade-in-up {
            animation: fade-in-up 0.9s forwards ease-out;
          }
        `}
      </style>
    </div>
  );
}