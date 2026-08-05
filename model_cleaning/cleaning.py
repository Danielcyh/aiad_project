import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

def process_transaction(raw_data: dict) -> dict:
    """
    Standardizes keys, handles missing data, clamps outliers, and encodes text.
    """
    # Key Standardization
    key_aliases = {
        'amount': ['amount', 'txn_amt', 'transaction_value'],
        'transaction_hour': ['transaction_hour', 'hour', 'time_of_day'],
        'merchant_category': ['merchant_category', 'category', 'store_type'],
        'foreign_transaction': ['foreign_transaction', 'is_foreign'],
        'location_mismatch': ['location_mismatch', 'mismatch'],
        'cardholder_age': ['cardholder_age', 'age']
    }
    
    standardized_data = {}
    for official_key, aliases in key_aliases.items():
        for alias in aliases:
            if alias in raw_data:
                standardized_data[official_key] = raw_data[alias]
                break 

    # Outlier Handling for Age
    def get_valid_age(age_val):
        try:
            age = int(age_val)
            if age < 18: return 18       
            if age > 100: return 100      
            return age
        except (ValueError, TypeError):
            return 30

    # Categorical Encoding for Merchant
    raw_category = str(standardized_data.get('merchant_category', 'other')).strip().lower()
    category_mapping = {
        'electronics': 0, 'travel': 1, 'grocery': 2, 'food': 3, 'clothing': 4
    }
    encoded_category = category_mapping.get(raw_category, 99)

    # Final Type Enforcement & Default Fallbacks
    clean_payload = {
        'amount': round(float(standardized_data.get('amount', 0.0)),2),
        'transaction_hour': int(standardized_data.get('transaction_hour', 12)),
        'merchant_category': encoded_category,
        'foreign_transaction': int(standardized_data.get('foreign_transaction', 0)),
        'location_mismatch': int(standardized_data.get('location_mismatch', 0)),
        'cardholder_age': get_valid_age(standardized_data.get('cardholder_age'))
    }
    
    return clean_payload

# --- Manual Form Submission ---
@app.route('/clean', methods=['POST'])
def clean_data():
    raw_data = request.get_json()
    clean_payload = process_transaction(raw_data)
    return jsonify(clean_payload), 200

# --- CSV File Upload ---
@app.route('/process-csv', methods=['POST'])
def process_csv():
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
        
    file = request.files['file']
    
    try:
        # 1. Read the CSV file using Pandas
        df = pd.read_csv(file)
        
        # 2. Convert the dataframe into a list of dictionaries (rows)
        raw_records = df.to_dict(orient='records')
        
        # 3. Pass every row through your exact same cleaning function!
        cleaned_records = [process_transaction(row) for row in raw_records]
        
        return jsonify({
            "status": "success",
            "message": f"Successfully cleaned {len(cleaned_records)} rows from {file.filename}",
            "cleaned_data": cleaned_records
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Failed to process CSV: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)