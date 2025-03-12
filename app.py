from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from router import call_llm  # Import the call_llm function

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)  # Enable CORS for all routes

@app.route('/generate', methods=['POST', 'OPTIONS'])
def generate():
    if request.method == 'OPTIONS':
        return '', 200

    data = request.get_json()
    if not data or "prompt" not in data:
        return jsonify({"error": "Missing prompt in request"}), 400

    prompt = data["prompt"]
    response = call_llm(prompt)  # Call your LLM function
    return jsonify(response)

@app.route('/stats', methods=['GET'])
def stats():
    try:
        with open("logs.csv", "r") as file:
            logs = file.read()
        return jsonify({"logs": logs.splitlines()})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
