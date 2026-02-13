import streamlit as st
import pandas as pd

st.set_page_config(page_title="Pro Real Estate ROI", layout="wide")
st.title("🏠 Real Estate ROI Architect")
st.write("Professional-grade investment analysis for property investors.")

with st.container(border=True):
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("💰 Investment Details")
        prop_price = st.number_input("Property Purchase Price ($)", min_value=0, value=250000)
        closing_costs = st.number_input("Closing Costs ($)", min_value=0, value=5000)
        repair_costs = st.number_input("Repair/Renovation ($)", min_value=0, value=10000)
        
    with col2:
        st.subheader("📊 Monthly Income/Expense")
        monthly_rent = st.number_input("Expected Monthly Rent ($)", min_value=0, value=2000)
        monthly_expenses = st.number_input("Monthly Expenses (Taxes, Insurance, etc) ($)", min_value=0, value=600)

# Calculations
total_investment = prop_price + closing_costs + repair_costs
annual_income = monthly_rent * 12
annual_expenses = monthly_expenses * 12
annual_net_profit = annual_income - annual_expenses
roi = (annual_net_profit / total_investment) * 100 if total_investment > 0 else 0

st.divider()

# Results Dashboard
c1, c2, c3 = st.columns(3)
c1.metric("Total Investment", f"${total_investment:,}")
c2.metric("Annual Net Profit", f"${annual_net_profit:,}")
c3.metric("ROI (%)", f"{roi:.2f}%")

if roi > 8:
    st.success("🔥 This is a High-Yield Investment!")
elif roi > 4:
    st.info("⚖️ This is a Moderate-Yield Investment.")
else:
    st.warning("⚠️ Low-Yield. Exercise caution.")

# Data Table for Export
st.subheader("📋 Detailed Breakdown")
data = {
    "Category": ["Total Capital Outlay", "Annual Rental Revenue", "Total Annual Expenses", "Annual Cash Flow"],
    "Value": [f"${total_investment:,}", f"${annual_income:,}", f"${annual_expenses:,}", f"${annual_net_profit:,}"]
}
st.table(pd.DataFrame(data))
