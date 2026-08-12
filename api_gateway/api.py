from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

PREPROCESSOR_URL = "http://preprocessor-service:5001/clean"
PREPROCESSOR_CSV_URL = "http://preprocessor-service:5001/process-csv"
PREDICTION_URL = "http://prediction-service:5002/predict"
PREDICTION_CSV_URL = "http://prediction-service:5002/predict-batch"
LOGGING_URL = "http://logging-service:5003/log"


@app.route("/predict", methods=["POST"])
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

    # Safely forward inputs and output to the separate logging container
    try:
      logging_payload = {
          "cleaned_data": cleaned_data,
          "prediction_result": ai_result,
      }
      requests.post(LOGGING_URL, json=logging_payload, timeout=2)
    except Exception as log_err:
      print(f"Warning: Logging service unreachable: {log_err}")

    return (
        jsonify({
            "message": "Transaction analyzed successfully through pipeline",
            "is_fraud": ai_result.get("is_fraud"),
            "message": (
                "Fraudulent Transaction Detected"
                if ai_result.get("is_fraud") == 1
                else "Transaction Approved"
            ),
        }),
        200,
    )

  except Exception as e:
    return jsonify({"error": str(e)}), 500

@app.route("/upload-csv", methods=["POST"])
def upload_csv():
  if "file" not in request.files:
    return jsonify({"error": "No file provided"}), 400

  file = request.files["file"]

  try:
    files = {"file": (file.filename, file.stream, file.content_type)}
    prep_response = requests.post(PREPROCESSOR_CSV_URL, files=files)

    if prep_response.status_code != 200:
      return jsonify({"error": "Failed at CSV preprocessing stage"}), 500

    prep_json = prep_response.json()
    cleaned_records = prep_json.get("cleaned_data", [])

    if not cleaned_records:
      return jsonify({"error": "No records found in cleaned CSV data"}), 400

    ai_response = requests.post(
        PREDICTION_CSV_URL, json={"records": cleaned_records}
    )

    if ai_response.status_code != 200:
      return jsonify({"error": "Failed at AI batch prediction stage"}), 500

    ai_result = ai_response.json()
    return jsonify(ai_result), 200

  except Exception as e:
    return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000)