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
            field_info = []
            for el in input_elements:
                props = await page.evaluate(
                    '''el => ({
                        name: el.name || null,
                        id: el.id || null,
                        placeholder: el.placeholder || null,
                        aria_label: el.getAttribute("aria-label") || null,
                        type: el.type || null,
                        tag: el.tagName.toLowerCase(),
                        label: null
                    })''',
                    el
                )
                if props['id']:
                    label_el = await page.query_selector(f'label[for="{props["id"]}"]')
                    if label_el:
                        props['label'] = await label_el.inner_text()
                if not props['label']:
                    parent_label = await el.evaluate_handle('(el) => el.closest("label")')
                    if parent_label:
                        try:
                            props['label'] = await parent_label.inner_text()
                        except Exception:
                            pass
                field_info.append({'element': el, 'props': props})
            matched = set()
            for user_key, user_value in form_data.items():
                user_key_lower = user_key.lower().replace('_', '').replace(' ', '')
                best_match = None
                best_score = 0
                for field in field_info:
                    props = field['props']
                    candidates = [
                        props.get('name', ''),
                        props.get('id', ''),
                        props.get('placeholder', ''),
                        props.get('aria_label', ''),
                        props.get('label', '')
                    ]
                    for cand in candidates:
                        if not cand:
                            continue
                        cand_norm = cand.lower().replace('_', '').replace(' ', '')
                        if user_key_lower == cand_norm:
                            best_match = field
                            best_score = 3
                            break
                        if user_key_lower in cand_norm or cand_norm in user_key_lower:
                            if best_score < 2:
                                best_match = field
                                best_score = 2
                    if best_score == 3:
                        break
                if best_match:
                    el = best_match['element']
                    tag = best_match['props']['tag']
                    try:
                        if tag == 'input' and best_match['props']['type'] in ['checkbox', 'radio']:
                            await el.set_checked(bool(user_value))
                        elif tag == 'select':
                            await el.select_option(str(user_value))
                        else:
                            await el.fill(str(user_value))
                        matched.add(id(el))
                    except Exception as e:
                        logger.warning(f"Failed to fill field {user_key}: {e}")
                else:
                    logger.warning(f"Could not match user field '{user_key}' to any form input.")
            try:
                submit_btn = await form.query_selector('button[type="submit"],input[type="submit"]')
                if submit_btn:
                    await submit_btn.click()
                else:
                    await form.evaluate('(f) => f.submit()')
            except Exception as e:
                logger.warning(f"Could not submit form: {e}")
            if not matched:
                logger.error("No user fields matched any form inputs.")
                return False
            return True
        except Exception as e:
            logger.error(f"Error in fill_form: {e}")
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