import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import time as dtime

st.set_page_config(page_title="Realmart Sales Dashboard", layout="wide", page_icon="🛒")

# ---------------------------------------------------------------
# Data loading & cleaning
# ---------------------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("realmart_raw.csv")
    df.columns = [c.strip() for c in df.columns]

    # Drop fully blank rows
    df = df.dropna(subset=["Invoice ID"])

    # Robust date parsing (mixed Excel-serial ints, strings, etc.)
    def parse_date(val):
        if pd.isna(val):
            return pd.NaT
        try:
            # Excel serial date
            fval = float(val)
            return pd.Timestamp("1899-12-30") + pd.to_timedelta(fval, unit="D")
        except (ValueError, TypeError):
            return pd.to_datetime(val, errors="coerce")

    df["Date"] = df["Date"].apply(parse_date)

    # Robust time parsing -> extract hour
    def parse_hour(val):
        if pd.isna(val):
            return np.nan
        try:
            fval = float(val)  # Excel time fraction of a day
            total_minutes = round(fval * 24 * 60)
            return (total_minutes // 60) % 24
        except (ValueError, TypeError):
            try:
                t = pd.to_datetime(val).time()
                return t.hour
            except Exception:
                return np.nan

    df["Hour"] = df["Time"].apply(parse_hour)

    df = df.dropna(subset=["Date", "Total"])
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    df["DayOfWeek"] = df["Date"].dt.day_name()
    df["Hour"] = df["Hour"].astype("Int64")

    numeric_cols = ["Unit price", "Quantity", "Tax 5%", "Total", "cogs",
                     "gross margin percentage", "gross income", "Rating"]
    for c in numeric_cols:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    return df

df = load_data()

st.title("🛒 Realmart Sales Dashboard")
st.caption(f"{len(df):,} transactions across {df['City'].nunique()} cities and {df['Branch'].nunique()} branches.")

# ---------------------------------------------------------------
# Sidebar filters
# ---------------------------------------------------------------
st.sidebar.header("Filters")

min_date, max_date = df["Date"].min().date(), df["Date"].max().date()
date_range = st.sidebar.date_input("Date range", (min_date, max_date), min_value=min_date, max_value=max_date)
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = min_date, max_date

city_sel = st.sidebar.multiselect("City", sorted(df["City"].dropna().unique()), default=sorted(df["City"].dropna().unique()))
branch_sel = st.sidebar.multiselect("Branch", sorted(df["Branch"].dropna().unique()), default=sorted(df["Branch"].dropna().unique()))
product_sel = st.sidebar.multiselect("Product line", sorted(df["Product line"].dropna().unique()), default=sorted(df["Product line"].dropna().unique()))
payment_sel = st.sidebar.multiselect("Payment method", sorted(df["Payment"].dropna().unique()), default=sorted(df["Payment"].dropna().unique()))
custtype_sel = st.sidebar.multiselect("Customer type", sorted(df["Customer type"].dropna().unique()), default=sorted(df["Customer type"].dropna().unique()))
gender_sel = st.sidebar.multiselect("Gender", sorted(df["Gender"].dropna().unique()), default=sorted(df["Gender"].dropna().unique()))

fdf = df[
    (df["Date"].dt.date >= start_date) & (df["Date"].dt.date <= end_date) &
    (df["City"].isin(city_sel)) &
    (df["Branch"].isin(branch_sel)) &
    (df["Product line"].isin(product_sel)) &
    (df["Payment"].isin(payment_sel)) &
    (df["Customer type"].isin(custtype_sel)) &
    (df["Gender"].isin(gender_sel))
]

st.markdown(f"**Showing {len(fdf):,} of {len(df):,} transactions**")

# ---------------------------------------------------------------
# KPI row
# ---------------------------------------------------------------
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Revenue", f"₹{fdf['Total'].sum():,.0f}")
c2.metric("Total Transactions", f"{len(fdf):,}")
c3.metric("Avg Order Value", f"₹{fdf['Total'].mean():,.2f}" if len(fdf) else "—")
c4.metric("Total Gross Income", f"₹{fdf['gross income'].sum():,.0f}")
c5.metric("Avg Rating", f"{fdf['Rating'].mean():.2f} ⭐" if len(fdf) else "—")

st.divider()

# ---------------------------------------------------------------
# Row 1: Revenue trend + City breakdown
# ---------------------------------------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("Revenue Over Time")
    daily = fdf.groupby(fdf["Date"].dt.date)["Total"].sum().reset_index()
    fig = px.line(daily, x="Date", y="Total", markers=True)
    fig.update_layout(yaxis_title="Revenue (₹)")
    st.plotly_chart(fig, width='stretch')

with col2:
    st.subheader("Revenue by City")
    city_rev = fdf.groupby("City")["Total"].sum().reset_index().sort_values("Total", ascending=False)
    fig2 = px.bar(city_rev, x="City", y="Total", color="City", text_auto=".2s")
    fig2.update_layout(yaxis_title="Revenue (₹)", showlegend=False)
    st.plotly_chart(fig2, width='stretch')

# ---------------------------------------------------------------
# Row 2: Product line + Branch
# ---------------------------------------------------------------
col3, col4 = st.columns(2)

with col3:
    st.subheader("Revenue by Product Line")
    pl_rev = fdf.groupby("Product line")["Total"].sum().reset_index().sort_values("Total", ascending=True)
    fig3 = px.bar(pl_rev, x="Total", y="Product line", orientation="h", text_auto=".2s")
    fig3.update_layout(xaxis_title="Revenue (₹)")
    st.plotly_chart(fig3, width='stretch')

with col4:
    st.subheader("Branch Performance")
    branch_rev = fdf.groupby("Branch").agg(Revenue=("Total", "sum"), Transactions=("Total", "count")).reset_index()
    fig4 = px.bar(branch_rev, x="Branch", y="Revenue", color="Branch", text_auto=".2s")
    fig4.update_layout(yaxis_title="Revenue (₹)", showlegend=False)
    st.plotly_chart(fig4, width='stretch')

# ---------------------------------------------------------------
# Row 3: Hourly pattern + Payment method
# ---------------------------------------------------------------
col5, col6 = st.columns(2)

with col5:
    st.subheader("Sales by Hour of Day")
    hourly = fdf.dropna(subset=["Hour"]).groupby("Hour")["Total"].sum().reset_index().sort_values("Hour")
    fig5 = px.bar(hourly, x="Hour", y="Total")
    fig5.update_layout(yaxis_title="Revenue (₹)", xaxis_title="Hour of Day")
    st.plotly_chart(fig5, width='stretch')

with col6:
    st.subheader("Payment Method Split")
    pay = fdf.groupby("Payment")["Total"].sum().reset_index()
    fig6 = px.pie(pay, names="Payment", values="Total", hole=0.4)
    st.plotly_chart(fig6, width='stretch')

# ---------------------------------------------------------------
# Row 4: Customer type / Gender + Rating distribution
# ---------------------------------------------------------------
col7, col8 = st.columns(2)

with col7:
    st.subheader("Revenue: Customer Type vs Gender")
    seg = fdf.groupby(["Customer type", "Gender"])["Total"].sum().reset_index()
    fig7 = px.bar(seg, x="Customer type", y="Total", color="Gender", barmode="group", text_auto=".2s")
    fig7.update_layout(yaxis_title="Revenue (₹)")
    st.plotly_chart(fig7, width='stretch')

with col8:
    st.subheader("Customer Rating Distribution")
    fig8 = px.histogram(fdf, x="Rating", nbins=20)
    st.plotly_chart(fig8, width='stretch')

# ---------------------------------------------------------------
# Row 5: Product line profitability heatmap by city
# ---------------------------------------------------------------
st.subheader("Revenue Heatmap: Product Line vs City")
heat = fdf.pivot_table(index="Product line", columns="City", values="Total", aggfunc="sum", fill_value=0)
fig9 = px.imshow(heat, text_auto=".0f", aspect="auto", color_continuous_scale="Blues")
st.plotly_chart(fig9, width='stretch')

# ---------------------------------------------------------------
# Top products / raw data
# ---------------------------------------------------------------
with st.expander("View filtered raw data"):
    st.dataframe(fdf, width='stretch')
