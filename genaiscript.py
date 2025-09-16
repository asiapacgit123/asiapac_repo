from playwright.sync_api import sync_playwright
import os

# Ensure screenshot folder exists
SCREENSHOT_FOLDER = "C:\\Users\\khandelwal.ankit\\.vscode\\M1\\testfolder"
os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)


import asyncio
import os
from playwright.async_api import async_playwright

# --- Configuration ---
WEBSITE_URL = 'https://example.com'  # Replace with the website you want to test
SCREENSHOT_FOLDER = 'screenshots'    # Folder to save screenshots
BROWSER_TYPE = 'chromium'           # 'chromium', 'firefox', or 'webkit'

# --- Helper function to create screenshot folder if it doesn't exist ---
def ensure_screenshot_folder_exists():
    if not os.path.exists(SCREENSHOT_FOLDER):
        os.makedirs(SCREENSHOT_FOLDER)
        print(f"Created screenshot folder: {SCREENSHOT_FOLDER}")

# --- Main testing function ---
async def perform_website_tests():
    async with async_playwright() as p:
        browser = None
        try:
            # 1. Launch the browser
            print(f"Launching {BROWSER_TYPE} browser...")
            if BROWSER_TYPE == 'chromium':
                browser = await p.chromium.launch()
            elif BROWSER_TYPE == 'firefox':
                browser = await p.firefox.launch()
            elif BROWSER_TYPE == 'webkit':
                browser = await p.webkit.launch()
            else:
                raise ValueError(f"Unsupported browser type: {BROWSER_TYPE}")

            # 2. Create a new browser context
            context = await browser.new_context()

            # 3. Create a new page
            page = await context.new_page()
            print(f"Navigating to: {WEBSITE_URL}")

            # 4. Navigate to the website
            await page.goto(WEBSITE_URL)

            # --- Start of specific test actions ---

            # 5. Take a screenshot of the initial page load
            initial_screenshot_path = os.path.join(SCREENSHOT_FOLDER, 'initial_page.png')
            await page.screenshot(path=initial_screenshot_path)
            print(f"Screenshot saved: {initial_screenshot_path}")

            # 6. (Example) Find an element and interact with it (e.g., click a button)
            #    Replace 'selector-for-button' with the actual CSS selector for the element you want to interact with.
            button_selector = 'button[id="submit-button"]' # Example selector
            try:
                print(f"Looking for button with selector: {button_selector}")
                # Using page.locator is the recommended way to find elements
                button = page.locator(button_selector)
                if await button.is_visible():
                    print("Button found and visible. Clicking...")
                    await button.click()

                    # 7. Take a screenshot after the interaction
                    after_click_screenshot_path = os.path.join(SCREENSHOT_FOLDER, 'after_button_click.png')
                    await page.screenshot(path=after_click_screenshot_path)
                    print(f"Screenshot saved: {after_click_screenshot_path}")

                    # 8. (Example) Wait for an element to appear or a change to occur
                    #    Replace 'selector-for-result' with the selector of an element that indicates success or a change.
                    result_selector = '.success-message' # Example selector
                    print(f"Waiting for element with selector: {result_selector}")
                    await page.wait_for_selector(result_selector, state='visible', timeout=10000)
                    print("Result element is visible.")

                    # 9. Take a screenshot of the result
                    result_screenshot_path = os.path.join(SCREENSHOT_FOLDER, 'after_interaction_result.png')
                    await page.screenshot(path=result_screenshot_path)
                    print(f"Screenshot saved: {result_screenshot_path}")
                else:
                    print('Button not found or not visible. Skipping interaction.')
            except Exception as e:
                print(f"Error during button interaction: {e}")
                # Optionally take a screenshot on error
                error_screenshot_path = os.path.join(SCREENSHOT_FOLDER, 'error_during_interaction.png')
                await page.screenshot(path=error_screenshot_path)
                print(f"Error screenshot saved: {error_screenshot_path}")

            # 10. (Example) Fill in a text input field
            #     Replace 'selector-for-input' and 'Your Test Text' accordingly.
            input_selector = 'input[name="username"]' # Example selector
            text_to_enter = 'Test User'
            try:
                print(f"Looking for input field with selector: {input_selector}")
                input_field = page.locator(input_selector)
                if await input_field.is_visible():
                    print(f"Entering text '{text_to_enter}' into input field...")
                    await input_field.fill(text_to_enter)

                    # 11. Take a screenshot after filling the input
                    after_fill_screenshot_path = os.path.join(SCREENSHOT_FOLDER, 'after_input_fill.png')
                    await page.screenshot(path=after_fill_screenshot_path)
                    print(f"Screenshot saved: {after_fill_screenshot_path}")
                else:
                    print('Input field not found or not visible. Skipping input.')
            except Exception as e:
                print(f"Error filling input field: {e}")
                # Optionally take a screenshot on error
                error_screenshot_path = os.path.join(SCREENSHOT_FOLDER, 'error_filling_input.png')
                await page.screenshot(path=error_screenshot_path)
                print(f"Error screenshot saved: {error_screenshot_path}")

            # --- End of specific test actions ---

            print('Website testing completed successfully.')

        except Exception as e:
            print(f"An error occurred during testing: {e}")
        finally:
            # 12. Close the browser
            if browser:
                print('Closing browser...')
                await browser.close()
                print('Browser closed.')

# --- Execute the tests ---
if __name__ == "__main__":
    ensure_screenshot_folder_exists()
    asyncio.run(perform_website_tests())