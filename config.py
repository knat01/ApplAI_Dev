import os

# Firebase configuration
firebase_config = {
    "type": "service_account",
    "project_id": "ai-job-assistant",
    "private_key_id": "your-private-key-id",
    "private_key": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-xxxxx@ai-job-assistant.iam.gserviceaccount.com",
    "client_id": "your-client-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40ai-job-assistant.iam.gserviceaccount.com"
}

# OpenAI API key
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# Stripe API key
STRIPE_API_KEY = os.environ.get("STRIPE_API_KEY")

# Flask secret key
FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "your-secret-key")
