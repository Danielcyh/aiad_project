# import neccessary library
from flask import Flask, request, jsonify # Flask create the app, request handle the incoming data, jsonify format output into JSON
from flask_cors import CORS # cross origin sharing allow web page to communicate with each other
import joblib # load the model in
import pandas as pd

app = Flask(__name__)
CORS(app)

# Load trained AI model pipeline
model = joblib.load('fraud_prediction_model.joblib')

'''
request for the data preprocess in data preprocessing for manual entries, 
do prediction using the AI model if ok return 200 if not return 400 error message

'''
# MANUAL ENTRY 
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

'''
request for the data preprocess in data preprocessing for csv upload, 
do prediction using the AI model and after that attached the predicted value 1 or 0 back to each row 
and uses lambda to translate 1 and 0 into messages as well as
if if ok return 200 if not return 400 error message

'''
# BATCH CSV UPLOAD 
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