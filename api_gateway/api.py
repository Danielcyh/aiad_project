from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app) 

PREPROCESSOR_URL = "http://preprocessor-service:5001/clean"
PREPROCESSOR_CSV_URL = "http://preprocessor-service:5001/process-csv"
PREDICTION_URL = "http://prediction-service:5002/predict"

@app.route('/predict', methods=['POST'])
def overall_api():
    try:
        raw_data = request.get_json()
        
        prep_response = requests.post(PREPROCESSOR_URL, json=raw_data)
        
        if prep_response.status_code != 200:
            return jsonify({"error": "Failed at preprocessing stage"}), 500
            
        cleaned_data = prep_response.json()

        ai_response = requests.post(PREDICTION_URL, json=cleaned_data)
        
        if ai_response.status_code != 200:
            return jsonify({"error": "Failed at AI prediction stage"}), 500

        ai_result = ai_response.json()

        return jsonify({
            "message": "Transaction analyzed successfully through pipeline",
            "is_fraud": ai_result.get("is_fraud"),
            "message": "Fraudulent Transaction Detected" if ai_result.get("is_fraud") == 1 else "Transaction Approved"
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