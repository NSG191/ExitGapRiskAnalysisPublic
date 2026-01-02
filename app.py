import streamlit as st

# --- Initial Assumptions ---
st.set_page_config(layout="wide")
st.title("Telco Business Performance Calculator")

st.sidebar.header("Assumptions")

# --- Input fields in the sidebar ---
budget_subscribers = st.sidebar.number_input("Budget Subscribers", value=1000000)
budget_arpu = st.sidebar.slider("Budget ARPU ($)", min_value=10, max_value=100, value=50)
actual_subscribers = st.sidebar.number_input("Actual Subscribers", value=1050000)
actual_arpu = st.sidebar.slider("Actual ARPU ($)", min_value=10, max_value=100, value=52)
opex_as_percent_of_revenue = st.sidebar.slider("Opex as % of Revenue", min_value=10, max_value=80, value=40)

# --- Calculations ---
budget_revenue = budget_subscribers * budget_arpu
actual_revenue = actual_subscribers * actual_arpu

budget_ebitda = budget_revenue * (1 - (opex_as_percent_of_revenue / 100))
actual_ebitda = actual_revenue * (1 - (opex_as_percent_of_revenue / 100))

revenue_impact = actual_revenue - budget_revenue
ebitda_impact = actual_ebitda - budget_ebitda

# --- Displaying the Results ---
st.header("Financial Summary")

col1, col2, col3 = st.columns(3)
col1.metric("Budget Revenue", f"${budget_revenue:,.0f}")
col2.metric("Actual Revenue", f"${actual_revenue:,.0f}")
col3.metric("Revenue Impact", f"${revenue_impact:,.0f}")

st.header("EBITDA Summary")
col4, col5, col6 = st.columns(3)
col4.metric("Budget EBITDA", f"${budget_ebitda:,.0f}")
col5.metric("Actual EBITDA", f"${actual_ebitda:,.0f}")
col6.metric("EBITDA Impact", f"${ebitda_impact:,.0f}")

st.header("Financial Ratios")
st.metric("EBITDA Margin", f"{(actual_ebitda / actual_revenue) * 100:.2f}%")
