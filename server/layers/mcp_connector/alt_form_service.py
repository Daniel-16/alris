import logging
from typing import Dict, Any, Optional
from playwright.async_api import async_playwright, Browser

logger = logging.getLogger("alt_form_service")

class SimpleFormService:
    def __init__(self):
        self.browser: Optional[Browser] = None
        
    async def initialize(self):
        """Initialize the browser if not already initialized"""
        if not self.browser:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(headless=True)
            
    async def close(self):
        """Close the browser if it exists"""
        if self.browser:
            await self.browser.close()
            self.browser = None
            
    @staticmethod
    async def fill_form(url: str, form_data: Dict[str, str]) -> Dict[str, Any]:
        service = SimpleFormService()
        try:
            await service.initialize()
            page = await service.browser.new_page()
            
            logger.info(f"Navigating to form URL: {url}")
            await page.goto(url)            
            await page.wait_for_load_state("networkidle")
            
            for field_name, value in form_data.items():
                try:
                    selectors = [
                        f'input[name="{field_name}"]',
                        f'input[id="{field_name}"]',
                        f'input[aria-label="{field_name}"]',
                        f'textarea[name="{field_name}"]',
                        f'textarea[id="{field_name}"]'
                    ]
                    
                    for selector in selectors:
                        try:
                            element = await page.wait_for_selector(selector, timeout=1000)
                            if element:
                                await element.fill(value)
                                logger.info(f"Filled field {field_name} with value {value}")
                                break
                        except Exception:
                            continue
                            
                except Exception as e:
                    logger.warning(f"Could not fill field {field_name}: {str(e)}")
            
            try:
                submit_button = await page.query_selector('button[type="submit"], input[type="submit"]')
                if submit_button:
                    await submit_button.click()
                    await page.wait_for_load_state("networkidle")
                    logger.info("Form submitted successfully")
            except Exception as e:
                logger.warning(f"Could not submit form: {str(e)}")
            
            screenshot = await page.screenshot()
            
            await page.close()
            await service.close()
            
            return {
                "status": "success",
                "message": "Form filled successfully",
                "screenshot": screenshot
            }
            
        except Exception as e:
            logger.error(f"Error filling form: {str(e)}", exc_info=True)
            if service.browser:
                await service.close()
            return {
                "status": "error",
                "message": f"Error filling form: {str(e)}"
            } 