# 🛒 Realmart Sales Dashboard (Streamlit)

An interactive sales analytics dashboard built with **Python + Streamlit**, upgraded from an earlier Excel/Pivot Table version. Analyzes 2,000+ retail transactions across 3 cities and 3 branches.

🔗 **Live demo:** _[add your Streamlit Community Cloud link here after deploying]_
📊 **Excel version:** _[link to your original Excel repo]_

## Features

- **KPI overview** — total revenue, transactions, average order value, gross income, average rating
- **Revenue trends** — daily revenue over time
- **Geographic breakdown** — revenue by city and branch
- **Product analysis** — revenue by product line, with a product line × city heatmap
- **Time patterns** — sales by hour of day
- **Payment & customer insights** — payment method split, customer type × gender breakdown, rating distribution
- **Interactive filters** — date range, city, branch, product line, payment method, customer type, gender

## Tech Stack

- Python
- Streamlit
- Pandas
- Plotly

## Run it locally

```bash
git clone https://github.com/SaiSanthosh1308/REALMART-SALES-DASHBOARD-STREAMLIT.git
cd REALMART-SALES-DASHBOARD-STREAMLIT
pip install -r requirements.txt
streamlit run app.py
```

## Dataset

Retail transaction data covering branch, city, product line, customer type, gender, payment method, unit price, quantity, tax, total, gross income, and customer rating.

## About This Project

This is a Python/Streamlit rebuild of an Excel dashboard I originally built for the same dataset — part of a broader effort to move from static Excel reporting to interactive, code-driven analytics tools as I build toward a data analyst role.
