import React, { useState } from "react";
import axios from "axios";
import './App.css';

const API_URL = "http://localhost:8000";

function App() {
  // Test case management
  const [testCases, setTestCases] = useState([
    { id: 1, name: "Login Test", steps: "Open /login\nFill #username with testuser\nFill #password with password123\nClick #loginBtn\nAssert #dashboard is visible" }
  ]);
  const [editingCase, setEditingCase] = useState(null);
  const [caseName, setCaseName] = useState("");
  const [caseSteps, setCaseSteps] = useState("");

  // Script generation & execution
  const [testSteps, setTestSteps] = useState("");
  const [script, setScript] = useState("");
  const [editedScript, setEditedScript] = useState("");
  const [output, setOutput] = useState("");
  const [screenshots, setScreenshots] = useState([]);
  const [verification, setVerification] = useState("");
  const [loading, setLoading] = useState(false);

  // Reporting
  const [history, setHistory] = useState([]);

  // Image modal
  const [modalImg, setModalImg] = useState(null);

  // Test case CRUD
  const saveTestCase = () => {
    if (editingCase) {
      setTestCases(testCases.map(tc => tc.id === editingCase.id ? { ...editingCase, name: caseName, steps: caseSteps } : tc));
    } else {
      setTestCases([...testCases, { id: Date.now(), name: caseName, steps: caseSteps }]);
    }
    setEditingCase(null);
    setCaseName("");
    setCaseSteps("");
  };
  const editTestCase = (tc) => {
    setEditingCase(tc);
    setCaseName(tc.name);
    setCaseSteps(tc.steps);
  };
  const deleteTestCase = (id) => {
    setTestCases(testCases.filter(tc => tc.id !== id));
  };

  // Script generation & execution
  const generateScript = async () => {
    setLoading(true);
    setOutput("");
    setScreenshots([]);
    setVerification("");
    try {
      const res = await axios.post(`${API_URL}/generate_script`, { test_steps: testSteps });
      setScript(res.data.script_code);
      setEditedScript(res.data.script_code);
    } catch (err) {
      alert("Error generating script");
    }
    setLoading(false);
  };

  const runScript = async () => {
    setLoading(true);
    setOutput("");
    setScreenshots([]);
    try {
      const res = await axios.post(`${API_URL}/run_script`, { script_code: editedScript });
      setOutput(res.data.output);
      setScreenshots(res.data.screenshots || []);
      setHistory([{ date: new Date().toLocaleString(), output: res.data.output, screenshots: res.data.screenshots || [] }, ...history]);
    } catch (err) {
      alert("Error running script");
    }
    setLoading(false);
  };

  const verifyScript = async () => {
    setLoading(true);
    setVerification("");
    try {
      const res = await axios.post(`${API_URL}/verify_script`, { script_code: editedScript });
      setVerification(res.data.verification);
    } catch (err) {
      alert("Error verifying script");
    }
    setLoading(false);
  };

  const rectifyScript = async () => {
    setLoading(true);
    try {
      const res = await axios.post(`${API_URL}/rectify_script`, { script_code: editedScript });
      setEditedScript(res.data.rectified_script);
    } catch (err) {
      alert("Error rectifying script");
    }
    setLoading(false);
  };

  return (
    <div style={{ maxWidth: 900, margin: "auto", padding: 24, fontFamily: "Segoe UI, Arial, sans-serif", background: "#f8f9fa", minHeight: "100vh" }}>
      <header style={{ display: "flex", alignItems: "center", marginBottom: 24 }}>
        <img src="https://upload.wikimedia.org/wikipedia/commons/4/4a/Logo_2013_Google.png" alt="logo" style={{ width: 48, marginRight: 16 }} />
        <h1 style={{ margin: 0, fontWeight: 700, fontSize: 28, color: "#1a237e" }}>
          Gemini AI Website Testing Dashboard
        </h1>
      </header>

      {/* Test Steps Input */}
      <section style={{ marginBottom: 32 }}>
        <h2 style={{ color: "#1976d2" }}>Test Steps</h2>
        <textarea
          rows={6}
          style={{
            width: "100%",
            fontSize: 16,
            padding: 12,
            borderRadius: 8,
            border: "1px solid #bbb",
            marginBottom: 12,
            background: "#f4f6f8"
          }}
          placeholder="Enter test steps, one per line..."
          value={testSteps}
          onChange={e => setTestSteps(e.target.value)}
        />
        <div style={{ display: "flex", gap: 12, marginBottom: 16 }}>
          <button className="main-btn" onClick={generateScript} disabled={loading}>
            🚀 Generate Playwright Script
          </button>
        </div>
      </section>

      {/* Test Case Editor */}
      <section style={{ marginBottom: 32 }}>
        <h2 style={{ color: "#1976d2" }}>Test Case Editor</h2>
        <div style={{ display: "flex", gap: 32 }}>
          <div style={{ flex: 1 }}>
            <h3>Test Cases</h3>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead>
                <tr style={{ background: "#f4f6f8" }}>
                  <th style={{ padding: 8, border: "1px solid #eee" }}>Name</th>
                  <th style={{ padding: 8, border: "1px solid #eee" }}>Actions</th>
                </tr>
              </thead>
              <tbody>
                {testCases.map(tc => (
                  <tr key={tc.id}>
                    <td style={{ padding: 8, border: "1px solid #eee" }}>{tc.name}</td>
                    <td style={{ padding: 8, border: "1px solid #eee" }}>
                      <button className="sec-btn" onClick={() => editTestCase(tc)}>Edit</button>
                      <button className="sec-btn" style={{ marginLeft: 8 }} onClick={() => deleteTestCase(tc.id)}>Delete</button>
                      <button className="main-btn" style={{ marginLeft: 8 }} onClick={() => setTestSteps(tc.steps)}>Use in Script</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div style={{ flex: 1 }}>
            <h3>{editingCase ? "Edit Test Case" : "Add New Test Case"}</h3>
            <input
              type="text"
              placeholder="Test Case Name"
              value={caseName}
              onChange={e => setCaseName(e.target.value)}
              style={{ width: "100%", padding: 8, marginBottom: 8, borderRadius: 6, border: "1px solid #bbb" }}
            />
            <textarea
              rows={8}
              placeholder="Test steps, one per line..."
              value={caseSteps}
              onChange={e => setCaseSteps(e.target.value)}
              style={{ width: "100%", padding: 8, borderRadius: 6, border: "1px solid #bbb" }}
            />
            <button className="main-btn" style={{ marginTop: 8 }} onClick={saveTestCase}>
              {editingCase ? "Save Changes" : "Add Test Case"}
            </button>
            {editingCase && (
              <button className="sec-btn" style={{ marginLeft: 8, marginTop: 8 }} onClick={() => { setEditingCase(null); setCaseName(""); setCaseSteps(""); }}>
                Cancel
              </button>
            )}
          </div>
        </div>
      </section>

      {/* Script Generator & Runner */}
      <section style={{ marginBottom: 32 }}>
        <h2 style={{ color: "#1976d2" }}>Script Generator & Runner</h2>
        {script && (
          <>
            <h3>Generated Playwright Script (Editable)</h3>
            <textarea
              rows={12}
              style={{
                width: "100%",
                fontSize: 15,
                padding: 12,
                borderRadius: 8,
                border: "1px solid #bbb",
                background: "#f4f6f8",
                marginBottom: 12,
                resize: "vertical",
                minHeight: 120,
                maxHeight: 240
              }}
              value={editedScript}
              onChange={e => setEditedScript(e.target.value)}
            />
            <div style={{ display: "flex", gap: 12, marginBottom: 8 }}>
              <button className="main-btn" onClick={runScript} disabled={loading}>
                ▶️ Run Script
              </button>
              <button className="sec-btn" onClick={verifyScript} disabled={loading}>
                ✅ Verify Script
              </button>
              <button className="sec-btn" onClick={rectifyScript} disabled={loading}>
                🛠️ Rectify Script
              </button>
            </div>
          </>
        )}
      </section>

      {/* Script Output */}
      {output && (
        <section style={{ marginBottom: 32 }}>
          <h3 style={{ color: "#388e3c" }}>Script Output</h3>
          <pre style={{
            background: "#f1f8e9",
            padding: 16,
            borderRadius: 8,
            fontSize: 15,
            overflowX: "auto"
          }}>{output}</pre>
        </section>
      )}

      {/* Verification */}
      {verification && (
        <section style={{ marginBottom: 32 }}>
          <h3 style={{ color: "#0288d1" }}>Verification Results</h3>
          <pre style={{
            background: "#e3f2fd",
            padding: 16,
            borderRadius: 8,
            fontSize: 15,
            overflowX: "auto"
          }}>{verification}</pre>
        </section>
      )}

      {/* Screenshots */}
      {screenshots.length > 0 && (
        <section style={{ marginBottom: 32 }}>
          <h3 style={{ color: "#7b1fa2" }}>Screenshots</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: 16 }}>
            {screenshots.map((img, idx) => (
              <div key={idx} style={{ textAlign: "center" }}>
                <img
                  src={`${API_URL}/screenshot/${img}`}
                  alt={`step ${idx+1}`}
                  style={{
                    width: 220,
                    margin: 4,
                    border: "1px solid #ccc",
                    borderRadius: 8,
                    background: "#fafafa",
                    cursor: "pointer"
                  }}
                  onClick={() => setModalImg(`${API_URL}/screenshot/${img}`)}
                />
                <div style={{ fontSize: 13, color: "#555" }}>{img}</div>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Reports & History */}
      {history.length > 0 && (
        <section style={{ marginBottom: 32 }}>
          <h2 style={{ color: "#1976d2" }}>Reports & History</h2>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr style={{ background: "#f4f6f8" }}>
                <th style={{ padding: 8, border: "1px solid #eee" }}>Date</th>
                <th style={{ padding: 8, border: "1px solid #eee" }}>Output</th>
                <th style={{ padding: 8, border: "1px solid #eee" }}>Screenshots</th>
              </tr>
            </thead>
            <tbody>
              {history.map((h, i) => (
                <tr key={i}>
                  <td style={{ padding: 8, border: "1px solid #eee" }}>{h.date}</td>
                  <td style={{ padding: 8, border: "1px solid #eee", maxWidth: 300, overflow: "auto" }}>
                    <pre style={{ whiteSpace: "pre-wrap" }}>{h.output.slice(0, 200)}{h.output.length > 200 ? "..." : ""}</pre>
                  </td>
                  <td style={{ padding: 8, border: "1px solid #eee" }}>
                    {h.screenshots.map((img, idx) => (
                      <img
                        key={idx}
                        src={`${API_URL}/screenshot/${img}`}
                        alt={`step ${idx+1}`}
                        style={{ width: 60, margin: 2, border: "1px solid #ccc", borderRadius: 4 }}
                        onClick={() => setModalImg(`${API_URL}/screenshot/${img}`)}
                      />
                    ))}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </section>
      )}

      {/* Image Modal */}
      {modalImg && (
        <div style={{
          position: "fixed", top: 0, left: 0, right: 0, bottom: 0,
          background: "rgba(0,0,0,0.7)", zIndex: 2000,
          display: "flex", alignItems: "center", justifyContent: "center"
        }}
          onClick={() => setModalImg(null)}
        >
          <img src={modalImg} alt="Screenshot" style={{ maxWidth: "90vw", maxHeight: "90vh", borderRadius: 12, boxShadow: "0 4px 32px #0008" }} />
        </div>
      )}

      {loading && (
        <div style={{
          position: "fixed",
          top: 0, left: 0, right: 0, bottom: 0,
          background: "rgba(255,255,255,0.7)",
          zIndex: 1000,
          display: "flex",
          alignItems: "center",
          justifyContent: "center"
        }}>
          <div style={{
            background: "#fff",
            padding: 32,
            borderRadius: 16,
            boxShadow: "0 2px 16px #0002",
            fontSize: 22,
            color: "#1976d2"
          }}>
            Loading...
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
