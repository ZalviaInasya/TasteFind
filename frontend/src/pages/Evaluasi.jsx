import React, { useEffect, useState } from "react";

export default function Evaluasi() {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    async function fetchReport() {
      setLoading(true);
      try {
        const res = await fetch("http://localhost:5000/evaluate");
        if (!res.ok) throw new Error("Failed to fetch evaluation");
        const data = await res.json();
        setReport(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchReport();
  }, []);

  if (loading) return (
    <div className="p-8">
      <p>Loading evaluation...</p>
    </div>
  );

  if (error) return (
    <div className="p-8">
      <p className="text-red-500">Error: {error}</p>
    </div>
  );

  if (!report) return null;

  const metrics = report.metrics || {};

  return (
    <div className="max-w-3xl mx-auto p-6">
      <div className="bg-[#1f2130] text-white rounded-lg p-6 shadow-lg">
        <h2 className="text-2xl font-semibold mb-4">Evaluasi</h2>

        {Object.keys(metrics).map((algo) => (
          <div key={algo} className="mb-6 border-b border-white/10 pb-4">
            <h3 className="text-lg font-semibold capitalize">{algo} Similarity</h3>
            <div className="mt-2 text-sm text-white/80">
              <p>Runtime : {metrics[algo].runtime_ms} ms</p>
              <p>Precision : {metrics[algo].precision}</p>
              <p>Recall : {metrics[algo].recall}</p>
              <p>f-measure : {metrics[algo].f1}</p>
              <p>MAP : {metrics[algo].map}</p>
            </div>
          </div>
        ))}

      </div>
    </div>
  );
}
