"""
Gemini Playwright Test Script Generator

Setup Instructions:
1. Install required packages: pip install google-generativeai playwright streamlit
2. Set your Google API key: 
   - Environment variable: export GOOGLE_API_KEY=your_api_key_here
   - Or update GOOGLE_API_KEY variable below
3. Install Playwright browsers: playwright install
4. Run: python chatgenaitest.py (CLI mode) or streamlit run chatgenaitest.py (Web UI)
"""

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import os
import subprocess
import glob
from datetime import datetime

import vertexai
from vertexai.generative_models import GenerativeModel, Part

# --- Configuration ---
PROJECT_ID = "project-1-3-464607"
REGION = "us-central1"
MODEL_NAME = "gemini-2.0-flash-lite"
GENERATED_SCRIPT = "generated_playwright_test.py"

vertexai.init(project=PROJECT_ID, location=REGION)
model = GenerativeModel(MODEL_NAME)

app = FastAPI()

# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only. Restrict in prod!
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TestStepsRequest(BaseModel):
    test_steps: str

class ScriptRequest(BaseModel):
    script_code: str

@app.post("/generate_script")
def generate_script(req: TestStepsRequest):
    prompt = f"""
You are an assistant that converts natural language test instructions into a complete Python Playwright script.
Generate a Python script that performs the following test steps using Playwright:

{req.test_steps}

The script should:
- Import necessary modules
- Launch a Chromium browser (headless=False)
- Execute the steps
- Take a screenshot after each step (save as 'step_1.png', 'step_2.png', etc.)
- Close the browser at the end

Only output the Python code, nothing else.
"""
    response = model.generate_content([Part.from_text(prompt)])
    script_code = response.text
    # Clean code (remove ```python etc)
    lines = script_code.strip().splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    script_code = "\n".join(lines).strip()
    return {"script_code": script_code}

@app.post("/run_script")
def run_script(req: ScriptRequest):
    # Remove old screenshots
    for f in glob.glob("step_*.png"):
        os.remove(f)
    # Save and run script
    with open(GENERATED_SCRIPT, "w", encoding="utf-8") as f:
        f.write(req.script_code)
    try:
        result = subprocess.run(
            ["python", GENERATED_SCRIPT],
            capture_output=True,
            text=True,
            timeout=300
        )
        screenshots = sorted(glob.glob("step_*.png"))
        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout + "\n" + result.stderr,
            "screenshots": [os.path.basename(s) for s in screenshots],
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "output": "Script execution timed out.",
            "screenshots": [],
            "return_code": -1
        }

@app.post("/verify_script")
def verify_script(req: ScriptRequest):
    prompt = f"""
Analyze the following Playwright test script and provide:

1. Code Quality Assessment
2. Best Practices Check
3. Potential Issues/Bugs
4. Performance Optimization Suggestions
5. Security Considerations
6. Maintainability Score (1-10)
7. Specific Improvements

Test Script:
{req.script_code}

Provide detailed feedback with specific line references where applicable.
"""
    response = model.generate_content([Part.from_text(prompt)])
    return {"verification": response.text}

@app.post("/generate_test_cases")
def generate_test_cases_api(req: TestStepsRequest):
    prompt = f"""
Generate comprehensive test cases from the following requirements:

{req.test_steps}

For each test case, provide:
1. Test Case ID
2. Test Case Name
3. Pre-conditions
4. Test Steps
5. Expected Results
6. Priority (High/Medium/Low)
7. Test Type (Functional/UI/Integration/etc.)

Format as a structured list with clear separation between test cases.
"""
    response = model.generate_content([Part.from_text(prompt)])
    return {"test_cases": response.text}

from fastapi.responses import FileResponse

@app.get("/screenshot/{filename}")
def get_screenshot(filename: str):
    path = os.path.join(os.getcwd(), filename)
    if os.path.exists(path):
        return FileResponse(path)
    return {"error": "File not found"}

# To run: uvicorn backend.main:app --reload