import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Laser Cut Waste Calculator", layout="wide")

st.title("🔧 Laser Cutting Waste & Cost Calculator")

REQUIRED_COLUMNS = {"date", "width", "length", "used_area", "price_eur"}

uploaded_file = st.file_uploader(
    "📂 Upload CSV or Excel file",
    type=["csv", "xlsx"]
)

if uploaded_file is None:
    st.info("👆 Upload a file to begin.")
    st.stop()

# Load data
if uploaded_file.name.endswith(".csv"):
    df = pd.read_csv(uploaded_file)
else:
    df = pd.read_excel(uploaded_file)

# Validate columns
missing = REQUIRED_COLUMNS - set(df.columns)
if missing:
    st.error(f"❌ Missing columns: {', '.join(missing)}")
    st.stop()

# Convert date
df["date"] = pd.to_datetime(df["date"], errors="coerce")
if df["date"].isna().any():
    st.error("❌ Invalid date format. Use YYYY-MM-DD.")
    st.stop()

# Calculations
df["total_area"] = df["width"] * df["length"]
df["waste_area"] = df["total_area"] - df["used_area"]
df["waste_percent"] = (df["waste_area"] / df["total_area"]) * 100
df["waste_cost_eur"] = (df["waste_area"] / df["total_area"]) * df["price_eur"]

# KPIs
total_area = df["total_area"].sum()
total_waste = df["waste_area"].sum()
total_cost = df["waste_cost_eur"].sum()

c1, c2, c3 = st.columns(3)
c1.metric("Waste %", f"{(total_waste / total_area) * 100:.2f}%")
c2.metric("Waste Area", f"{total_waste:.2f}")
c3.metric("Money Lost (€)", f"{total_cost:.2f}")

st.subheader("📋 Detailed Results")
st.dataframe(df)

# Chart
st.subheader("📈 Daily Waste Cost (€)")
daily = df.groupby("date")["waste_cost_eur"].sum()

fig, ax = plt.subplots()
ax.plot(daily.index, daily.values)
ax.set_xlabel("Date")
ax.set_ylabel("EUR")
ax.set_title("Daily Laser Cutting Waste Cost")
plt.xticks(rotation=45)
st.pyplot(fig)

# Download
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "⬇️ Download Results as CSV",
    csv,
    "laser_cut_waste_results.csv",
    "text/csv"
)
