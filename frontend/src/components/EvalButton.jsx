import React, { useState } from "react";

export default function EvalButton() {
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  async function openEval() {
    console.log("EVALUASI DIKLIK");
    setOpen(true);
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:5000/evaluate", {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
          },
          body: JSON.stringify({
              query: "ayam goreng", 
              top_k: 20
          })
      });
      console.log("STATUS:", res.status);
      console.log("RAW:", await res.clone().text());
      const data = await res.json();
      setReport(data);
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
                          <div key={algo} className="bg-white/5 border border-white/10 rounded-lg p-4 hover:bg-white/8 transition-colors">
                            <h3 className="text-base font-semibold text-[#F3D9B1]">{algoName}</h3>
                            <div className="mt-3 text-sm text-white/70 space-y-2">
                              <div className="grid grid-cols-2 gap-4">
                                <div className="flex justify-between">
                                  <span>Runtime</span>
                                  <span className="text-white/90 font-medium">{report.metrics[algo].runtime_ms} ms</span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Precision</span>
                                  <span className="text-white/90 font-medium">{report.metrics[algo].precision}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span>Recall</span>
                                  <span className="text-white/90 font-medium">{report.metrics[algo].recall}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span>f-measure</span>
                                  <span className="text-white/90 font-medium">{report.metrics[algo].f1}</span>
                                </div>
                                <div className="flex justify-between">
                                  <span>MAP</span>
                                  <span className="text-white/90 font-medium">{report.metrics[algo].map}</span>
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
