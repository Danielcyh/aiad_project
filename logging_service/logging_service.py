import csv
from datetime import datetime
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

CSV_AUDIT_FILE = "deployment_audit_trail.csv"


def append_audit_log(cleaned_data: dict, prediction_result: dict) -> None:
  try:
    row_data = list(cleaned_data.values())
    prediction_val = prediction_result.get(
        "is_fraud", prediction_result.get("prediction", "N/A")
    )
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_row = row_data + [prediction_val, timestamp]

    file_exists = os.path.exists(CSV_AUDIT_FILE)

    with open(CSV_AUDIT_FILE, mode="a", newline="", encoding="utf-8") as file:
      writer = csv.writer(file)
      if not file_exists:
        headers = list(cleaned_data.keys()) + ["prediction", "timestamp"]
        writer.writerow(headers)
      writer.writerow(full_row)
  except Exception as e:
    print(f"Error writing to audit log: {str(e)}")
    raise e


@app.route("/log", methods=["POST"])
def log_transaction():
  try:
    payload = request.get_json()
    if (
        not payload
        or "cleaned_data" not in payload
        or "prediction_result" not in payload
    ):
      return jsonify({"error": "Invalid payload format."}), 400

    cleaned_data = payload["cleaned_data"]
    prediction_result = payload["prediction_result"]
    append_audit_log(cleaned_data, prediction_result)

    return (
        jsonify({
            "status": "success",
            "message": "Audit log recorded successfully.",
        }),
        200,
    )
  except Exception as e:
    return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5003)