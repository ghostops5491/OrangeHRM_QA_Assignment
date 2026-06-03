from playwright.sync_api import Page, Locator
from config.config import Config
from utils.logger import get_logger
from features.pages.components.sidebar_component import SidebarComponent

logger = get_logger(__name__)


class BasePage:
    def __init__(self, page: Page):
        self.page = page
        self.base_url = Config.BASE_URL
        self.sidebar = SidebarComponent(page)
    
    def navigate(self, path: str = ""):
        url = f"{self.base_url}{path}"
        logger.info(f"Navigating to {url}")
        self.page.goto(url, wait_until="domcontentloaded", timeout=Config.TIMEOUT)
    
    def _get_element(self, locator: Locator, timeout: int = Config.TIMEOUT) -> Locator:
        try:
            locator.wait_for(state="visible", timeout=timeout)
            return locator
        except Exception as e:
            if not Config.AI_SELF_HEALING:
                raise e
            
            logger.warning(f"Element visibility check failed for locator: {locator}. Starting AI self-healing...")
            try:
                screenshot_bytes = self.page.screenshot()
                from utils.self_healing import SelfHealingEngine
                healed_locator = SelfHealingEngine.find_alternative_locator(
                    self.page,
                    str(locator),
                    str(e),
                    screenshot_bytes
                )
                if healed_locator:
                    logger.info("AI self-healing suggested alternative locator. Waiting for it...")
                    healed_locator.wait_for(state="visible", timeout=timeout)
                    return healed_locator
            except Exception as healing_err:
                logger.error(f"Error during AI self-healing execution: {healing_err}")
                
            raise e

    def click(self, locator: Locator):
        el = self._get_element(locator)
        el.click()
    
    def fill(self, locator: Locator, text: str):
        el = self._get_element(locator)
        el.fill(text)
    
    def get_text(self, locator: Locator) -> str:
        el = self._get_element(locator)
        return el.text_content()
    
    def wait_for_element(self, locator: Locator, timeout: int = Config.TIMEOUT):
        self._get_element(locator, timeout=timeout)
    
    def is_visible(self, locator: Locator, timeout: int = 5000) -> bool:
        try:
            locator.wait_for(state="visible", timeout=timeout)
            return True
        except:
            return False

