  # Credit Card Fraud Detection System

This repository contains a containerized  **Credit Card Fraud Detection System** using **Docker Compose** and deployed on **Kubernetes (Minikube)**. The application splits machine learning processes into 4 decoupled, communicative microservices that interact sequentially over standard HTTP/REST protocols to evaluate live transactions and batch CSV uploads for potential fraud.

---

## Project Overview & Objectives

Traditional applications wrap user interfaces, data processing, and machine learning models in a single server. In environments like financial transaction processing, this creates tight coupling, blocking independent scaling and making the system vulnerable to single-point-of-failure issues.

### Objective

Develop a scalable, microservices-based AI application that ingests real-time transaction data and uses a machine learning model to detect and classify transactions as legitimate or fraudulent.

---

## Repository Directory Structure

```
aiad_project/
│
├── Dcoker-Compose.yml                
├── fraud_detection.yaml                
├── requirements.txt                  
│   
├── api_gateway/
│   ├── api.py                          # 
│   └── Dockerfile                      # 
│   
│
├── model_cleaning/
│   ├── cleaning.py                     # 
│   └── Dockerfile                      # 
│                
│
├── model_training/
│   ├── training.py                     #
│   ├── fraud_prediction_model.joblib   #
│   └── Dockerfile
│           
|
└── logger_service/
    ├── logging_service.py              #      
    └──  Dockerfile                     #
    
```

## Build, Run, and Deployment Instructions

### Deployment (Kubernetes via Minikube)
Follow this step-by-step workflow to deploy the microservice architecture into a local Kubernetes cluster.

#### 1. Routing
Ensure terminal is routed to the project folder
```bash
cd /<project folder>
```

#### 2. Start your local cluster
Ensure Minikube is started on your PC (or inside WSL) as well as Docker Desktop is running:
```bash
minikube start 
```

#### 3. Enter into Minikube's Docker Environment
Point your current terminal session to Minikube's Docker Environment:

- **Linux / WSL / Mac:**
  ```bash
  eval $(minikube docker-env)
  ```

#### 4. Build container images inside the Minikube environment
With the environment variables linked, navigate to your root project directory and build the images:
```bash
docker compose build
```

#### 5. Apply Kubernetes Manifests
Deploy the persistent storage resources, deployments, and routing services to your cluster using the Kubernetes YAML (`fraud_detection.yaml`):
```bash
kubectl apply -f fraud_detection.yaml
```

#### 6. Verify Pods, Services, and Storage
Ensure all elements have transitioned to a healthy state:
- **Check Pod Status (Wait for `1/1 Running`):**
  ```bash
  kubectl get pods
  ```
- **Check Storage (PVC must display `Bound` status):**
  ```bash
  kubectl get pvc
  ```

#### 7. Open the Network to the Gateway
Because internal cluster networks are isolated from your local operating system, open a network to route local traffic directly into the cluster's gateway-service:
```bash
kubectl port-forward svc/gateway-service 5000:5000
```
*Note: Keep this terminal window open and running, open new terminal to do addition commands*

Open your interface.html and You can now test manual entries or upload bulk CSV files!

---

## Microservice Architecture & Purpose
*Our group has decoupled the system into the following 4 services. Team members should complete the description, responsibilities, and API contract details for their respective sections:*

### 1. API Gateway (`gateway-service`)
- **Lead Developer:** `Muhammad Aslam`
- **Technology Stack:** `Python, Flask, Flask-CORS`
- **Purpose & Description:**
  The API Gateway is the single point of entry for out client applications. It uses Flask-CORS to handle Cross-Origin Resource Sharing for frontend compatibility and coordinates sequential execution pipelines across internal microservices. It decouples client requests from internal service architecture while handling error forwarding and logging dispatch.
- **API Endpoints & Contracts:**
  - `POST /predict`
    - **Request Payload:** `Raw JSON object containing unstandardized transaction details`
    - **Response Payload:** `JSON object containing the pipeline execution status and final fraud prediction outcome`
  - `POST /upload-csv`
    - **Request Payload:** `Multipart/form-data containing the uploaded CSV file`
    - **Response:** `JSON object containing batch processing status and prediction results for all records`
  - `POST /download-csv`
    - **Request Payload:** `None`
    - **Response:** `Binary CSV file stream containing the complete deployment audit trail`

---

### 2. Data Preprocessor (`preprocessor-service`)
- **Lead Developer:** `Hoon Yao Hong`
- **Technology Stack:** `Python, Pandas, Flask`
- **Purpose & Description:**
  This service acts as the data cleaning station between the API Gateway and the Machine Learning model. It uses Pandas to standardize inconsistent iformatting (e.g., mapping `txn_amt` to `amount`). It handles outliers by clamping `cardholder_age` values between 18 and 100 and defaulting invalid entries to 30. Furthermore, it sanitizes categorical strings like `merchant_category` by validating against a strict list of accepted categories and defaulting unrecognized inputs to 'Other', ensuring the OneHotEncoder can process the data without any isses. At the end, it enforces strict type conversion (float/int) across all features before passing them forward.
- **API Endpoints & Contracts:**
  - `POST /clean`
    - **Request Payload:** `Raw JSON object containing unstandardized transaction data`
    - **Response Payload:** `Cleaned JSON object with standardized keys, defaults applied, and enforced data types`
  - `POST /process-csv`
    - **Request Payload:** `Contain CSV file uploaded`
    - **Response Payload:** `JSON object containing the batch processing status, a summary message, and an array of cleaned transaction objects`

---

### 3. AI Prediction Engine (`prediction-service`)
- **Lead Developer:** `[INSERT NAME]`
- **Technology Stack:** `[INSERT FLOW/FRAMEWORK, e.g., Python/Scikit-Learn/Joblib]`
- **Purpose & Description:**
  *(Group to fill out: Describe how the machine learning pipeline is loaded from a frozen serialized joblib binary, how predictions are processed in batches, and how prediction keys are attached to datasets)*
- **API Endpoints & Contracts:**
  - `POST /predict`
    - **Request Payload:** `[INSERT SCHEMA]`
    - **Response Payload:** `[INSERT SCHEMA]`
  - `POST /predict-batch`
    - **Request Payload:** `[INSERT SCHEMA]`
    - **Response Payload:** `[INSERT SCHEMA]`

---

### 4. Audit Logging Service (`logging-service`)
- **Lead Developer:** `[INSERT NAME]`
- **Technology Stack:** `[INSERT FLOW/FRAMEWORK, e.g., Flask/SQLite]`
- **Purpose & Description:**
  *(Group to fill out: Explain how transactions and model predictions are saved asynchronously, how the service interacts with persistent volume mounts, and why the gateway protects transactions from database service downtime)*
- **API Endpoints & Contracts:**
  - `POST /log`
    - **Request Payload:** `[INSERT SCHEMA]`
    - **Response Payload:** `[INSERT SCHEMA]`

---

## Dataset Information & Sources

The system is trained and validated on a transaction dataset containing 10,000 credit card records:
- **File Name:** `credit_card_fraud_10k.csv`
- **URL:** `https://www.kaggle.com/datasets/miadul/credit-card-fraud-detection-dataset`
- **Features Used:**
  1. `amount` (float): Transaction amount in USD.
  2. `transaction_hour` (int): Hour of the day the transaction occurred (0-23).
  3. `merchant_category` (string/categorical): Merchant segment (Grocery, Food, Electronics, Clothing, Travel, Other).
  4. `cardholder_age` (int): Age of the cardholder (clamped between 18 and 100 in the preprocessor).
  5. `foreign_transaction` (binary, 0 or 1): Indicator of whether the transaction was processed internationally.
  6. `location_mismatch` (binary, 0 or 1): Indicator of a discrepancy between billing address and IP location.
  7. `device_trust_score` (int, default=80): Simulated score representing terminal hardware safety.
  8. `velocity_last_24h` (int, default=1): Number of transactions initiated on the card within the last day.
- **Target Feature:** `is_fraud` (binary, 0 = Safe, 1 = Fraudulent).

---

## Known Issues & Limitations
- **Synchronous Coupling & Cascading Failures:** Our API Gateway uses blocking HTTP requests to chain all our microservices sequentially. If there is any single downstream container crashes or times out, the entire request aborts and returns a 500 error.
- **Lack of Security and Access Controls:** The endpoints are exposed publicly with CORS enabled and without authentication or rate limiting. Any client on the network can trigger batch predictions or download full audit trails containing transaction logs.
- **Hardcoded UI Parameters:** The interface has hardcoded device_trust_score to 80 and velocity_last_24h to 1 during the single-transaction submissions. Users cannot evaluate transactions involving varying device safety levels or rapid transaction counts through the web interface.