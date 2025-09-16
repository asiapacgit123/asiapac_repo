import os
from playwright.sync_api import sync_playwright
from google import genai

# ========= CONFIG =========
SCREENSHOT_DIR = "screenshots"
# API_KEY = os.getenv("GEMINI_API_KEY", os.getenv("GOOGLE_API_KEY"))
MODEL = "gemini-1.5-flash"   # use gemini-1.5-pro if you have access
API_KEY = "AQ.Ab8RN6JSHD6qr0AZDTJPdi6ka9LnzsjZiqTnR0UlinzGWFSYMw"  # Replace with your actual API key
# ==========================

# Example: Manually enter your test steps here
test_instructions = [
    "Open https://example.com",
    "Click on the More information link",
    "Take screenshot",
]

# Make sure screenshots folder exists
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

# Init Google GenAI client
client = genai.Client(api_key=API_KEY)

def interpret_instruction(instruction: str) -> str:
    """Convert natural language instruction into Playwright Python code."""
    prompt = f"""
You are an assistant that converts natural language test instructions into Playwright Python commands.

Examples:
- Instruction: "Open https://example.com"
  Output: page.goto("https://example.com")
- Instruction: "Click on the login button"
  Output: page.click("text=login")
- Instruction: "Type username test_user"
  Output: page.fill("input[name='username']", "test_user")
- Instruction: "Take screenshot"
  Output: page.screenshot(path=f"{{SCREENSHOT_DIR}}/step.png")

Now convert this instruction:
"{instruction}"
"""
    resp = client.models.generate_content(model=MODEL, contents=prompt)
    return resp.text.strip()

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=True to hide UI
        page = browser.new_page()

        for step, instruction in enumerate(test_instructions, start=1):
            print(f"\nStep {step}: {instruction}")

            try:
                # Convert to Playwright command
                command = interpret_instruction(instruction)
                print(f" -> Generated code: {command}")

                # Run the command
                exec(command)

                # Save screenshot after every step
                screenshot_path = os.path.join(SCREENSHOT_DIR, f"step_{step}.png")
                page.screenshot(path=screenshot_path)

            except Exception as e:
                print(f"Error at step {step}: {e}")
                break

        browser.close()

if __name__ == "__main__":
    if not API_KEY:
        print("❌ Error: API key not set. Use GEMINI_API_KEY or GOOGLE_API_KEY env var.")
    else:
        run()
