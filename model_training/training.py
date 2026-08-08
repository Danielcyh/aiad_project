from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load your trained AI model when the server starts
model = joblib.load('fraud_prediction_model.joblib')

@app.route('/predict', methods=['POST'])
def predict():
    try:
        # 1. Get the raw JSON data sent by the user/UI
        raw_data = request.json
        
        # 2. Convert the JSON into a Pandas DataFrame
        # (We wrap it in a list so Pandas knows it's a single row of data)
        df = pd.DataFrame([raw_data])
        
        # 3. Make the prediction! 
        # Because we saved a Pipeline, this automatically scales the numbers, 
        # encodes the text, and runs the Logistic Regression model.
        prediction = model.predict(df)
        
        # 4. Format the result and send it back to the user
        # prediction[0] will be 1 (Fraud) or 0 (Not Fraud)
        result = {
            "status": "success",
            "is_fraud": int(prediction[0]),
            "message": "Fraudulent Transaction Detected" if int(prediction[0]) == 1 else "Transaction Approved"
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        # If the user sends bad data, return an error safely
        return jsonify({"status": "error", "message": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)