import os

ALMONDS_ENV = os.getenv("ALMONDS_ENVIRONMENT", "sandbox").lower() == "production"
