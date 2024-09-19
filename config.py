import os

# Firebase configuration
firebase_config = {
    "type": "service_account",
    "project_id": "ai-job-assistant",
    "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
    "private_key": os.environ.get("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n') if os.environ.get("FIREBASE_PRIVATE_KEY") else None,
    "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
    "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL")
}

# Remove None values from firebase_config
firebase_config = {k: v for k, v in firebase_config.items() if v is not None}

# OpenAI API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

# Stripe API key
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY", "")

# Flask secret key
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "default-secret-key")
