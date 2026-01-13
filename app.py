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
with pd.ExcelWriter(buf, engine="openpyxl") as writer:
    template.to_excel(writer, index=False)

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
# LOAD FILE (ROBUST CSV)
# =====================================================
if file.name.lower().endswith(".csv"):
    df = pd.read_csv(file, sep=None, engine="python", encoding="utf-8-sig")
else:
    df = pd.read_excel(file)

df.columns = df.columns.str.lower().str.strip()

# =====================================================
# COLUMN MAP
# =====================================================
def find(cols):
    return next((c for c in cols if c in df.columns), None)

col = {
    "date": find(["date"]),
    "width": find(["width"]),
    "length": find(["length"]),
    "used": find(["used_area"]),
    "price": find(["price_per_m2", "price"]),
}

if None in col.values():
    st.error("❌ Missing required columns")
    st.write("Detected columns:", list(df.columns))
    st.stop()

# =====================================================
# CLEAN DATA
# =====================================================
df[col["date"]] = pd.to_datetime(df[col["date"]], errors="coerce", dayfirst=True)

for k in ["width", "length", "used", "price"]:
    df[col[k]] = pd.to_numeric(df[col[k]], errors="coerce")

df = df.dropna().reset_index(drop=True)

# =====================================================
# CALCULATIONS
# =====================================================
df["total_m2"] = df[col["width"]] * df[col["length"]]
df["waste_m2"] = df["total_m2"] - df[col["used"]]
df["waste_pct"] = (df["waste_m2"] / df["total_m2"]) * 100
df["waste_eur"] = df["waste_m2"] * df[col["price"]]

df["month"] = df[col["date"]].dt.to_period("M").astype(str)

# =====================================================
# KPI SUMMARY
# =====================================================
st.subheader("📌 Summary")

c1, c2, c3 = st.columns(3)
c1.markdown(f"<div class='metric-box'>Total waste<br>{df['waste_m2'].sum():.1_]()
