import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    BASE_URL = os.getenv("BASE_URL", "https://opensource-demo.orangehrmlive.com")
    API_BASE_URL = os.getenv("API_BASE_URL", "https://opensource-demo.orangehrmlive.com/web/index.php")
    BROWSER = os.getenv("BROWSER", "chromium")
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    TIMEOUT = int(os.getenv("TIMEOUT", "60000"))
    
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "Admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
    
    PARALLEL_WORKERS = int(os.getenv("PARALLEL_WORKERS", "3"))
    ALLURE_RESULTS_DIR = os.getenv("ALLURE_RESULTS_DIR", "reports/allure-results")
    LOGS_DIR = os.getenv("LOGS_DIR", "logs")
    
    # AI and Resiliency Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    AI_SELF_HEALING = os.getenv("AI_SELF_HEALING", "true").lower() == "true"
    AI_FAILURE_ANALYSIS = os.getenv("AI_FAILURE_ANALYSIS", "true").lower() == "true"
    TRACES_DIR = os.getenv("TRACES_DIR", "reports/traces")
    VIDEOS_DIR = os.getenv("VIDEOS_DIR", "reports/videos_failures")
    AUTO_OPEN_REPORT = os.getenv("AUTO_OPEN_REPORT", "true").lower() == "true"


