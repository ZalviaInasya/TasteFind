import { useState, useEffect } from "react";

export default function Makanan() {
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

    try {
      const response = await fetch("http://localhost:5000/search", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: searchValue,
          category: "makanan",
          top_k: 5,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResults(data.results || []);
    } catch (err) {
      console.error("Search error:", err);
      setError(`Terjadi kesalahan: ${err.message}`);
      setResults([]);
    } finally {
      setLoading(false);
    }
  };

  const getTFIDFResults = () => {
    return [...results].sort((a, b) => (b.tfidf_score || 0) - (a.tfidf_score || 0)).slice(0, 5);
  };

  const getSBERTResults = () => {
    return [...results].sort((a, b) => (b.sbert_score || 0) - (a.sbert_score || 0)).slice(0, 5);
  };

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
    const text = (item["Isi Berita"] || item["Isi Resep"] || "").trim();
    if (!text) return "Tidak ada deskripsi";
    if (text.length <= maxLen) return text;
    return text.substring(0, maxLen) + ".....";
  };

  if (!hasSearched) {
    return (
      <div
        className="relative w-full min-h-screen flex flex-col items-center justify-center"
        style={{
          backgroundImage: "url(/images/makanan.jpg)",
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
            Temukan <span className="text-[#E4C590]">Rasa Terbaik</span> di Setiap Hidangan
          </h1>

          {/* SUBTEXT */}
          <p
            className="text-lg md:text-xl text-white/85 max-w-2xl leading-relaxed mb-10 opacity-0 animate-fade-in"
            style={{ fontFamily: "Georgia, serif", animationDelay: "0.5s" }}
          >
            Ribuan resep makanan lezat dari seluruh Nusantara hingga mancanegara.
            <span className="text-[#F1D8AA] font-semibold">
              {" "}
              Ayo mulai petualangan rasa-mu.
            </span>
          </p>

          {/* SEARCH BOX */}
          <div
            className="flex bg-white/90 backdrop-blur-xl rounded-full overflow-hidden shadow-[0_4px_35px_rgba(0,0,0,0.3)] w-full max-w-2xl opacity-0 animate-fade-in-up"
            style={{ animationDelay: "0.8s" }}
          >
            <input
              type="text"
              placeholder="Cari makanan favoritmu..."
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

  return (
    <div
      className="relative w-full min-h-screen"
      style={{
        backgroundImage: "url(/images/makanan.jpg)",
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
            placeholder="Cari makanan favoritmu..."
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
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
              {/* TF-IDF SECTION */}
              <div className="backdrop-blur-lg bg-white/[0.02] border border-white/20 rounded-2xl p-8 shadow-lg hover:bg-white/[0.05] transition-all opacity-0 animate-fade-in-up" style={{ animationDelay: "0.3s" }}>
                <h2 className="text-2xl font-semibold text-white mb-6 drop-shadow-lg" style={{ fontFamily: "Poppins, serif" }}>
                  TF-IDF Results
                </h2>
                {getTFIDFResults().length > 0 ? (
                  <div className="space-y-6">
                    {getTFIDFResults().map((item, idx) => (
                      <div
                        key={`tfidf-${idx}`}
                        className="bg-white/[0.03] backdrop-blur-lg border border-white/15 rounded-xl shadow-md hover:shadow-lg hover:bg-white/[0.08] transition-all group h-40 flex flex-col"
                      >
                        <div className="flex flex-col sm:flex-row items-start gap-3 p-3 flex-1 overflow-hidden">
                          {/* IMAGE WITH ROUNDED WRAPPER */}
                          <div className="w-full sm:w-32 h-32 flex-shrink-0 rounded-lg overflow-hidden bg-white/5">
                            <img
                              src={item["URL Gambar"] || "/images/placeholder.jpg"}
                              alt={item["Judul"] || "Item"}
                              className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                              onError={(e) => {
                                e.target.src = "/images/placeholder.jpg";
                              }}
                            />
                          </div>
                          
                          {/* CONTENT */}
                          <div className="flex-1 flex flex-col justify-between min-w-0">
                            <div>
                              <h3 className="font-semibold text-white mb-1 line-clamp-2 drop-shadow text-left text-sm">
                                {item["Judul"] || item["Judul Resep"] || "N/A"}
                              </h3>
                              <p className="text-xs text-white/70 mb-1 text-left">
                                {formatDate(item["Tanggal"]) }
                              </p>
                              <p className="text-xs text-white/80 text-left line-clamp-2">
                                {getDescription(item, 100)}
                              </p>
                            </div>
                            <div className="flex justify-between items-center pt-2 gap-2">
                              <span className="text-xs bg-blue-400/30 backdrop-blur-sm border border-blue-300/50 text-white px-2 py-1 rounded-full font-semibold whitespace-nowrap">
                                tf-idf: {(item["tfidf_score"] || 0).toFixed(3)}
                              </span>
                              <a
                                href={item["URL Link"] || "#"}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="bg-amber-800/40 hover:bg-amber-700/50 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-all drop-shadow whitespace-nowrap border border-amber-600/30"
                              >
                                Selengkapnya
                              </a>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-white/80">Tidak ada hasil untuk TF-IDF</p>
                )}
              </div>

              {/* SBERT SECTION */}
              <div className="backdrop-blur-lg bg-white/[0.02] border border-white/20 rounded-2xl p-8 shadow-lg hover:bg-white/[0.05] transition-all opacity-0 animate-fade-in-up" style={{ animationDelay: "0.4s" }}>
                <h2 className="text-2xl font-semibold text-white mb-6 drop-shadow-lg" style={{ fontFamily: "Poppins, serif" }}>
                  SBERT Results
                </h2>
                {getSBERTResults().length > 0 ? (
                  <div className="space-y-6">
                    {getSBERTResults().map((item, idx) => (
                      <div
                        key={`sbert-${idx}`}
                        className="bg-white/[0.03] backdrop-blur-lg border border-white/15 rounded-xl shadow-md hover:shadow-lg hover:bg-white/[0.08] transition-all group h-40 flex flex-col"
                      >
                        <div className="flex flex-col sm:flex-row items-start gap-3 p-3 flex-1 overflow-hidden">
                          {/* IMAGE WITH ROUNDED WRAPPER */}
                          <div className="w-full sm:w-32 h-32 flex-shrink-0 rounded-lg overflow-hidden bg-white/5">
                            <img
                              src={item["URL Gambar"] || "/images/placeholder.jpg"}
                              alt={item["Judul"] || "Item"}
                              className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                              onError={(e) => {
                                e.target.src = "/images/placeholder.jpg";
                              }}
                            />
                          </div>
                          
                          {/* CONTENT */}
                          <div className="flex-1 flex flex-col justify-between min-w-0">
                            <div>
                              <h3 className="font-semibold text-white mb-1 line-clamp-2 drop-shadow text-left text-sm">
                                {item["Judul"] || item["Judul Resep"] || "N/A"}
                              </h3>
                              <p className="text-xs text-white/70 mb-1 text-left">
                                {formatDate(item["Tanggal"]) }
                              </p>
                              <p className="text-xs text-white/80 text-left line-clamp-2">
                                {getDescription(item, 100)}
                              </p>
                            </div>
                            <div className="flex justify-between items-center pt-2 gap-2">
                              <span className="text-xs bg-green-400/30 backdrop-blur-sm border border-green-300/50 text-white px-2 py-1 rounded-full font-semibold whitespace-nowrap">
                                sbert: {(item["sbert_score"] || 0).toFixed(3)}
                              </span>
                              <a
                                href={item["URL Link"] || "#"}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="bg-amber-800/40 hover:bg-amber-700/50 text-white text-xs font-semibold px-3 py-1.5 rounded-md transition-all drop-shadow whitespace-nowrap border border-amber-600/30"
                              >
                                Selengkapnya
                              </a>
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-white/80">Tidak ada hasil untuk SBERT</p>
                )}
              </div>
            </div>
          </div>
        )}
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