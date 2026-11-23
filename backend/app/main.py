import os
from dotenv import load_dotenv

load_dotenv()

def main():
    app_name = os.getenv("APP_NAME", "My Python App")
    print(f"Running {app_name}...")

if __name__ == "__main__":
    main()
