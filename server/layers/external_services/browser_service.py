import logging
from typing import Dict, Optional
from playwright.async_api import async_playwright

logger = logging.getLogger("external_services.browser")

class BrowserService:
    def __init__(self):
        self._playwright = None
        self._browser = None
        self._context = None
        self._page = None
    
    async def initialize(self):
        if self._playwright is None:
            logger.info("Initializing Playwright browser service")
            self._playwright = await async_playwright().start()
            self._browser = await self._playwright.chromium.launch(headless=True)
            self._context = await self._browser.new_context()
            self._page = await self._context.new_page()
            logger.info("Browser service initialized")
    
    async def navigate(self, url: str) -> bool:
        logger.info(f"Navigating to {url}")
        await self.initialize()
        try:
            await self._page.goto(url)
            return True
        except Exception as e:
            logger.error(f"Failed to navigate to {url}: {str(e)}")
            return False
    
    async def fill_form(self, form_data: Dict[str, str], selectors: Optional[Dict[str, str]] = None) -> bool:
        await self.initialize()
        try:
            page = self._page
            form = await page.query_selector('form')
            if not form:
                logger.error("No form found on the page.")
                return False
            input_elements = await form.query_selector_all('input, select, textarea')
            field_map = {}
            for element in input_elements:
                name = await element.get_attribute('name')
                el_id = await element.get_attribute('id')
                placeholder = await element.get_attribute('placeholder')
                label_text = None
                if el_id:
                    label = await page.query_selector(f'label[for="{el_id}"]')
                    if label:
                        label_text = (await label.inner_text()).strip().lower()
                keys = set()
                if name:
                    keys.add(name.strip().lower())
                if el_id:
                    keys.add(el_id.strip().lower())
                if placeholder:
                    keys.add(placeholder.strip().lower())
                if label_text:
                    keys.add(label_text)
                for key in keys:
                    field_map[key] = element
            for field, value in form_data.items():
                field_key = field.strip().lower()
                matched = False
                if field_key in field_map:
                    await field_map[field_key].fill(str(value))
                    matched = True
                else:
                    for key, element in field_map.items():
                        if field_key in key or key in field_key:
                            await element.fill(str(value))
                            matched = True
                            break
                if not matched:
                    logger.warning(f"Could not match form field '{field}' to any input on the page.")
            try:
                await form.evaluate('(form) => form.submit()')
            except Exception as e:
                submit_btn = await form.query_selector('button[type="submit"], input[type="submit"]')
                if submit_btn:
                    await submit_btn.click()
                else:
                    logger.warning("Could not find a submit button to submit the form.")
            return True
        except Exception as e:
            logger.error(f"Failed to fill form: {str(e)}")
            return False
    
    async def click_element(self, selector: str) -> bool:
        await self.initialize()
        try:
            await self._page.click(selector)
            return True
        except Exception as e:
            logger.error(f"Failed to click element {selector}: {str(e)}")
            return False
    
    async def close(self):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        self._browser = None
        self._context = None
        self._page = None
        self._playwright = None
        logger.info("Browser service closed")
    
    async def discover_form_fields(self, url: str):
        """Navigate to the URL, scrape the first form, and return a list of field names and user-friendly labels."""
        await self.initialize()
        try:
            page = self._page
            await page.goto(url)
            form = await page.query_selector('form')
            if not form:
                logger.error("No form found on the page.")
                return []
            input_elements = await form.query_selector_all('input, select, textarea')
            fields = []
            for element in input_elements:
                name = await element.get_attribute('name')
                el_id = await element.get_attribute('id')
                placeholder = await element.get_attribute('placeholder')
                label_text = None
                if el_id:
                    label = await page.query_selector(f'label[for="{el_id}"]')
                    if label:
                        label_text = (await label.inner_text()).strip()
                user_label = label_text or placeholder or name or el_id or "Unknown Field"
                field_name = name or el_id or placeholder or user_label
                if field_name:
                    fields.append({
                        "field_name": field_name,
                        "label": user_label
                    })
            return fields
        except Exception as e:
            logger.error(f"Failed to discover form fields: {str(e)}")
            return [] 