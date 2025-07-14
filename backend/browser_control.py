import asyncio
from playwright.async_api import async_playwright
import os
import time

class BrowserController:
    def __init__(self, email, password, screenshot_dir=r"C:\Users\91701\Desktop\BrowserAutomation\screenshots"):
        self.email = email
        self.password = password
        self.screenshot_dir = screenshot_dir
        os.makedirs(screenshot_dir, exist_ok=True)

    async def send_email(self, to, subject, body):
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False)
            context = await browser.new_context()
            page = await context.new_page()

            try:
                # Step 1: Go to Gmail
                print("Navigating to Gmail...")
                await page.goto("https://mail.google.com")
                await self.capture(page, "1_login_page")

                # Step 2: Enter email
                print("Entering email...")
                await page.wait_for_selector("input[type='email']", timeout=10000)
                await page.fill("input[type='email']", self.email)
                await page.click("#identifierNext")

                # Step 3: Wait for password page and enter password
                print("Waiting for password page...")
                await asyncio.sleep(2)

                # Wait for password input with multiple possible selectors
                password_selectors = [
                    "input[type='password']",
                    "input[name='password']",
                    "#password",
                    "input[aria-label*='password']"
                ]

                password_input = None
                for selector in password_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=5000)
                        password_input = page.locator(selector)
                        if await password_input.is_visible():
                            break
                    except:
                        continue

                if not password_input:
                    raise Exception("Could not find password input field")

                await self.capture(page, "2_password_page")

                print(" Entering password...")
                await password_input.fill(self.password)
                await asyncio.sleep(1)

                # Click next button
                next_selectors = [
                    "#passwordNext",
                    "button[type='submit']",
                    "div[role='button'][id*='Next']"
                ]

                clicked = False
                for selector in next_selectors:
                    try:
                        if await page.locator(selector).is_visible():
                            await page.click(selector)
                            clicked = True
                            break
                    except:
                        continue

                if not clicked:
                    # Try pressing Enter as fallback
                    await password_input.press("Enter")

                # Step 4: Wait for inbox to load
                print("Waiting for inbox to load...")
                await asyncio.sleep(3)

                # Multiple selectors for inbox detection
                inbox_selectors = [
                    "div[role='main']",
                    "div[gh='tm']",  # Gmail toolbar
                    "div[role='button'][gh='cm']",  # Compose button
                    "div[data-tooltip='Compose']"
                ]

                inbox_loaded = False
                for selector in inbox_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=10000)
                        inbox_loaded = True
                        break
                    except:
                        continue

                if not inbox_loaded:
                    raise Exception("Could not detect inbox loaded")

                await self.capture(page, "3_inbox_loaded")

                # Step 5: Click Compose
                print("Opening compose window...")

                # Try multiple approaches to find and click compose
                compose_selectors = [
                    "div[role='button'][gh='cm']",
                    "div[data-tooltip='Compose']",
                    "div[aria-label*='Compose']",
                    "div[jsaction*='compose']",
                    "div.T-I.T-I-KE.L3"  # Common Gmail compose button class
                ]

                compose_clicked = False
                for selector in compose_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=3000)
                        if await page.locator(selector).is_visible():
                            await page.click(selector)
                            compose_clicked = True
                            print(f"Compose clicked using selector: {selector}")
                            break
                    except:
                        continue

                if not compose_clicked:
                    # Try pressing 'C' key as shortcut
                    await page.keyboard.press("c")
                    await asyncio.sleep(2)
                    print("Tried keyboard shortcut 'C' for compose")

                # Step 6: Wait for compose window and fill email
                print("Waiting for compose window...")
                await asyncio.sleep(3)

                # First, let's wait for the compose window to be fully loaded
                compose_window_selectors = [
                    "div[role='dialog']",
                    "div.aYF",  # Gmail compose window class
                    "div[aria-label*='New Message']",
                    "div.M9"  # Another common Gmail compose class
                ]

                compose_window_found = False
                for selector in compose_window_selectors:
                    try:
                        await page.wait_for_selector(selector, timeout=10000)
                        if await page.locator(selector).is_visible():
                            compose_window_found = True
                            print(f"Compose window found with selector: {selector}")
                            break
                    except:
                        continue

                if not compose_window_found:
                    print("Compose window not detected, continuing anyway...")

                # Debug: Take screenshot and print all input elements
                await self.capture(page, "4_compose_debug")

                # Get all input elements for debugging
                all_inputs = await page.locator("input, textarea, div[contenteditable]").all()
                print(f"Found {len(all_inputs)} input elements")

                for i, input_elem in enumerate(all_inputs):
                    try:
                        if await input_elem.is_visible():
                            tag_name = await input_elem.evaluate("el => el.tagName")
                            name = await input_elem.get_attribute("name") or "no-name"
                            placeholder = await input_elem.get_attribute("placeholder") or "no-placeholder"
                            aria_label = await input_elem.get_attribute("aria-label") or "no-aria-label"
                            print(f"  {i}: {tag_name} - name:{name} - placeholder:{placeholder} - aria-label:{aria_label}")
                    except:
                        pass

                # Try multiple selectors for TO field with more comprehensive list
                to_selectors = [
                    "textarea[name='to']",
                    "input[name='to']",
                    "div[aria-label*='To']",
                    "textarea[aria-label*='To']",
                    "input[aria-label*='To']",
                    "div[data-hovercard-id='to']",
                    "div[role='textbox'][aria-label*='To']",
                    "textarea[placeholder*='To']",
                    "input[placeholder*='To']",
                    "div[contenteditable='true'][aria-label*='To']",
                    "div.vR input",  # Gmail specific TO field
                    "div.aoD.hl input",  # Another Gmail TO field selector
                    "div[jsname] input[type='hidden'] + div[contenteditable]",  # Gmail TO field pattern
                    "div.aYF input",  # Any input in compose window
                    "div.aYF textarea",  # Any textarea in compose window
                    "div[role='dialog'] input",  # Any input in dialog
                    "div[role='dialog'] textarea"  # Any textarea in dialog
                ]

                to_field = None
                for selector in to_selectors:
                    try:
                        elements = await page.locator(selector).all()
                        for element in elements:
                            if await element.is_visible():
                                to_field = element
                                print(f" Found TO field with selector: {selector}")
                                break
                        if to_field:
                            break
                    except:
                        continue

                if not to_field:
                    # Try to find any visible input/textarea in the compose area
                    print("Trying to find any visible input field...")
                    all_visible_inputs = await page.locator("input:visible, textarea:visible, div[contenteditable='true']:visible").all()
                    if all_visible_inputs:
                        to_field = all_visible_inputs[0]  # Take the first visible input
                        print(f"Using first visible input field")
                    else:
                        raise Exception("Could not find TO field in compose window")

                await self.capture(page, "4_compose_open")

                # Fill recipient
                print("Filling recipient...")
                try:
                    await to_field.click()  # Click to focus
                    await asyncio.sleep(0.5)
                    await to_field.fill(to)
                    await asyncio.sleep(0.5)
                    # Press Tab to move to next field
                    await page.keyboard.press("Tab")
                    print("Recipient filled successfully")
                except Exception as e:
                    print(f"Error filling recipient: {e}")
                    # Try typing instead
                    await page.keyboard.type(to)
                    await page.keyboard.press("Tab")

                # Fill subject - try multiple selectors
                print(" Filling subject...")
                subject_selectors = [
                    "input[name='subjectbox']",
                    "input[aria-label*='Subject']",
                    "input[placeholder*='Subject']",
                    "div[role='dialog'] input[type='text']",
                    "div.aYF input[type='text']"
                ]

                subject_filled = False
                for selector in subject_selectors:
                    try:
                        elements = await page.locator(selector).all()
                        for element in elements:
                            if await element.is_visible():
                                await element.click()
                                await asyncio.sleep(0.5)
                                await element.fill(subject)
                                subject_filled = True
                                print(f"Subject filled with selector: {selector}")
                                break
                        if subject_filled:
                            break
                    except:
                        continue

                if not subject_filled:
                    print("Could not find subject field, trying keyboard input...")
                    await page.keyboard.type(subject)
                    await page.keyboard.press("Tab")

                # Fill body - try multiple selectors
                print("Filling email body...")
                body_selectors = [
                    "div[aria-label='Message Body']",
                    "div[role='textbox'][aria-label*='Message']",
                    "div[contenteditable='true'][role='textbox']",
                    "div[contenteditable='true'][aria-label*='Message']",
                    "div[g_editable='true']",
                    "div[role='textbox'][contenteditable='true']",
                    "div.Am.Al.editable.LW-avf.tS-tW",  # Gmail body class
                    "div[contenteditable='true'][spellcheck='true']"
                ]

                body_filled = False
                for selector in body_selectors:
                    try:
                        elements = await page.locator(selector).all()
                        for element in elements:
                            if await element.is_visible():
                                await element.click()  # Click first to focus
                                await asyncio.sleep(0.5)
                                await element.fill(body)
                                body_filled = True
                                print(f"Body filled with selector: {selector}")
                                break
                        if body_filled:
                            break
                    except:
                        continue

                if not body_filled:
                    print("Could not find message body field, trying keyboard input...")
                    await page.keyboard.type(body)

                await self.capture(page, "5_email_filled")

                # Step 7: Send email
                print("Sending email...")
                send_selectors = [
                    "div[aria-label*='Send'][role='button']",
                    "div[data-tooltip='Send']",
                    "div[role='button'][tabindex='1']",
                    "div[aria-label='Send ‪(Ctrl+Enter)‬']",
                    "div.T-I.J-J5-Ji.aoO.v7.T-I-atl.L3"  # Common Gmail send button class
                ]

                sent = False
                for selector in send_selectors:
                    try:
                        if await page.locator(selector).is_visible():
                            await page.click(selector)
                            sent = True
                            print(f"Email sent using selector: {selector}")
                            break
                    except:
                        continue

                if not sent:
                    # Try keyboard shortcut as fallback
                    await page.keyboard.press("Ctrl+Enter")
                    print("Tried keyboard shortcut Ctrl+Enter to send")

                await asyncio.sleep(3)
                await self.capture(page, "6_email_sent")

                print("Email sent successfully!")
                return {"status": "success", "message": "Email sent successfully."}

            except Exception as e:
                print(f"Error: {e}")
                await self.capture(page, "error_screenshot")
                return {"status": "error", "message": str(e)}

            finally:
                await browser.close()

    async def capture(self, page, filename):
        """Save screenshot with given filename in screenshots directory"""
        path = os.path.join(self.screenshot_dir, f"{filename}.png")
        try:
            await page.screenshot(path=path)
            print(f"Screenshot saved: {filename}.png")
        except Exception as e:
            print(f"Could not save screenshot {filename}: {e}")

if __name__ == "__main__":
    EMAIL = "techtestingln@gmail.com"
    PASSWORD = "techtestingln@2025"

    TO = "saisujan08@gmail.com"
    SUBJECT = "AI Agent Task - Sai Sujan Shamarthi"
    BODY = "Hi, this is a test email sent by my browser control agent using Playwright."

    controller = BrowserController(EMAIL, PASSWORD)
    asyncio.run(controller.send_email(TO, SUBJECT, BODY))