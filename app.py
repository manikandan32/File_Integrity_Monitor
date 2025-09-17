from flask import Flask, render_template, jsonify
import threading
import fimsys  # import our fim logic

app = Flask(__name__)

# Configuration
TARGET_DIR = r"C:\\Users\\hp\Desktop\\fim_sample"   # Folder to monitor (change this)
BASELINE_FILE = "baseline.json"
LOG_FILE = "fim.log"
EXCLUDE_PATTERNS = []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/baseline", methods=["POST"])
def create_baseline():
    b = fimsys.build_baseline(TARGET_DIR, BASELINE_FILE, EXCLUDE_PATTERNS)
    return jsonify({"status": "Baseline created", "total_files": len(b.get("files", {}))})

@app.route("/scan", methods=["POST"])
def scan_once():
    rc = fimsys.run_scan_once(TARGET_DIR, BASELINE_FILE, LOG_FILE, EXCLUDE_PATTERNS)
    return jsonify({"status": "Scan complete", "changes_detected": rc})

@app.route("/monitor", methods=["POST"])
def start_monitor():
    def run_monitor():
        # ✅ enable auto-update baseline
        fimsys.monitor_loop(TARGET_DIR, BASELINE_FILE, 5, LOG_FILE, True, EXCLUDE_PATTERNS)

    t = threading.Thread(target=run_monitor, daemon=True)
    t.start()
    return jsonify({"status": "Monitoring started with auto-update baseline"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
