import allure
from playwright.sync_api import sync_playwright
from behave.model import Scenario, Status
from config.config import Config
from utils.logger import get_logger

logger = get_logger(__name__)


def before_all(context):
    logger.info("Starting test suite")
    context.playwright = sync_playwright().start()

    # Monkeypatch Scenario.run to implement global retries (original run + 2 retries)
    original_run = Scenario.run

    def retrying_run(self, runner):
        max_attempts = 3  # 1 original attempt + 2 retries
        for attempt in range(1, max_attempts + 1):
            if attempt > 1:
                logger.info(f"Retrying scenario '{self.name}' (Attempt {attempt}/{max_attempts}) due to failure")
            
            # Execute original run
            result = original_run(self, runner)
            
            # If scenario passed, or was skipped/untested, return immediately
            if not self.status.has_failed() and not self.hook_failed:
                if attempt > 1 and self.status == Status.passed:
                    logger.info(f"Scenario '{self.name}' PASSED on retry attempt {attempt}")
                return result
            
            if attempt == max_attempts:
                logger.error(f"Scenario '{self.name}' FAILED after {max_attempts} attempts")
                return result
            
            # Reset scenario and step statuses before retrying
            self.reset()
            for step in self.all_steps:
                step.status = None
                step.exception = None
                step.error_message = None
                step.duration = 0.0

        return result

    Scenario.run = retrying_run



def before_scenario(context, scenario):
    logger.info(f"Starting scenario: {scenario.name}")
    
    browser_type = context.playwright[Config.BROWSER]
    context.browser = browser_type.launch(headless=Config.HEADLESS)
    context.page = context.browser.new_page()
    context.page.set_default_timeout(Config.TIMEOUT)
    context.page.set_viewport_size({"width": 1920, "height": 1080})
    logger.info(f"Browser {Config.BROWSER} launched")


def after_scenario(context, scenario):
    if scenario.status.has_failed():
        logger.error(f"Scenario failed: {scenario.name}")
        if hasattr(context, "page"):
            screenshot = context.page.screenshot()
            allure.attach(
                screenshot,
                name=f"Failed scenario: {scenario.name}",
                attachment_type=allure.attachment_type.PNG
            )
    
    if hasattr(context, "browser"):
        context.browser.close()
        logger.info("Browser closed")


def after_all(context):
    logger.info("Test suite completed")
    if hasattr(context, "playwright"):
        context.playwright.stop()
