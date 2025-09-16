import os
from playwright.sync_api import sync_playwright

# Ensure screenshot folder exists
screenshot_dir = "C:\\Users\\khandelwal.ankit\\.vscode\\M1\\testfolder"
os.makedirs(screenshot_dir, exist_ok=True)

# with sync_playwright() as p:
#     browser = p.chromium.launch(headless=False)  # Set True if you don't want UI
#     page = browser.new_page()

#     # 1. Go to website
#     page.goto("https://samliew.com/nric-generator")

#     # 2. Take homepage screenshot
#     page.screenshot(path=f"{screenshot_dir}/homepage.png")

#     # 3. Click the link
#     page.click("a")

#     # 4. Wait and take another screenshot
#     page.wait_for_load_state()
#     page.screenshot(path=f"{screenshot_dir}/after_click.png")

#     browser.close()


# import os
# from playwright.sync_api import sync_playwright

# # Folder for screenshots
# screenshot_dir = "screenshots"
# os.makedirs(screenshot_dir, exist_ok=True)
def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # 1. Go to example.com
        page.goto("https://example.com")

        # 2. Click on "Terms and Conditions" link
        # Assuming there is a link with text containing "Terms" 
        page.click("text=More information")
        page.click("text=Terms")  

        # 3. Wait for page to load
        page.wait_for_load_state("networkidle")

        # 4. Scroll to the bottom of the page
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        # 5. Take screenshot of the bottom
        page.screenshot(path=f"{screenshot_dir}/bottom.png", full_page=True)

        # 6. Close browser
        browser.close()

if __name__ == "__main__":
    run()