import subprocess
import time
import webview
import sys
import os

def run_streamlit():
    app_path = os.path.join(os.path.dirname(__file__), "app.py")

    subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", app_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

if __name__ == "__main__":
    run_streamlit()
    time.sleep(4)  # wait for Streamlit server

    webview.create_window(
        "Laser Cut Waste Calculator",
        "http://localhost:8501",
        width=1100,
        height=800
    )
    webview.start()
