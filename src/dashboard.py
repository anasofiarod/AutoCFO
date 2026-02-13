import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import sys
from typing import Optional

# For portfolio purposes, we will leave the default demo_store. 
# This would ideally have to be passed dynamically.
DEFAULT_CLIENT = "demo_client"

st.set_page_config(page_title="Auto-CFO Dashboard", layout="wide")

@st.cache_data
def load_data() -> Optional[pd.DataFrame]:
    base_dir = Path(__file__).resolve().parent.parent
    client_name = DEFAULT_CLIENT

    # Again, for portfolio purposes we are using examples dir. 
    file_path = base_dir / "examples" / client_name / "data.csv"
    
    if not file_path.exists():
        return None
    
    df = pd.read_csv(file_path)
    df = df.rename(columns={"Date": "date", "Memo": "description", "Cost": "amount"})
    df["date"] = pd.to_datetime(df["date"])
    

    def categorize(desc: str) -> str:
        d = str(desc).lower()
        if any(x in d for x in ["stripe", "income", "deposit", "consulting"]): return "Revenue"
        if any(x in d for x in ["github", "server", "hosting", "software"]): return "Tech"
        if any(x in d for x in ["starbucks", "food", "meal"]): return "Meals"
        return "Operating Exp"

    df["category"] = df["description"].apply(categorize)
    df["year"] = df["date"].dt.year
    df["month_str"] = df["date"].dt.strftime("%Y-%m")
    return df

# --- APP LAYOUT ---
st.title("Executive Financial Dashboard")
st.markdown("Interactive view of your generated financial data.")

df = load_data()

if df is None:
    st.error("Data not found. Run the generator first!")
    st.stop()

# Sidebar
year = st.sidebar.selectbox("Select Year", sorted(df["year"].unique(), reverse=True))
df_view = df[df["year"] == year]

# Top Metrics
kpi1, kpi2, kpi3 = st.columns(3)
rev = df_view[df_view["category"]=="Revenue"]["amount"].sum()
exp = df_view[df_view["category"]!="Revenue"]["amount"].sum()
profit = rev - exp

kpi1.metric("Revenue", f"${rev:,.2f}")
kpi2.metric("Expenses", f"${exp:,.2f}")
kpi3.metric("Net Profit", f"${profit:,.2f}", delta_color="normal")

st.divider()

# Charts
c1, c2 = st.columns([2,1])
with c1:
    st.subheader("Cash Flow Trend")
    trend = df_view.groupby("month_str")["amount"].sum().reset_index()
    fig = px.area(trend, x="month_str", y="amount", markers=True)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Expense Breakdown")
    exps = df_view[df_view["category"]!="Revenue"]
    fig2 = px.doughnut(exps, names="category", values="amount", hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)

st.caption(f"Showing data for {year}. Source: Auto-CFO Engine.")