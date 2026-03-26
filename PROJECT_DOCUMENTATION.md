# 🛡️ Project Documentation: Ironclad Fraud Safeguard

## 1. Project Overview

The **Ironclad Fraud Safeguard** is a production-ready, high-security web application designed to detect fraudulent credit card transactions in real-time. By transforming a complex 28-feature PCA dataset into an intuitive, behavioral-based dashboard, the project allows non-technical users to simulate and verify fraud detection capabilities across three distinct machine learning architectures.

---

## 2. Machine Learning Pipeline (`Credit Card Fraud Detection.ipynb`)

### **Dataset Architecture**

- **Source**: Anonymized European credit card transactions (284,807 records).
- **Features**: 28 PCA-transformed behavioral signals (V1-V28) + Transaction Amount.
- **Class Balance**: Highly imbalanced (0.17% fraud).

### **Data Engineering**

1. **Normalization**: The `Amount` feature is standardized using `StandardScaler` to match the scale of PCA components.
2. **Feature Removal**: The `Time` component is discarded as it serves as a sequential index rather than a behavioral predictor.
3. **Leakage Prevention**: The dataset is split into training (70%) and testing (30%) sets _before_ any resampling occurs, ensuring the model never sees synthetic data during evaluation.
4. **Resampling (SMOTE)**: Synthetic Minority Over-sampling Technique is applied exclusively to the **training set** to balance classes, allowing the models to learn complex fraud patterns without underfitting.

### **The Triple-Engine Suite**

The system currently trains and serves three distinct models:

1.  🟦 **Random Forest**: An ensemble of 100 decision trees. High robustness and excellent at capturing non-linear relationships.
2.  🟡 **XGBoost**: Extreme Gradient Boosting. Optimized for predictive speed and competitive accuracy on structured data.
3.  🟣 **Logistic Regression**: A high-speed statistical baseline. Useful for linear behavioral patterns and instant inference.

---

## 3. Web Application Architecture (`app.py`)

### **Core Stack**

- **Engine**: FastAPI (High-performance Python web framework).
- **Frontend**: Jinja2 Templating with Vanilla CSS (Glassmorphism design).
- **Inference**: Joblib for dynamic model loading and real-time prediction.

### **Enterprise-Grade Security Shell**

To ensure the app is resistant to common web attacks, several security layers are integrated:

- **Rate Limiting (SlowAPI)**: Protects against Brute-Force and DoS attacks by limiting users to 20 scans per minute.
- **Security Headers**: Implements HSTS, X-Frame-Options (Deny), X-Content-Type-Options (No-Sniff), and XSS Protection.
- **CORS Hardening**: Restricts browser requests to local development origins.
- **Input Sanitization**: All user inputs (sliders/amount) are validated and clamped to strict ranges `[-50.0, 50.0]` to prevent adversarial overflow or injection.
- **Parameter Whitelisting**: The model selection mechanism is validated against a strict internal registry to prevent malicious parameter tampering.

---

## 4. UI/UX & Interaction Design (`index.html`)

### **The "Neuro-Defense" Dashboard**

- **Glassmorphism Design**: A premium dark-mode interface utilizing backdrop blurs and radial gradients for a modern technical feel.
- **Behavioral Sliders**: Raw numeric V-features are replaced with human-readable labels (e.g., "Location Regularity," "Hardware Link"), allowing users to set up a behavioral profile intuitively.
- **Real-Time Legends**: Contextual labels like _"Home Region"_ vs. _"Extreme Distance"_ update as the user interacts, teaching them how behavioral variance impacts risk.
- **Multi-Engine Switcher**: A dynamic selector allows users to choose which ML engine (RF, XGB, or LR) runs the profile scan.
- **Color-Coded Verdicts**: VERDICT results are visually distinct (🟦 Secure vs. 🟥 Fraud) with an accompanying model-specific badge.

### **Standard Model Verifier (Benchmarks)**

Integrated testing suite for instant model validation:

- **Routine Habit Check**: Sets a perfect "normal" profile to confirm the model's ability to recognize safe usage.
- **Master Identity Theft**: Synchronizes 10 critical signals to extreme fraud values to prove detection accuracy.
- **Behavioral Drift**: Simulates a "suspicious but low-confidence" scenario to test model sensitivity.

---

## 5. Deployment & Execution

1. **Dependencies**: `pip install -r requirements.txt` (FastAPI, Scikit-Learn, XGBoost, etc.).
2. **Training**: Run the first cell of `Credit Card Fraud Detection.ipynb` to generate `model_*.pkl` files.
3. **Execution**: Run `python app.py` to start the server at `127.0.0.1:8000`.
