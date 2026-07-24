from flask import Flask, request, jsonify
import requests

app = Flask(__name__)
PREPROCESSOR_URL = "http://preprocessor-service:5001/clean"

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)