import React, { useState } from "react";

export default function EvalButton() {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);
  const [query, setQuery] = useState("");

  async function openEval() {
    console.log("EVALUASI DIKLIK");
    setOpen(true);
    setError(null);

    // Load cached eval and last search
    let cached = null;
    let lastSearch = null;

    try {
      const rawCached = localStorage.getItem("tastefind:last_eval");
      if (rawCached) cached = JSON.parse(rawCached);
    } catch (e) {
      console.warn("Failed to parse cached eval", e);
    }

    try {
      lastSearch = localStorage.getItem("tastefind:last_search");
    } catch (e) {}

    // If cached eval matches last search, use it immediately
    if (cached && cached.query && lastSearch && cached.query === lastSearch) {
      setQuery(cached.query || "");
      setReport(cached.result || null);
      return;
    }

    // If we have a last search query but no matching cached eval, auto-run evaluation
    if (lastSearch) {
      setQuery(lastSearch);
      // start evaluation and show loading state
      setReport(null);
      setLoading(true);
      try {
        await runEval(lastSearch);
      } finally {
        setLoading(false);
      }
      return;
    }

    // Fallback: no cached report and no previous search
    setReport(null);
  }

  async function runEval(q) {
    const qToUse = (typeof q === "string" && q.trim()) ? q.trim() : (query || "");
    if (!qToUse) {
      setError("Silakan masukkan query untuk dievaluasi");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:5000/evaluate/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query: qToUse, top_k: 20 }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(`Status ${res.status}: ${text}`);
      }
      const data = await res.json();
      setReport(data);
      setQuery(qToUse);
      try {
        localStorage.setItem("tastefind:last_eval", JSON.stringify({ query: qToUse, result: data, ts: Date.now() }));
        localStorage.setItem("tastefind:last_search", qToUse);
      } catch (e) {}
    } catch (err) {
      setError(err.message || "Failed to fetch evaluation");
    } finally {
      setLoading(false);
    }
  }

  function closeModal() {
    setOpen(false);
    setReport(null);
    setError(null);
  }

  return (
    <>
      {/* Floating glass button (bottom-right) with glassmorphism */}
      <button
        onClick={openEval}
        aria-label="Open evaluation"
        className="fixed right-6 bottom-6 z-50 w-14 h-14 rounded-2xl bg-gradient-to-br from-white/15 via-white/5 to-transparent backdrop-blur-lg border border-white/20 shadow-xl shadow-[#6E4A3E]/20 flex items-center justify-center hover:scale-110 hover:from-white/25 hover:via-white/10 hover:shadow-xl hover:shadow-[#6E4A3E]/40 transition-all duration-300 group"
        title="Open Evaluation"
      >
        {/* Animated inner glow */}
        <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-[#F3D9B1]/10 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
        
        {/* Inline SVG icon */}
        <svg width="28" height="28" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg" className="relative z-10">
          <rect x="3" y="3" width="18" height="18" rx="4" stroke="#F3D9B1" strokeWidth="1.5" />
          <path d="M8 12h8" stroke="#F3D9B1" strokeWidth="1.6" strokeLinecap="round" />
          <path d="M8 8h8" stroke="#F3D9B1" strokeWidth="1.6" strokeLinecap="round" />
          <path d="M8 16h5" stroke="#F3D9B1" strokeWidth="1.6" strokeLinecap="round" />
        </svg>
      </button>

      {/* Modal overlay with blur */}
      {open && (
        <div className="fixed inset-0 z-50 flex items-center justify-center px-4 backdrop-blur-sm">
          <div className="absolute inset-0 bg-black/35" onClick={closeModal} />

          <div className="relative w-full max-w-2xl">
            {/* Glassmorphism card */}
            <div className="bg-gradient-to-br from-white/10 via-white/5 to-transparent backdrop-blur-xl border border-white/20 rounded-2xl p-7 shadow-2xl text-white overflow-hidden">
              {/* Decorative blur background */}
              <div className="absolute inset-0 bg-gradient-to-br from-[#6E4A3E]/5 to-transparent pointer-events-none" />

              <div className="relative z-10">
                {/* Header */}
                <div className="flex items-start justify-between mb-5">
                  <h2 className="text-3xl font-bold bg-gradient-to-r from-[#F3D9B1] to-[#E6C9A8] bg-clip-text text-transparent">Evaluasi</h2>
                  <button 
                    onClick={closeModal} 
                    className="text-white/60 hover:text-white/90 transition-colors text-2xl font-light"
                  >
                    ✕
                  </button>
                </div>

                {/* Content */}
                <div className="mt-6 min-h-[120px]">
                  {/* Show query header when we have a cached or running report, otherwise show input */}
                  {(report || loading || query) ? (
                    <div className="mb-4">
                      <div className="rounded-md bg-white/5 border border-white/10 px-4 py-3 flex items-center gap-3">
                        <span className="text-sm text-white/70">Query:</span>
                        <span className="font-semibold text-[#F3D9B1]">"{query}"</span>
                      </div>
                    </div>
                  ) : (
                    <div className="flex gap-3 mb-4">
                      <input
                        className="flex-1 px-3 py-2 rounded-lg bg-white/6 text-white outline-none"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        placeholder="Masukkan query untuk evaluasi atau gunakan hasil pencarian terakhir"
                      />
                      <button onClick={() => runEval()} className="px-4 py-2 bg-[#6E4A3E] rounded-lg font-semibold">Jalankan</button>
                    </div>
                  )}
                  {loading && (
                    <div className="flex items-center gap-3">
                      <div className="w-4 h-4 rounded-full bg-[#F3D9B1] animate-pulse" />
                      <p className="text-white/70">Loading evaluation... (first run may take time)</p>
                    </div>
                  )}
                  {error && (
                    <div className="bg-red-500/20 border border-red-500/40 rounded-lg p-3">
                      <p className="text-red-300 text-sm">⚠ Error: {error}</p>
                    </div>
                  )}

                  {report && report.metrics && (
                    <div className="space-y-4">
                      {Object.keys(report.metrics).map((algo) => {
                        const algoName = algo === "tfidf" ? "TF-IDF Cosine Similarity" : "SBERT Cosine Similarity";
                        return (
                          <div key={algo} className="bg-white/5 border border-white/10 rounded-lg p-3 hover:bg-white/8 transition-colors">
                            <div className="flex items-start justify-between">
                            <h3 className="text-xl md:text-2xl font-extrabold text-[#F3D9B1] drop-shadow-sm" style={{ fontFamily: "Poppins, serif" }}>{algoName}</h3>
                            <div className="text-sm text-white/70 flex items-center gap-2">
                              {/* small clock icon */}
                              <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4 text-white/70" viewBox="0 0 24 24" fill="none" stroke="#F3D9B1" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
                                <circle cx="12" cy="12" r="9" />
                                <path d="M12 7v6l4 2" />
                              </svg>
                              <span className="font-medium text-white/90">{(report.metrics[algo].runtime_ms/1000).toFixed(4)} sec</span>
                            </div>
                          </div>

                          <div className="mt-4">
                            <div className="max-w-[620px] mx-auto text-sm text-white/70">
                              <div className="space-y-2">
                                <div className="grid grid-cols-[1fr_auto] items-center gap-2">
                                  <span className="text-base text-[#F3D9B1]">Precision</span>
                                  <span className="font-semibold text-white/90">{Number(report.metrics[algo].precision || 0).toFixed(8)}</span>
                                </div>
                                <div className="grid grid-cols-[1fr_auto] items-center gap-2">
                                  <span className="text-base text-[#F3D9B1]">Recall</span>
                                  <span className="font-semibold text-white/90">{Number(report.metrics[algo].recall || 0).toFixed(8)}</span>
                                </div>
                                <div className="grid grid-cols-[1fr_auto] items-center gap-2">
                                  <span className="text-base text-[#F3D9B1]">F1-Score</span>
                                  <span className="font-semibold text-white/90">{Number(report.metrics[algo].f1 || 0).toFixed(8)}</span>
                                </div>
                                <div className="grid grid-cols-[1fr_auto] items-center gap-2">
                                  <span className="text-base text-[#F3D9B1]">MAP</span>
                                  <span className="font-semibold text-white/90">{Number(report.metrics[algo].map || 0).toFixed(8)}</span>
                                </div>
                              </div>
                            </div>
                          </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
