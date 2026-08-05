from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app) 

# The internal Docker network URLs to reach your Preprocessor
PREPROCESSOR_URL = "http://preprocessor-service:5001/clean"
PREPROCESSOR_CSV_URL = "http://preprocessor-service:5001/process-csv"

# --- Handles the Manual Input Form ---
@app.route('/submit-transaction', methods=['POST'])
def submit_transaction():
    try:
        raw_data = request.get_json()
        
        response = requests.post(PREPROCESSOR_URL, json=raw_data)
        
        if response.status_code != 200:
            return jsonify({"error": "Failed at preprocessing stage"}), 500
            
        result = response.json()
        return jsonify({
            "message": "Transaction processed successfully through microservices pipeline",
            "pipeline_result": result
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Handles the CSV File Upload ---
@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    try:
        files = {'file': (file.filename, file.stream, file.content_type)}
        
        response = requests.post(PREPROCESSOR_CSV_URL, files=files)
        
        return jsonify(response.json()), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)