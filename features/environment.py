import os
import datetime
import shutil
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
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    clean_scenario_name = "".join([c if c.isalnum() or c in (" ", "_", "-") else "" for c in scenario.name]).replace(" ", "_")
    
    # Store video files in reports/temp_videos during execution
    context.temp_video_dir = os.path.join("reports", "temp_videos")
    os.makedirs(context.temp_video_dir, exist_ok=True)
    
    context.browser_context = context.browser.new_context(
        record_video_dir=context.temp_video_dir,
        record_video_size={"width": 1920, "height": 1080}
    )
    
    # Start tracing with snapshots, screenshots, and sources
    context.browser_context.tracing.start(screenshots=True, snapshots=True, sources=True)
    
    context.page = context.browser_context.new_page()
    context.page.set_default_timeout(Config.TIMEOUT)
    context.page.set_viewport_size({"width": 1920, "height": 1080})
    
    # Console logs collector
    context.console_logs = []
    context.page.on("console", lambda msg: context.console_logs.append(f"[{msg.type}] {msg.text}"))
    
    context.scenario_timestamp = timestamp
    context.scenario_clean_name = clean_scenario_name
    
    logger.info(f"Browser {Config.BROWSER} launched with tracing and video recording enabled")


def after_scenario(context, scenario):
    failed = scenario.status.has_failed()
    
    # Attach failure screenshot
    if failed and hasattr(context, "page"):
        try:
            screenshot = context.page.screenshot()
            allure.attach(
                screenshot,
                name=f"Failure Screenshot: {scenario.name}",
                attachment_type=allure.attachment_type.PNG
            )
        except Exception as e:
            logger.error(f"Failed to capture failure screenshot: {e}")
            
    # Perform AI Failure Analysis
    if failed and Config.AI_FAILURE_ANALYSIS and hasattr(context, "page"):
        logger.info("Performing AI failure analysis using Gemini...")
        failed_step = None
        for step in scenario.steps:
            if step.status.has_failed():
                failed_step = step
                break
        
        step_info = ""
        if failed_step:
            step_info = f"Failed Step: {failed_step.keyword} {failed_step.name}\n"
            step_info += f"Error Message:\n{failed_step.error_message}\n"
            
        console_logs_str = "\n".join(context.console_logs[-20:])
        prompt = f"""
You are a senior QA automation engineer. A test scenario failed in our OrangeHRM BDD automation framework.
Scenario Name: {scenario.name}
{step_info}

Last 20 Browser Console Logs:
```
{console_logs_str}
```

Please analyze the failure screenshot and the error details above to:
1. Explain in clear, plain English what went wrong.
2. Provide a concrete, step-by-step recommendation on how to fix this issue (e.g. selector fix, wait/timeout adjustments, test data corrections, or application bug report).

Format your response in neat Markdown. Use headers, bullet points, and code blocks as appropriate.
"""
        try:
            screenshot_bytes = context.page.screenshot()
            from utils.ai_client import AIClient
            analysis_report = AIClient.call_gemini(prompt, image_bytes=screenshot_bytes)
            
            # Attach to Allure
            allure.attach(
                analysis_report,
                name="AI Failure Analysis Report",
                attachment_type=allure.attachment_type.TEXT
            )
            logger.info("AI failure analysis completed successfully.")
        except Exception as analysis_err:
            logger.error(f"Error generating AI failure analysis: {analysis_err}")

    # Trace and Video File Handling
    trace_path = None
    video_final_path = None
    
    # Reference to Playwright video path before context closes
    video = context.page.video if hasattr(context, "page") else None
    temp_video_path = video.path() if video else None
    
    # Stop tracing and save trace file on failure
    if hasattr(context, "browser_context"):
        if failed:
            os.makedirs(Config.TRACES_DIR, exist_ok=True)
            trace_path = os.path.join(Config.TRACES_DIR, f"trace_{context.scenario_clean_name}_{context.scenario_timestamp}.zip")
            try:
                context.browser_context.tracing.stop(path=trace_path)
                logger.info(f"Trace saved to: {trace_path}")
            except Exception as e:
                logger.error(f"Failed to save trace file: {e}")
                try:
                    context.browser_context.tracing.stop()
                except:
                    pass
        else:
            try:
                context.browser_context.tracing.stop()
            except:
                pass
                
        # Close the context
        try:
            context.browser_context.close()
        except Exception as e:
            logger.error(f"Failed to close browser context: {e}")

    # Close browser
    if hasattr(context, "browser"):
        try:
            context.browser.close()
            logger.info("Browser closed")
        except Exception as e:
            logger.error(f"Failed to close browser: {e}")

    # Manage video files
    if temp_video_path:
        if failed:
            os.makedirs(Config.VIDEOS_DIR, exist_ok=True)
            video_final_path = os.path.join(Config.VIDEOS_DIR, f"video_{context.scenario_clean_name}_{context.scenario_timestamp}.webm")
            try:
                if os.path.exists(temp_video_path):
                    shutil.move(temp_video_path, video_final_path)
                    logger.info(f"Video saved to: {video_final_path}")
            except Exception as e:
                logger.error(f"Failed to move video file: {e}")
        else:
            try:
                if os.path.exists(temp_video_path):
                    os.remove(temp_video_path)
            except Exception as e:
                logger.warning(f"Failed to delete successful execution video: {e}")

    # Cleanup temp videos directory if empty
    if hasattr(context, "temp_video_dir") and os.path.exists(context.temp_video_dir):
        try:
            if not os.listdir(context.temp_video_dir):
                os.rmdir(context.temp_video_dir)
        except:
            pass

    # Attach trace and video to Allure
    if failed:
        if trace_path and os.path.exists(trace_path):
            try:
                allure.attach.file(
                    trace_path,
                    name=f"Playwright Trace: {scenario.name}",
                    attachment_type=allure.attachment_type.ZIP
                )
            except Exception as e:
                logger.error(f"Failed to attach trace file to Allure: {e}")
        if video_final_path and os.path.exists(video_final_path):
            try:
                allure.attach.file(
                    video_final_path,
                    name=f"Execution Video: {scenario.name}",
                    attachment_type=allure.attachment_type.WEBM
                )
            except Exception as e:
                logger.error(f"Failed to attach video file to Allure: {e}")


def after_all(context):
    logger.info("Test suite completed")
    if hasattr(context, "playwright"):
        context.playwright.stop()

