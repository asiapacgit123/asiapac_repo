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

import vertexai
from vertexai.generative_models import GenerativeModel, Part
import subprocess
import sys
import os
from datetime import datetime

# --- Configuration ---
PROJECT_ID = "project-1-3-464607"
REGION = "us-central1"
MODEL_NAME = "gemini-2.0-flash-lite"
GENERATED_SCRIPT = "generated_playwright_test.py"
LOGO_PATH = "C:\\Users\\khandelwal.ankit\\.vscode\\M1\\M1_Singapore_2020.svg"  # Path to your logo file

# --- Initialize Vertex AI ---
try:
    vertexai.init(project=PROJECT_ID, location=REGION)
except Exception as e:
    print(f"Error initializing Vertex AI: {e}")
    sys.exit(1)

# --- Load the Model ---
try:
    model = GenerativeModel(MODEL_NAME)
except Exception as e:
    print(f"Error loading model '{MODEL_NAME}': {e}")
    sys.exit(1)

def generate_playwright_script(test_steps: str) -> str:
    prompt = f"""
You are an assistant that converts natural language test instructions into a complete Python Playwright script.
Generate a Python script that performs the following test steps using Playwright:

{test_steps}

The script should:
- Import necessary modules
- Launch a Chromium browser (headless=False)
- Execute the steps
- Take a screenshot after each step (save as 'step_1.png', 'step_2.png', etc.)
- Close the browser at the end

Only output the Python code, nothing else.
"""
    response = model.generate_content([Part.from_text(prompt)])
    return response.text

def clean_script_code(script_code: str) -> str:
    # Remove triple backticks and language hints from start/end
    lines = script_code.strip().splitlines()
    if lines and lines[0].strip().startswith("```"):
        lines = lines[1:]
    if lines and lines and lines[-1].strip().startswith("```"):
        lines = lines[:-1]
    # Remove any ''' at start/end
    if lines and lines[0].strip().startswith("'''"):
        lines = lines[1:]
    if lines and lines and lines[-1].strip().startswith("'''"):
        lines = lines[:-1]
    return "\n".join(lines).strip()

def save_and_run_script(script_code: str, filename: str):
    script_code = clean_script_code(script_code)
    with open(filename, "w", encoding="utf-8") as f:
        f.write(script_code)
    print(f"\nGenerated script saved to {filename}. Running the script...\n")
    subprocess.run(["python", filename], check=False)

def run_playwright_script(script_code: str) -> dict:
    """Execute Playwright script and return results"""
    try:
        # Remove old screenshots
        import glob
        for f in glob.glob("step_*.png"):
            os.remove(f)
        
        # Save and run script
        with open(GENERATED_SCRIPT, "w", encoding="utf-8") as f:
            f.write(script_code)
        
        result = subprocess.run(
            ["python", GENERATED_SCRIPT],
            capture_output=True,
            text=True,
            timeout=500
        )
        
        # Collect screenshots
        screenshots = sorted(glob.glob("step_*.png"))
        
        return {
            "status": "success" if result.returncode == 0 else "error",
            "output": result.stdout + "\n" + result.stderr,
            "screenshots": screenshots,
            "return_code": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "output": "Script execution timed out after 5 minutes",
            "screenshots": [],
            "return_code": -1
        }
    except Exception as e:
        return {
            "status": "error",
            "output": f"Error running script: {str(e)}",
            "screenshots": [],
            "return_code": -1
        }

def generate_test_report(report_type: str, session_state: dict) -> str:
    """Generate different types of test reports"""
    if report_type == "Execution Summary":
        return generate_execution_summary(session_state)
    elif report_type == "Test Case Documentation":
        return generate_test_case_docs(session_state)
    elif report_type == "Code Quality Report":
        return generate_code_quality_report(session_state)
    elif report_type == "Full Test Suite Report":
        return generate_full_report(session_state)
    else:
        return "Report type not supported"

def generate_execution_summary(session_state: dict) -> str:
    """Generate execution summary report"""
    history = session_state.get("execution_history", [])
    if not history:
        return "No test executions found."
    
    total = len(history)
    successful = sum(1 for exec in history if exec.get("status") == "success")
    failed = total - successful
    success_rate = (successful / total * 100) if total > 0 else 0
    
    report = f"""# Test Execution Summary Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Overview
- Total Executions: {total}
- Successful: {successful}
- Failed: {failed}
- Success Rate: {success_rate:.1f}%

## Recent Executions
"""
    
    for i, execution in enumerate(history[-10:], 1):
        report += f"""
### Execution {i}
- Timestamp: {execution.get('timestamp', 'Unknown')}
- Status: {execution.get('status', 'Unknown').upper()}
- Screenshots: {len(execution.get('screenshots', []))}
"""
    
    return report

def generate_test_case_docs(session_state: dict) -> str:
    """Generate test case documentation"""
    test_cases = session_state.get("test_cases", "")
    if not test_cases:
        return "No test cases generated yet."
    
    return f"""# Test Case Documentation
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Test Cases

{test_cases}

## Additional Notes
- Generated using Gemini AI
- Review and validate before execution
- Update as requirements change
"""

def generate_code_quality_report(session_state: dict) -> str:
    """Generate code quality report"""
    verification = session_state.get("verification_results", "")
    if not verification:
        return "No code verification results available."
    
    return f"""# Code Quality Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Analysis Results

{verification}

## Recommendations
- Follow Playwright best practices
- Include proper error handling
- Add meaningful assertions
- Use page object patterns for complex tests
"""

def generate_full_report(session_state: dict) -> str:
    """Generate comprehensive report"""
    return f"""# Comprehensive Test Suite Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{generate_execution_summary(session_state)}

{generate_test_case_docs(session_state)}

{generate_code_quality_report(session_state)}

## Appendix
- Tool: Gemini Test Automation Suite
- Model: {MODEL_NAME}
- Project: {PROJECT_ID}
"""

def prepare_export_data(session_state: dict, format_type: str) -> str:
    """Prepare data for export in various formats"""
    if format_type == "JSON":
        import json
        export_data = {
            "generated_at": datetime.now().isoformat(),
            "test_cases": session_state.get("test_cases", ""),
            "script_code": session_state.get("script_code", ""),
            "verification_results": session_state.get("verification_results", ""),
            "execution_history": session_state.get("execution_history", [])
        }
        return json.dumps(export_data, indent=2)
    
    elif format_type == "CSV":
        history = session_state.get("execution_history", [])
        if not history:
            return "timestamp,status,output_length,screenshots_count\n"
        
        csv_data = "timestamp,status,output_length,screenshots_count\n"
        for execution in history:
            csv_data += f"{execution.get('timestamp', '')},{execution.get('status', '')},{len(execution.get('output', ''))},{len(execution.get('screenshots', []))}\n"
        return csv_data
    
    elif format_type == "HTML":
        logo_section = ""
        if os.path.exists(LOGO_PATH):
            import base64
            try:
                with open(LOGO_PATH, "rb") as img_file:
                    img_data = base64.b64encode(img_file.read()).decode()
                logo_section = f'<img src="data:image/svg+xml;base64,{img_data}" alt="Logo" style="max-width: 80px; height: 60px; display: block; margin: 0 auto;">'
            except:
                logo_section = ""
        
        return f"""<!DOCTYPE html>
<html>
<head>
    <title>Test Automation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 20px; text-align: center; }}
        .section {{ margin: 20px 0; }}
        pre {{ background-color: #f5f5f5; padding: 10px; overflow-x: auto; }}
        .logo {{ margin-bottom: 20px; }}
        .footer {{ text-align: center; margin-top: 40px; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header">
        <div class="logo">{logo_section}</div>
        <h1>🤖 Gemini Test Automation Suite</h1>
        <h2>Test Automation Report</h2>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
    </div>
    
    <div class="section">
        <h2>Test Cases</h2>
        <pre>{session_state.get("test_cases", "No test cases available")}</pre>
    </div>
    
    <div class="section">
        <h2>Generated Script</h2>
        <pre>{session_state.get("script_code", "No script generated")}</pre>
    </div>
    
    <div class="section">
        <h2>Verification Results</h2>
        <pre>{session_state.get("verification_results", "No verification results")}</pre>
    </div>
    
    <div class="footer">
        <p>Generated by Gemini Test Automation Suite | Powered by Google Vertex AI</p>
    </div>
</body>
</html>"""
    
    else:  # PDF placeholder
        return "PDF export not yet implemented. Use HTML format for now."

def cli_mode():
    print("Enter your test steps (type 'END' on a new line to finish):")
    steps = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        steps.append(line)
    test_steps = "\n".join(steps)

    if not test_steps.strip():
        print("No test steps provided. Exiting.")
    else:
        script_code = generate_playwright_script(test_steps)
        print("\nGenerated Playwright Script:\n")
        print(script_code)
        save_and_run_script(script_code, GENERATED_SCRIPT)

def generate_test_cases(requirements: str) -> str:
    """Generate comprehensive test cases from requirements"""
    prompt = f"""
Generate comprehensive test cases from the following requirements:

{requirements}

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
    return response.text

def verify_test_script(script_code: str) -> str:
    """Verify and analyze test script for best practices"""
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
{script_code}

Provide detailed feedback with specific line references where applicable.
"""
    response = model.generate_content([Part.from_text(prompt)])
    return response.text

def streamlit_mode():
    import streamlit as st
    import os
    from glob import glob
    import json
    from datetime import datetime

    st.set_page_config(
        page_title="Gemini Test Automation Suite", 
        page_icon="🤖", 
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header with logo
    header_col1, header_col2, header_col3 = st.columns([1, 3, 1])
    with header_col2:
        logo_col, title_col = st.columns([1, 3])
        with logo_col:
            if os.path.exists(LOGO_PATH):
                st.image(LOGO_PATH, width=80)
        with title_col:
            st.title("🤖 Gemini Test Automation Suite")
            st.markdown("*AI-Powered Test Generation & Automation Platform*")
    st.markdown("---")

    # Initialize session state
    if "script_code" not in st.session_state:
        st.session_state["script_code"] = ""
    if "editable_script" not in st.session_state:
        st.session_state["editable_script"] = ""
    if "test_cases" not in st.session_state:
        st.session_state["test_cases"] = ""
    if "verification_results" not in st.session_state:
        st.session_state["verification_results"] = ""
    if "execution_history" not in st.session_state:
        st.session_state["execution_history"] = []

    # Sidebar configuration
    with st.sidebar:
        # Logo in sidebar if available
        if os.path.exists(LOGO_PATH):
            st.image(LOGO_PATH, width=60)
            st.markdown("---")
        
        st.header("⚙️ Configuration")
        browser_type = st.selectbox("Browser", ["chromium", "firefox", "webkit"], index=0)
        headless = st.checkbox("Headless Mode", value=False)
        timeout = st.number_input("Timeout (ms)", value=30000, min_value=1000, max_value=120000)
        
        st.markdown("---")
        st.header("📊 Quick Stats")
        st.metric("Total Executions", len(st.session_state["execution_history"]))
        if st.session_state["execution_history"]:
            successful = sum(1 for exec in st.session_state["execution_history"] if exec.get("status") == "success")
            st.metric("Success Rate", f"{(successful/len(st.session_state['execution_history'])*100):.1f}%")

    # Main tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎯 Test Case Generation", 
        "🛠️ Script Generation", 
        "✅ Verification & Analysis", 
        "📈 Execution Status", 
        "📋 Reports & Export"
    ])

    with tab1:
        st.header("🎯 Test Case Generation")
        st.markdown("Generate comprehensive test cases from requirements or user stories.")
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            requirements = st.text_area(
                "Requirements/User Stories",
                height=300,
                placeholder="Enter your requirements, user stories, or feature descriptions...\n\nExample:\nAs a user, I want to log into the application so that I can access my dashboard.\nThe login form should validate credentials and show appropriate error messages."
            )
            
            if st.button("🎯 Generate Test Cases", type="primary"):
                if requirements.strip():
                    with st.spinner("Generating comprehensive test cases..."):
                        test_cases = generate_test_cases(requirements)
                        st.session_state["test_cases"] = test_cases
                    st.success("✅ Test cases generated successfully!")
                else:
                    st.warning("⚠️ Please enter requirements or user stories.")
        
        with col2:
            st.markdown("### 📝 Test Case Templates")
            templates = {
                "Login Flow": "User authentication with valid/invalid credentials, password reset, session management",
                "E-commerce": "Product search, add to cart, checkout process, payment validation",
                "Form Validation": "Input validation, required fields, format checking, error handling",
                "API Testing": "CRUD operations, authentication, error responses, data validation"
            }
            
            selected_template = st.selectbox("Choose Template", list(templates.keys()))
            if st.button("Use Template"):
                st.session_state["requirements_template"] = templates[selected_template]
        
        if st.session_state["test_cases"]:
            st.markdown("### 📋 Generated Test Cases")
            st.text_area("Test Cases", value=st.session_state["test_cases"], height=400, key="generated_test_cases")
            st.download_button("📥 Download Test Cases", st.session_state["test_cases"], file_name=f"test_cases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

    with tab2:
        st.header("🛠️ Playwright Script Generation")
        st.markdown("Convert test steps into executable Playwright automation scripts.")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            test_steps = st.text_area(
                "Test Steps",
                height=250,
                placeholder="Enter your test steps (one per line):\n\nExample:\nOpen https://example.com\nClick on login button\nEnter username: testuser\nEnter password: password123\nClick submit button\nVerify dashboard is displayed"
            )
            # Append pattern if added
            if "pattern_to_add" in st.session_state and st.session_state["pattern_to_add"]:
                test_steps += st.session_state["pattern_to_add"]
                st.session_state["pattern_to_add"] = ""
        
            if st.button("🛠️ Generate Playwright Script", type="primary"):
                if test_steps.strip():
                    with st.spinner("Generating Playwright script..."):
                        script_code = generate_playwright_script(test_steps)
                        cleaned_code = clean_script_code(script_code)
                    st.session_state["script_code"] = cleaned_code
                    st.session_state["editable_script"] = cleaned_code
                    st.success("✅ Script generated successfully!")
                else:
                    st.warning("⚠️ Please enter test steps.")
        
        with col2:
            st.markdown("### ⚙️ Script Options")
            include_assertions = st.checkbox("Include Assertions", value=True)
            include_screenshots = st.checkbox("Take Screenshots", value=True)
            include_waits = st.checkbox("Smart Waits", value=True)
            error_handling = st.checkbox("Error Handling", value=True)
            
            st.markdown("### 🎯 Common Patterns")
            if st.button("🔐 Add Login Pattern"):
                login_pattern = "\nNavigate to login page\nEnter username in #username\nEnter password in #password\nClick login button\nWait for dashboard to load"
                st.session_state["pattern_to_add"] = login_pattern
            
            if st.button("📝 Add Form Pattern"):
                form_pattern = "\nFill form field #name with 'Test User'\nFill form field #email with 'test@example.com'\nSelect dropdown option\nSubmit form\nVerify success message"
                st.session_state["pattern_to_add"] = form_pattern

    if st.session_state["script_code"]:
        st.markdown("### 📝 Generated Playwright Script (Editable)")
        edited_code = st.text_area(
            "Edit the script if needed:",
            value=st.session_state["editable_script"],
            height=400,
            key="editable_script"
        )

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("📸 Show Screenshots"):
                import glob
                screenshots = sorted(glob.glob("step_*.png"))
                if screenshots:
                    st.session_state["show_screenshots"] = True
                    st.success(f"Found {len(screenshots)} screenshots!")
                else:
                    st.warning("No screenshots found. Run a test first!")

        with col2:
            st.download_button("📥 Download Script", edited_code, file_name=GENERATED_SCRIPT)
        
        with col3:
            if st.button("✅ Verify Script"):
                with st.spinner("Analyzing script..."):
                    verification = verify_test_script(edited_code)
                    st.session_state["verification_results"] = verification
                st.success("Script analyzed!")
        
        with col4:
            if st.button("▶️ Run Script", type="primary"):
                execution_result = run_playwright_script(edited_code)
                st.session_state["execution_history"].append({
                    "timestamp": datetime.now().isoformat(),
                    "status": execution_result.get("status", "unknown"),
                    "output": execution_result.get("output", ""),
                    "screenshots": execution_result.get("screenshots", [])
                })
                st.success("Script executed! Check screenshots below.")
        
        # Display screenshots if requested or after running
        if st.session_state.get("show_screenshots", False) or any(exec.get("screenshots") for exec in st.session_state.get("execution_history", [])[-1:]):
            import glob
            screenshots = sorted(glob.glob("step_*.png"))
            if screenshots:
                st.markdown("### 📸 Test Screenshots")
                cols = st.columns(min(3, len(screenshots)))  # Max 3 columns
                for i, screenshot in enumerate(screenshots):
                    with cols[i % 3]:
                        if os.path.exists(screenshot):
                            st.image(screenshot, caption=f"Step {i+1}", use_column_width=True)
                        
                # Clear the show screenshots flag
                if st.button("🗑️ Clear Screenshots"):
                    for f in screenshots:
                        try:
                            os.remove(f)
                        except:
                            pass
                    st.session_state["show_screenshots"] = False
                    st.success("Screenshots cleared!")
                    st.rerun()

    with tab3:
        st.header("✅ Verification & Analysis")
        st.markdown("Analyze your test scripts for quality, performance, and best practices.")
        
        if st.session_state["verification_results"]:
            st.markdown("### 🔍 Latest Analysis Results")
            st.text_area("Analysis Results", value=st.session_state["verification_results"], height=400)
        else:
            st.info("💡 Generate a script first, then use the 'Verify Script' button to see analysis results here.")
        
        st.markdown("### 🎯 Manual Code Review")
        manual_code = st.text_area(
            "Paste code for manual review:",
            height=200,
            placeholder="Paste your Playwright script here for analysis..."
        )
        
        if st.button("🔍 Analyze Code"):
            if manual_code.strip():
                with st.spinner("Analyzing code..."):
                    verification = verify_test_script(manual_code)
                    st.session_state["verification_results"] = verification
                st.success("Analysis complete!")
                st.rerun()

    with tab4:
        st.header("📈 Execution Status & Monitoring")
        
        if st.session_state["execution_history"]:
            st.markdown("### 📊 Execution History")
            
            # Summary metrics
            col1, col2, col3, col4 = st.columns(4)
            total_executions = len(st.session_state["execution_history"])
            successful = sum(1 for exec in st.session_state["execution_history"] if exec.get("status") == "success")
            failed = total_executions - successful
            success_rate = (successful / total_executions * 100) if total_executions > 0 else 0
            
            col1.metric("Total Executions", total_executions)
            col2.metric("Successful", successful)
            col3.metric("Failed", failed)
            col4.metric("Success Rate", f"{success_rate:.1f}%")
            
            # Recent executions
            st.markdown("### 📋 Recent Executions")
            for i, execution in enumerate(reversed(st.session_state["execution_history"][-10:])):
                with st.expander(f"Execution {len(st.session_state['execution_history'])-i} - {execution.get('timestamp', 'Unknown')} - {execution.get('status', 'Unknown').upper()}"):
                    st.text(execution.get("output", "No output available"))
                    
                    screenshots = execution.get("screenshots", [])
                    if screenshots:
                        st.markdown("**Screenshots:**")
                        for screenshot in screenshots:
                            if os.path.exists(screenshot):
                                st.image(screenshot, caption=screenshot, width=300)
        else:
            st.info("🚀 Run your first test to see execution status and history here!")
            
        # Real-time monitoring section
        if st.button("🔄 Refresh Status"):
            st.rerun()

    with tab5:
        st.header("📋 Reports & Export")
        st.markdown("Generate comprehensive reports and export your test data.")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 📊 Report Generation")
            report_type = st.selectbox(
                "Report Type",
                ["Execution Summary", "Test Case Documentation", "Code Quality Report", "Full Test Suite Report"]
            )
            
            date_range = st.date_input("Date Range", value=[datetime.now().date()])
            
            if st.button("📈 Generate Report"):
                report_data = generate_test_report(report_type, st.session_state)
                st.session_state["current_report"] = report_data
                st.success("Report generated!")
        
        with col2:
            st.markdown("### 💾 Export Options")
            export_format = st.selectbox("Format", ["JSON", "CSV", "HTML", "PDF"])
            
            if st.button("📤 Export Data"):
                export_data = prepare_export_data(st.session_state, export_format)
                st.download_button(
                    f"📥 Download {export_format}",
                    export_data,
                    file_name=f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format.lower()}"
                )
        
        if "current_report" in st.session_state:
            st.markdown("### 📄 Generated Report")
            
            # Add logo to report if available
            if os.path.exists(LOGO_PATH):
                report_col1, report_col2, report_col3 = st.columns([2, 1, 2])
                with report_col2:
                    st.image(LOGO_PATH, width=50)
                    st.markdown("<center><small>Generated by Gemini Test Automation Suite</small></center>", unsafe_allow_html=True)
                st.markdown("---")
            
            st.text_area("Report Content", value=st.session_state["current_report"], height=400)

            # Display screenshots
            screenshots = sorted(glob("step_*.png"))
            if screenshots:
                st.markdown("#### Screenshots")
                for img in screenshots:
                    st.image(img, caption=img)
            else:
                st.info("No screenshots found. Make sure your script takes screenshots as 'step_1.png', 'step_2.png', etc.")

if __name__ == "__main__":
    # Detect if running in Streamlit
    try:
        import streamlit.runtime.scriptrunner
        streamlit_mode()
    except ImportError:
        cli_mode()