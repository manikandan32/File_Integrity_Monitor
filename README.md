# File Integrity Monitoring System 🛡️📂

A **Python-based File Integrity Monitoring (FIM) tool** that detects file changes such as **additions, modifications, and deletions** in real time. Built for an **MSc Cybersecurity mini-project**, it uses only Python’s standard library — no external FIM tools — and comes with a **modern Web UI (Flask + HTML/CSS)**.

> ⚠️ **Important — Educational Use Only.**  
> This project is intended for **academic and defensive security purposes**. Always use it responsibly and only on files/directories you own or have permission to monitor.  

---

## Features ✨

- Generate a **baseline snapshot** of files (SHA-256 + metadata).  
- Detect file **Additions, Modifications, Deletions**.  
- **Continuous monitoring** with auto-baseline update.  
- **Console & file logging** for forensic evidence.  
- **Web UI** with buttons to Baseline / Scan / Monitor.  
- Exclude files/folders with **glob patterns**.  
- **Cross-platform** — works on Windows, Linux, macOS.  

---

## Files 📂

- `fimsys.py` — Core Python logic (baseline, scan, monitor).  
- `app.py` — Flask web application.  
- `templates/` — Web UI templates (`index.html`).  
- `static/` — CSS styles for the dashboard.  
- `baseline.json` — Auto-generated baseline file.  
- `fim.log` — Log file of detected events.  

---

## Requirements ⚙️

- Python 3.7+  
- Flask (`pip install flask`)  

*(No third-party FIM libraries required — everything is built from scratch.)*

---

## Usage 💡

1. Clone the repository and install Flask:

```bash
git clone https://github.com/your-username/fim_system.git
cd fim_system
pip install flask
```

---

### ▶️ CLI Mode

1. Generate baseline:
```bash
python fimsys.py --baseline --dir "C:\path\to\monitor_dir" --baseline-file baseline.json
```

2. Run single scan:
```bash
python fimsys.py --scan-once --dir "C:\path\to\monitor_dir" --baseline-file baseline.json
```

3. Start continuous monitor:
```bash
python fimsys.py --monitor --dir "C:\path\to\monitor_dir" --baseline-file baseline.json --interval 10
```

---

### 🌐 Web UI Mode (Recommended)

1. Run Flask app:
```bash
python app.py
```

2. Open in browser:  
👉 [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

3. Use buttons:  
- 🛠 Generate Baseline  
- 🔍 Run Scan Once  
- 📡 Start Monitoring  

---

## Example Output 🖥️

**Console / Log file:**

```
2025-09-17 10:32:11 - INFO - ADDED: new_file.txt | hash=ab34...
2025-09-17 10:32:20 - INFO - MODIFIED: report.docx | old_hash=12ff.. | new_hash=99aa..
2025-09-17 10:32:35 - INFO - DELETED: old_data.csv | old_hash=45bb...
Baseline auto-updated after change.
```

**Web UI:**  
✅ Baseline created with 12 files  
✅ Scan complete, changes detected: 2  
✅ Monitoring started with auto-update baseline  

---

## How it works 🧠

1. System scans all files recursively and computes **SHA-256 hashes**.  
2. Stores baseline in `baseline.json`.  
3. Compares new scans against baseline.  
4. Reports **Additions, Deletions, Modifications**.  
5. (Optional) Updates baseline automatically after logging the change.  

---

## Recommended Improvements 🚀

- 📧 Email / Slack notifications on change.  
- 📊 Dashboard for historical logs.  
- ⚙️ Run as Windows Service / Linux Daemon.  
- 🔐 Digital signatures for baseline file integrity.  

---

## Author / Contact 👨‍💻

Developed by *[Your Name]* — MSc Cybersecurity Student.  
Purpose: Academic Mini Project | Topic: **File Integrity Monitoring System**

*Made with ❤️ for cybersecurity learning and defense.*
