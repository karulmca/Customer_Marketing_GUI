import os
from dotenv import load_dotenv

# Try to load .env from current directory
env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
    load_dotenv(env_path)
    print(f"Loaded .env from: {env_path}")
else:
    print(f".env file not found at: {env_path}")

# Print key environment variables
for key in ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME']:
    value = os.getenv(key)
    print(f"{key}: {value}")

# Indicate if all variables are present
missing = [k for k in ['DB_HOST', 'DB_USER', 'DB_PASSWORD', 'DB_NAME'] if os.getenv(k) is None]
if missing:
    print(f"Missing variables: {', '.join(missing)}")
else:
    print("All required variables found.")
