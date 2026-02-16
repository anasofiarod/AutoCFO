import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
import os
from typing import Optional

# --- CONFIGURATION ---
BASE_DIR = Path(__file__).resolve().parent.parent
CLIENTS_DIR = BASE_DIR / "clients"
EXAMPLES_DIR = BASE_DIR / "examples"

st.set_page_config(page_title="Auto-CFO Dashboard", layout="wide")

def get_available_clients() -> dict:
    """Scans for clients with data.csv in clients/ and examples/ folders."""
    client_map = {}

    # 1. Scan Examples
    if EXAMPLES_DIR.exists():
        for folder in EXAMPLES_DIR.iterdir():
            if folder.is_dir() and (folder / "data.csv").exists():
                client_map[f"Example: {folder.name}"] = folder

    # 2. Scan Clients
    if CLIENTS_DIR.exists():
        for folder in CLIENTS_DIR.iterdir():
            if folder.is_dir() and (folder / "data.csv").exists():
                client_map[f"Client: {folder.name}"] = folder
    
    return client_map

@st.cache_data
def load_data(client_path: Path) -> Optional[pd.DataFrame]:
    file_path = client_path / "data.csv"
    
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
    df["Month"] = df["date"].dt.strftime("%Y-%m")
    df = df.rename(columns={"amount": "Amount"})
    return df

# --- APP LAYOUT ---
st.title("Executive Financial Dashboard")

# 1. Sidebar Client Selection
clients = get_available_clients()

if not clients:
    st.error("No clients found! Ensure you have created a client folder in `clients/` or `examples/` with a `data.csv` file.")
    st.stop()

selected_client_name = st.sidebar.selectbox("Select Client", list(clients.keys()))
selected_client_path = clients[selected_client_name]

# 2. Load Data
st.markdown(f"**Viewing Data for:** `{selected_client_name}`")
df = load_data(selected_client_path)

if df is None:
    st.error(f"Data file missing for {selected_client_name}.")
    st.stop()

# Sidebar
# Year Selection
year = st.sidebar.selectbox("Select Year", sorted(df["year"].unique(), reverse=True))
df_view = df[df["year"] == year]

# Month Selection
months = ["All Months"] + sorted(df_view["Month"].unique().tolist())
selected_month = st.sidebar.selectbox("Select Month", months)

if selected_month != "All Months":
    df_view = df_view[df_view["Month"] == selected_month]

# Top Metrics
kpi1, kpi2, kpi3 = st.columns(3)
rev = df_view[df_view["category"]=="Revenue"]["Amount"].sum()
exp = df_view[df_view["category"]!="Revenue"]["Amount"].sum()
profit = rev - exp

kpi1.metric("Revenue", f"${rev:,.2f}")
kpi2.metric("Expenses", f"${exp:,.2f}")
kpi3.metric("Net Profit", f"${profit:,.2f}", delta_color="normal")

st.divider()

# Charts
c1, c2 = st.columns([2,1])
with c1:
    st.subheader("Cash Flow Trend")
    trend = df_view.groupby("Month")["Amount"].sum().reset_index()
    fig = px.area(trend, x="Month", y="Amount", markers=True)
    st.plotly_chart(fig, use_container_width=True)

with c2:
    st.subheader("Expense Breakdown")
    exps = df_view[df_view["category"]!="Revenue"]
    fig2 = px.pie(exps, names="category", values="Amount", hole=0.4)
    st.plotly_chart(fig2, use_container_width=True)

st.caption(f"Showing data for {year}. Source: Auto-CFO Engine.")