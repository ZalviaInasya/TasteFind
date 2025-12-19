from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import json
from query_engine import search
from evaluate import Evaluator

app = Flask(__name__)
CORS(app)

# Cache evaluation results in memory at startup (takes ~40 seconds once)
EVAL_CACHE = None
EVALUATOR = None


def get_evaluator():
    global EVALUATOR
    if EVALUATOR is None:
        EVALUATOR = Evaluator()
    return EVALUATOR

def init_eval_cache():
    """Initialize evaluation cache at app startup"""
    global EVAL_CACHE
    print("[INFO] Pre-computing evaluation metrics (this takes ~40 seconds)...")
    try:
        evaluator = get_evaluator()
        report = evaluator.evaluate()
        
        # Round metrics for display
        for algo, m in report["metrics"].items():
            m["runtime_ms"] = round(m["runtime_ms"], 4)
            m["precision"] = round(m["precision"], 4)
            m["recall"] = round(m["recall"], 4)
            m["f1"] = round(m["f1"], 4)
            m["map"] = round(m["map"], 4)
        
        EVAL_CACHE = report
        print("[INFO] ✓ Evaluation cache ready!")
    except Exception as e:
        print(f"[WARN] Failed to initialize eval cache: {e}")
        EVAL_CACHE = {"metrics": {}, "results": {}}

@app.route("/search", methods=["POST"])
def search_endpoint():
    """
    Search endpoint that returns results with both TF-IDF and SBERT score
    """
    try:
        data = request.json
        query = data.get("query", "")
        category = data.get("category", "semua")
        top_k = int(data.get("top_k", 10))  # default to top 10 results
        
        if not query:
            return jsonify({
                "error": "Query is required",
                "query": "",
                "category": category,
                "total_results": 0,
                "results": []
            }), 400
        
        # Perform search
        result = search(query, category, top_k=top_k)
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"[ERROR] Search endpoint failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "error": str(e),
            "query": data.get("query", ""),
            "category": data.get("category", "semua"),
            "total_results": 0,
            "results": []
        }), 500

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"}), 200


@app.route("/evaluate", methods=["GET"])
def evaluate_endpoint():
    """Serve in-memory cached evaluation results (instant!)"""
    if EVAL_CACHE is None:
        return jsonify({"error": "Evaluation cache not ready"}), 503
    return jsonify(EVAL_CACHE), 200


@app.route("/evaluate/query", methods=["POST"])
def evaluate_query_endpoint():
    """Evaluate a single query dynamically and return per-algo metrics"""
    try:
        data = request.json or {}
        query = data.get("query", "")
        top_k = int(data.get("top_k", 20))

        if not query:
            return jsonify({"error": "Query is required"}), 400

        evaluator = get_evaluator()
        result = evaluator.evaluate_query(query, algorithms=("tfidf", "sbert"), top_k=top_k)

        # Round some numbers for concise display
        for algo, m in result.get("metrics", {}).items():
            if "runtime_ms" in m:
                m["runtime_ms"] = round(m["runtime_ms"], 4)
            if "precision" in m:
                m["precision"] = round(m["precision"], 8)
            if "recall" in m:
                m["recall"] = round(m["recall"], 8)
            if "f1" in m:
                m["f1"] = round(m["f1"], 8)
            # Round both per-query AP and alias 'map' if present
            if "ap" in m:
                m["ap"] = round(m["ap"], 8)
            if "map" in m:
                m["map"] = round(m["map"], 8)

        return jsonify(result), 200
    except Exception as e:
        print(f"[ERROR] evaluate_query failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    init_eval_cache()
    app.run(debug=True, port=5000)

