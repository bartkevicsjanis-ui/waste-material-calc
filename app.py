import streamlit as st
import pandas as pd

# -------------------------------------------------
# Page configuration
# -------------------------------------------------
st.set_page_config(
    page_title="Laser Cut Waste Calculator",
    layout="centered"
)

# -------------------------------------------------
# Limit app width (CSS)
# -------------------------------------------------
st.markdown(
    """
    <style>
    .block-container {
        max-width: 900px;
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------------------------------------------
# App Title
# -------------------------------------------------
st.title("🔧 Laser Cutting Waste & Cost Calculator")

# -------------------------------------------------
# Unit selector
# -------------------------------------------------
st.subheader("⚙️ Input Units")

unit = st.selectbox(
    "Select unit used in Excel file (width, length, used_area):",
    ["mm", "cm", "m"]
)

UNIT_TO_METER = {
    "mm": 0.001,
    "cm": 0.01,
    "m": 1.0
}

st.markdown(f"""
**Selected unit:** `{unit}`  
Results shown in **square meters (m²)** and **EUR (€)**  
Date format: **DD.MM.YYYY**
""")

# -------------------------------------------------
# Required columns
# -------------------------------------------------
REQUIRED_COLUMNS = {"date", "width", "length", "used_area", "price_eur"}

# -------------------------------------------------
# File upload
# -------------------------------------------------
uploaded_file = st.file_uploader(
    "📂 Upload CSV or Excel file",
    type=["csv", "xlsx"]
)

if uploaded_file is None:
    st.info("👆 Upload a file to begin.")
    st.stop()

# -------------------------------------------------
# Load data
# -------------------------------------------------
if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

# -------------------------------------------------
# Validate columns
# -------------------------------------------------
missing = REQUIRED_COLUMNS - set(df.columns)
if missing:
    st.error(f"❌ Missing required columns: {', '.join(missing)}")
    st.stop()

# -------------------------------------------------
# Convert & validate date
# -------------------------------------------------
df["date"] = pd.to_datetime(df["date"], errors="coerce")
if df["date"].isna().any():
    st.error("❌ Invalid date format. Use YYYY-MM-DD or Excel date.")
    st.stop()

# -------------------------------------------------
# Convert units → meters / m²
# -------------------------------------------------
factor = UNIT_TO_METER[unit]

df["width_m"] = df["width"] * factor
df["length_m"] = df["length"] * factor
df["used_area_m2"] = df["used_area"] * (factor ** 2)

# -------------------------------------------------
# Calculate total area
# -------------------------------------------------
df["total_area_m2"] = df["width_m"] * df["length_m"]

# -------------------------------------------------
# ❌ VALIDATION: used area > total area
# -------------------------------------------------
invalid_rows = df[df["used_area_m2"] > df["total_area_m2"]].copy()

if not invalid_rows.empty:
    st.error("❌ ERROR: Used area is larger than total sheet area in the rows listed below.")

    # Add Excel row numbers (row 1 = header)
    invalid_rows["Excel Row"] = invalid_rows.index + 2
    invalid_rows["date"] = invalid_rows["date"].dt.strftime("%d.%m.%Y")

    st.markdown("### 🚨 Incorrect Rows (fix these in Excel)")

    st.dataframe(
        invalid_rows[
            [
                "Excel Row",
                "date",
                "width",
                "length",
                "used_area",
                "total_area_m2",
                "used_area_m2"
            ]
        ].round(4),
        use_container_width=True
    )

    st.info(
        "ℹ️ **Explanation:** In these rows, the used area is larger than the total "
        "sheet area (width × length). Please correct the values in Excel and upload again."
    )

    st.stop()

# -------------------------------------------------
# Calculations (safe)
# -------------------------------------------------
df["waste_area_m2"] = df["total_area_m2"] - df["used_area_m2"]
df["waste_percent"] = (df["waste_area_m2"] / df["total_area_m2"]) * 100
df["waste_cost_eur"] = (df["waste_area_m2"] / df["total_area_m2"]) * df["price_eur"]

# -------------------------------------------------
# KPIs
# -------------------------------------------------
total_material_m2 = df["total_area_m2"].sum()
total_waste_m2 = df["waste_area_m2"].sum()
total_cost = df["waste_cost_eur"].sum()

c1, c2, c3 = st.columns(3)
c1.metric("Waste (%)", f"{(total_waste_m2 / total_material_m2) * 100:.2f}%")
c2.metric("Waste (m²)", f"{total_waste_m2:.3f}")
c3.metric("Money Lost (€)", f"{total_cost:.2f}")

# -------------------------------------------------
# Display results table
# -------------------------------------------------
st.subheader("📋 Detailed Results")

display_df = df.copy()
display_df["date"] = display_df["date"].dt.strftime("%d.%m.%Y")

display_cols = [
    "date",
    "total_area_m2",
    "used_area_m2",
    "waste_area_m2",
    "waste_percent",
    "waste_cost_eur"
]

st.dataframe(
    display_df[display_cols].round(4),
    use_container_width=True
)

# -------------------------------------------------
# Daily waste chart
# -------------------------------------------------
st.subheader("📈 Daily Waste Cost (€)")

daily = df.groupby("date")["waste_cost_eur"].sum()
daily.index = daily.index.strftime("%d.%m.%Y")
st.line_chart(daily)

# -------------------------------------------------
# Download results
# -------------------------------------------------
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Full Results as CSV",
    csv,
    "laser_cut_waste_results.csv",
    "text/csv"
)
