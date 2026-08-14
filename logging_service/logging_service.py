import csv
from datetime import datetime, timedelta, timezone
import os
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


LOG_DIR = "/app/data"
os.makedirs(LOG_DIR, exist_ok=True)

CSV_AUDIT_FILE = os.path.join(LOG_DIR, "deployment_audit_trail.csv")


SGT_OFFSET = timezone(timedelta(hours=8))


def write_rows_to_csv(headers: list, rows: list):
  file_exists = os.path.exists(CSV_AUDIT_FILE)
  with open(CSV_AUDIT_FILE, mode="a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    if not file_exists:
      writer.writerow(headers)
    writer.writerows(rows)


@app.route("/log", methods=["POST"])
def log_transaction():
  try:
    payload = request.get_json()
    if not payload:
      return jsonify({"error": "Invalid payload format."}), 400

    timestamp = datetime.now(SGT_OFFSET).strftime("%Y-%m-%d %H:%M:%S")

    #  Batch CSV Processing Log
    if "records" in payload:
      records = payload["records"]
      if not records:
        return jsonify({"status": "success", "message": "Empty batch log."}), 200

      rows_to_write = []
      headers = None

      for record in records:
        rec_copy = dict(record)
        # Extract prediction output
        pred_val = rec_copy.pop("is_fraud", rec_copy.pop("prediction", "N/A"))
        rec_copy.pop(
            "prediction_message", None
        )  # remove UI status message if present

        if headers is None:
          headers = list(rec_copy.keys()) + ["prediction", "timestamp"]

        row_data = list(rec_copy.values()) + [pred_val, timestamp]
        rows_to_write.append(row_data)

      if headers and rows_to_write:
        write_rows_to_csv(headers, rows_to_write)

    # Single Manual Form Log
    elif "cleaned_data" in payload and "prediction_result" in payload:
      cleaned_data = payload["cleaned_data"]
      prediction_result = payload["prediction_result"]

      pred_val = prediction_result.get(
          "is_fraud", prediction_result.get("prediction", "N/A")
      )
      headers = list(cleaned_data.keys()) + ["prediction", "timestamp"]
      row_data = list(cleaned_data.values()) + [pred_val, timestamp]

      write_rows_to_csv(headers, [row_data])

    else:
      return jsonify({"error": "Unrecognized logging payload structure."}), 400

    return (
        jsonify({
            "status": "success",
            "message": "Audit log(s) recorded successfully.",
        }),
        200,
    )

  except Exception as e:
    print(f"Error writing to audit log: {str(e)}")
    return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5003)