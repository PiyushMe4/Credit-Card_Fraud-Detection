from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import joblib
import numpy as np
import traceback

# RATE LIMITER
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="Safeguard Defense Center")
app.state.limiter = limiter

# Rate limit error handler
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return HTMLResponse(
        content="<h2>Too many requests. Please slow down.</h2>",
        status_code=429
    )

# SECURITY HEADERS MIDDLEWARE
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), camera=(), microphone=()"
        return response

app.add_middleware(SecurityHeadersMiddleware)

# CORS (Restricted for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# MULTI-MODEL REGISTRY
MODELS = {}
MODEL_NAMES = {
    "random_forest": "Random Forest",
    "xgboost": "XGBoost",
    "logistic_regression": "Logistic Regression"
}

MODEL_FILES = {
    "random_forest": "model_random_forest.pkl",
    "xgboost": "model_xgboost.pkl",
    "logistic_regression": "model_logistic_regression.pkl"
}

for key, filename in MODEL_FILES.items():
    try:
        MODELS[key] = joblib.load(filename)
        print(f"Loaded model: {key}")
    except Exception as e:
        print(f"WARNING: Could not load {key}: {e}")

# Fallback to legacy model
if not MODELS:
    try:
        MODELS["random_forest"] = joblib.load("credit_fraud_model.pkl")
        print("Loaded legacy model as random_forest fallback.")
    except Exception as e:
        print(f"CRITICAL: No models available: {e}")

# Load scaler
try:
    scaler = joblib.load('scaler.pkl')
except Exception as e:
    print(f"CRITICAL ERROR loading scaler: {e}")

templates = Jinja2Templates(directory="templates")

# INPUT VALIDATION
def validate_and_clamp(value, min_val=-50, max_val=50):
    """Clamp input to safe range to prevent adversarial injection."""
    try:
        v = float(value)
        return max(min_val, min(max_val, v))
    except (ValueError, TypeError):
        return 0.0

# ROUTES
@app.get("/", response_class=HTMLResponse)
@limiter.limit("30/minute")
async def home(request: Request):
    try:
        default_data = {f"V{i}": "0.0000" for i in range(1, 29)}
        default_data["Amount"] = "100.00"
        
        context = {
            "request": request,
            "form_data": default_data, 
            "prediction": None, 
            "risk_level": "0.00",
            "result_class": "",
            "available_models": MODEL_NAMES,
            "selected_model": "random_forest"
        }
        return templates.TemplateResponse(request, "index.html", context)
    except Exception as e:
        traceback.print_exc()
        return HTMLResponse(content=f"Setup Error: {str(e)}", status_code=500)

@app.post("/predict")
@limiter.limit("20/minute")
async def predict(request: Request):
    try:
        form_raw = await request.form()
        form_data = dict(form_raw)
        
        # Validate model choice (prevent injection)
        selected_model = form_data.get('model_choice', 'random_forest')
        if selected_model not in MODEL_FILES:
            selected_model = 'random_forest'
        
        model = MODELS.get(selected_model)
        if model is None:
            model = list(MODELS.values())[0]
            selected_model = list(MODELS.keys())[0]
        
        # Validate & clamp all inputs
        amount = validate_and_clamp(form_data.get('Amount', 0), 0, 50000)
        features = [validate_and_clamp(form_data.get(f'V{i}', 0)) for i in range(1, 29)]
        
        scaled_amount = scaler.transform([[amount]])[0][0]
        query = np.array(features + [scaled_amount]).reshape(1, -1)
        
        prediction = int(model.predict(query)[0])
        probability = float(model.predict_proba(query)[0][1])
        
        result_text = "FRAUD DETECTED" if prediction == 1 else "TRANSACTION SECURE"
        result_class = "fraud" if prediction == 1 else "secure"
        risk_level = f"{probability * 100:.2f}"
        
        context = {
            "request": request,
            "prediction": result_text,
            "result_class": result_class,
            "risk_level": risk_level,
            "form_data": form_data,
            "available_models": MODEL_NAMES,
            "selected_model": selected_model
        }
        return templates.TemplateResponse(request, "index.html", context)
    except Exception as e:
         traceback.print_exc()
         return templates.TemplateResponse(request, "index.html", {
            "request": request,
            "prediction": f"ERROR: {str(e)}",
            "result_class": "error",
            "risk_level": "0.00",
            "form_data": {},
            "available_models": MODEL_NAMES,
            "selected_model": "random_forest"
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
