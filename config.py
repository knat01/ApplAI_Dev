import os

def get_firebase_config():
    """
    Retrieves Firebase configuration from environment variables.

    Returns:
        dict: Firebase service account configuration.
    """
    firebase_config = {
        "type": "service_account",
        "project_id": os.environ.get("FIREBASE_PROJECT_ID"),
        "private_key_id": os.environ.get("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.environ.get("FIREBASE_PRIVATE_KEY", "").replace('\\n', '\n'),
        "client_email": os.environ.get("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.environ.get("FIREBASE_CLIENT_ID"),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": os.environ.get("FIREBASE_CLIENT_X509_CERT_URL")
    }
    # Remove any None values to avoid initialization errors
    firebase_config = {k: v for k, v in firebase_config.items() if v is not None}
    return firebase_config

def get_firebase_api_key():
    """
    Retrieves Firebase REST API key from environment variables.

    Returns:
        str: Firebase API key.
    """
    firebase_api_key = os.environ.get("FIREBASE_API_KEY")
    if not firebase_api_key:
        raise ValueError("FIREBASE_API_KEY environment variable is not set")
    return firebase_api_key

def get_openai_api_key():
    """
    Retrieves OpenAI API key from environment variables.

    Returns:
        str: OpenAI API key.
    """
    return os.environ.get("OPENAI_API_KEY", "")

def get_stripe_api_key():
    """
    Retrieves Stripe API key from environment variables.

    Returns:
        str: Stripe API key.
    """
    return os.environ.get("STRIPE_API_KEY", "")

def get_google_oauth_credentials():
    """
    Retrieves Google OAuth credentials from environment variables.

    Returns:
        dict: Google OAuth client ID and client secret.
    """
    return {
        "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
        "client_secret": os.environ.get("GOOGLE_CLIENT_SECRET", "")
    }

def get_redirect_uri():
    """
    Retrieves OAuth Redirect URI from environment variables.

    Returns:
        str: OAuth Redirect URI.
    """
    return os.environ.get("REDIRECT_URI", "http://localhost:8501/")  # Default to localhost if not set

def set_firebase_project_id():
    """
    Sets the GOOGLE_CLOUD_PROJECT environment variable with the Firebase Project ID.
    """
    project_id = os.environ.get("FIREBASE_PROJECT_ID")
    if project_id:
        os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
    else:
        raise ValueError("FIREBASE_PROJECT_ID environment variable is not set")

# Set GOOGLE_CLOUD_PROJECT environment variable
set_firebase_project_id()
