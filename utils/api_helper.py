import requests
from config.config import Config
from utils.logger import get_logger
from playwright.sync_api import Page

logger = get_logger(__name__)


class APIHelper:
    def __init__(self, base_url: str = Config.BASE_URL):
        self.base_url = base_url
        self.session = requests.Session()
    
    def login_and_set_cookies(self, page: Page, username: str = Config.ADMIN_USERNAME, password: str = Config.ADMIN_PASSWORD):
        """
        Logs in via API and sets cookies on the Playwright page for authenticated session
        """
        logger.info(f"Starting API login flow for username: {username}")
        
        # 1. First navigate to get initial cookies and CSRF token
        login_page_url = f"{self.base_url}/web/index.php/auth/login"
        response = self.session.get(login_page_url)
        response.raise_for_status()
        
        # 2. Send login request to validate credentials
        validate_url = f"{self.base_url}/web/index.php/auth/validate"
        payload = {
            "username": username,
            "password": password
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": self.base_url,
            "Referer": login_page_url
        }
        
        login_response = self.session.post(validate_url, data=payload, headers=headers, allow_redirects=True)
        login_response.raise_for_status()
        
        # 3. Get cookies from the requests session
        cookies = []
        for cookie in self.session.cookies:
            cookies.append({
                "name": cookie.name,
                "value": cookie.value,
                "domain": cookie.domain,
                "path": cookie.path,
                "expires": -1 if cookie.expires is None else cookie.expires,
                "httpOnly": cookie.has_nonstandard_attr("HttpOnly"),
                "secure": cookie.secure
            })
        
        # 4. Set cookies on Playwright page
        page.context.add_cookies(cookies)
        logger.info("API login successful and cookies set on Playwright page")
        
        return cookies
    
    def get_employees(self):
        logger.info("Fetching employees via API")
        url = f"{self.base_url}/web/index.php/api/v2/pim/employees"
        response = self.session.get(url)
        response.raise_for_status()
        return response.json()
