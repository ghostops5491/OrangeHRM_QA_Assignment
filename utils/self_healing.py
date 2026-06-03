import json
from playwright.sync_api import Page, Locator
from utils.ai_client import AIClient
from utils.logger import get_logger

logger = get_logger(__name__)


class SelfHealingEngine:
    """Engine that uses Gemini to find corrected selectors for failed locators."""

    @staticmethod
    def extract_interactive_elements(page: Page) -> list:
        """Execute a JS script on the page to retrieve a clean, compact representation of interactive elements."""
        js_script = """
        () => {
            const elements = Array.from(document.querySelectorAll('input, button, select, a, [role="button"], [role="link"], [role="checkbox"], [role="textbox"], label, h1, h2, h3'));
            return elements.map(el => {
                // Get basic attributes
                const tagName = el.tagName.toLowerCase();
                const id = el.id || '';
                const className = el.className || '';
                const name = el.getAttribute('name') || '';
                const placeholder = el.getAttribute('placeholder') || '';
                const role = el.getAttribute('role') || '';
                const type = el.getAttribute('type') || '';
                
                // Get visible text content
                let text = (el.innerText || el.textContent || '').trim().replace(/\\s+/g, ' ');
                if (text.length > 100) {
                    text = text.substring(0, 100) + '...';
                }
                
                // Construct a simple identifier path for reference
                let cssPath = tagName;
                if (id) {
                    cssPath += '#' + id;
                } else if (className) {
                    // Grab first class
                    const firstClass = className.split(' ')[0];
                    if (firstClass && !firstClass.includes(':')) {
                        cssPath += '.' + firstClass;
                    }
                }
                
                return {
                    tag: tagName,
                    id: id,
                    name: name,
                    placeholder: placeholder,
                    role: role,
                    type: type,
                    text: text,
                    selector: cssPath
                };
            }).filter(item => {
                // Filter out items that are empty and lack key attributes
                return item.id || item.name || item.placeholder || item.text || item.role;
            });
        }
        """
        try:
            return page.evaluate(js_script)
        except Exception as e:
            logger.error(f"Failed to extract DOM elements: {e}")
            return []

    @staticmethod
    def find_alternative_locator(page: Page, failed_locator_str: str, error_message: str, screenshot_bytes: bytes) -> Locator | None:
        """Ask Gemini to find a corrected selector for the failed locator using the current page state."""
        logger.info(f"Analyzing failed locator: {failed_locator_str}")
        
        elements = SelfHealingEngine.extract_interactive_elements(page)
        elements_json_str = json.dumps(elements, indent=2)
        
        prompt = f"""
You are a test automation self-healing agent. A test using Playwright Python failed to find a specific element.
Original Locator representation: {failed_locator_str}
Error Message received: {error_message}

Your task is to analyze the list of interactive elements extracted from the current page DOM below, along with the screenshot provided, and identify which element is the correct substitute for the failing locator.

Here is the JSON list of interactive elements currently present on the page:
```json
{elements_json_str}
```

Please analyze the screenshot and the DOM elements list:
1. Identify the element that matches the intent of the original locator (e.g. if original was the username input box, find the input box for username).
2. Generate a valid, robust Playwright selector for this element. Prefer CSS selectors (e.g., "button[type='submit']", "input[name='username']", ".oxd-button") or basic text/XPath selectors that can be resolved by Playwright's page.locator() method.
3. Return your response in STRICT JSON format with no other text, wrapping, or markdown. Use this schema:
{{
  "found": true/false,
  "reason": "Explain why this element matches and what changed (e.g. name, placeholder, class change)",
  "new_locator_selector": "the Playwright selector string to use"
}}
"""
        
        # Invoke Gemini API
        response_text = AIClient.call_gemini(prompt, image_bytes=screenshot_bytes)
        logger.debug(f"Gemini Self-Healing Raw Response: {response_text}")
        
        # Clean up JSON from markdown if Gemini wraps it
        cleaned_response = response_text.strip()
        if cleaned_response.startswith("```json"):
            cleaned_response = cleaned_response[7:]
        if cleaned_response.endswith("```"):
            cleaned_response = cleaned_response[:-3]
        cleaned_response = cleaned_response.strip()
        
        try:
            result = json.loads(cleaned_response)
            if result.get("found") and result.get("new_locator_selector"):
                new_selector = result["new_locator_selector"]
                logger.info(f"Self-healing suggestion: {new_selector} (Reason: {result.get('reason')})")
                # Return the new locator
                return page.locator(new_selector)
            else:
                logger.warning(f"Self-healing could not find an alternative element: {result.get('reason')}")
                return None
        except Exception as e:
            logger.error(f"Failed to parse self-healing response JSON: {e}. Raw response: {response_text}")
            return None
