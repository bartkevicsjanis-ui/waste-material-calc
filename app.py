import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Laser Cutting Waste Calculator",
    layout="wide"
)

# =====================================================
# CUSTOM STYLE
# =====================================================
st.markdown(
    """
    <style>
    .stApp {
        background-color: #e6f4ea;
        color: black;
    }

    .block-container {
        max-width: 70%;
        padding: 2rem;
    }

    section[data-testid="stFileUploader"] {
        background-color: #3a3a3a;
        padding: 20px;
        border-radius: 10px;
    }

    section[data-testid="stFileUploader"] label,
    section[data-testid="stFileUploader"] small {
        color: white;
        font-weight: 600;
    }

    .stDownloadButton button {
        background-color: #2f7d32;
        color: white;
        border-radius: 8px;
        font-weight: 600;
    }

    .metric-box {
        background-color: #cfe9d6;
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🛠️ Laser Cutting Waste & Cost Calculator")

# =====================================================
# TEMPLATE DOWNLOAD
# =====================================================
st.subheader("📥 Download Excel Template")

template = pd.DataFrame({
    "date": ["01.01.2026", "15.01.2026"],
    "width": [1.0, 1.2],
    "length": [2.0, 2.5],
    "used_area": [1.6, 2.4],
    "price_per_m2": [30, 28],
})

buf = BytesIO()
try:
    with pd.ExcelWriter(buf) as writer:
        template.to_excel(writer, index=False)
except Exception as e:
    st.error("Excel export failed. Make sure openpyxl is installed.")
    st.stop()

st.download_button(
    "⬇️ Download Excel Template",
    buf.getvalue(),
    "laser_cut_template.xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
)

st.divider()
st.caption("Units: meters (m), square meters (m²), EUR")

# =====================================================
# FILE UPLOAD
# =====================================================
file = st.file_uploader("📂 Upload CSV or Excel file", type=["csv", "xlsx"])
if not file:
    st.stop()

# =====================================================
# LOAD FILE
# =====================================================
try:
    if file.name.lower().endswith(".csv"):
        df = pd.read_csv(file, sep=None, engine="python", encoding="utf-8-sig")
    else:
        df = pd.read_excel(file)
except Exception as e:
    st.error("Failed to read file. Check format and dependencies.")
    st.stop()

df.columns = df.columns.str.lower().str.strip()

# =====================================================
# COLUMN MAP
# =====================================================
def fi
