from flask import Flask, request, jsonify
from flask_cors import CORS
from query_engine import search

app = Flask(__name__)
CORS(app)

@app.route("/search", methods=["POST"])
def search_endpoint():
    """
    Search endpoint that returns results with both TF-IDF and SBERT score
    """
    try:
        data = request.json
        query = data.get("query", "")
        category = data.get("category", "semua")
        top_k = data.get("top_k", 5)
        
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

if __name__ == "__main__":
    app.run(debug=True, port=5000)

