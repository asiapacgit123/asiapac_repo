import playwright
from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Step 1: Open google.com
    page.goto("https://www.google.com")
    page.screenshot(path="step_1.png")
    print("Step 1 completed")


    # Step 2: Wait for 3 seconds
    time.sleep(3)
    page.screenshot(path="step_2.png")
    print("Step 2 completed")



    # Step 3: Type "hello singapore" in the search bar
    page.locator("input[name='q']").type("hello singapore")
    page.screenshot(path="step_3.png")
    print("Step 3 completed")


    # Step 4: Wait for 3 seconds
    time.sleep(3)
    page.screenshot(path="step_4.png")
    print("Step 4 completed")

    browser.close()