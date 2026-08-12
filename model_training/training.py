from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load your trained AI model pipeline
model = joblib.load('fraud_prediction_model.joblib')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        raw_data = request.json
        df = pd.DataFrame([raw_data])
        
        prediction = model.predict(df)
        
        result = {
            "status": "success",
            "is_fraud": int(prediction[0]),
            "message": "Fraudulent Transaction Detected" if int(prediction[0]) == 1 else "Transaction Approved"
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/predict-batch', methods=['POST'])
def predict_batch():
    try:
        data = request.get_json()
        records = data.get('records', [])
        
        if not records:
            return jsonify({"status": "error", "message": "No records provided"}), 400
            
        # Convert list of cleaned dictionaries into a Pandas DataFrame
        df = pd.DataFrame(records)
        
        # Run batch predictions through the model pipeline
        predictions = model.predict(df)
        
        # Attach predictions and messages back to each record row
        df['is_fraud'] = [int(p) for p in predictions]
        df['prediction_message'] = df['is_fraud'].apply(
            lambda x: "Fraudulent Transaction Detected" if x == 1 else "Transaction Approved"
        )
        
        # Convert back to a list of dictionaries
        results = df.to_dict(orient='records')
        
        return jsonify({
            "status": "success",
            "results": results
        }), 200
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)