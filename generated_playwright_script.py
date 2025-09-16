from playwright.sync_api import sync_playwright



with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page()

    # Step 1: Open www.google.com
    page.goto("https://www.google.com")
    page.screenshot(path="step_1.png")

    # Step 2: Click on Settings
    page.locator("#gbwa a").click()
    page.screenshot(path="step_2.png")


    # Step 3: Click on Advanced Search
    page.locator("#fsettl a:has-text('Advanced search')").click()
    page.screenshot(path="step_3.png")

    # Step 4: Take a screenshot and save
    page.screenshot(path="googleimage1.png")

    browser.close()




