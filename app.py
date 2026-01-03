import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide")
st.title("Interactive Telco Business Performance")

# --- Page Navigation and Reset Button ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a Page", ["Financial Model", "Graphical Analysis"])

st.sidebar.title("Actions")
# NEW: A button to force a hard reset of the session state if things get stuck
if st.sidebar.button("Clear Cache & Reset App", type="primary"):
    # Delete the stored dataframes from memory
    for key in ['editor_df', 'final_report_df']:
        if key in st.session_state:
            del st.session_state[key]
    # Rerun the app from the top
    st.rerun()

# --- Define Constants ---
MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
ALL_METRICS = [
    "Subscribers (Budget) (M)", "Subscribers (Actual) (M)",
    "ARPU (Budget)", "ARPU (Actual)",
    "Revenue (Budget) (M)", "Revenue (Actual) (M)", "Revenue Impact (M)",
    "EBITDA (Budget) (M)", "EBITDA (Actual) (M)", "EBITDA Impact (M)",
]

# --- Sidebar for Assumptions ---
st.sidebar.title("Key Assumptions")
opex_as_percent_of_revenue = st.sidebar.slider("Opex as % of Revenue", min_value=10, max_value=80, value=40)

# --- PAGE 1: The Interactive Financial Model ---
if page == "Financial Model":

    # --- Initialize Session State ---
    if 'editor_df' not in st.session_state:
        initial_actuals = {
            "Subscribers (Actual) (M)": [x / 1_000_000 for x in [1010000, 1012000, 1018000, 1025000, 1030000, 1028000, 1035000, 1042000, 1050000, 1060000, 1065000, 1070000]],
            "ARPU (Actual)": [52.0, 52.1, 51.9, 52.3, 52.4, 52.5, 52.6, 52.7, 52.8, 52.9, 53.0, 53.2],
        }
        st.session_state.editor_df = pd.DataFrame(initial_actuals, index=MONTHS).T

    # --- Display the User Input Section ---
    st.header("1. Edit Actual Figures")
    st.write("Make your changes in the table below. When you're ready, click the button at the bottom.")

    edited_inputs = st.data_editor(
        st.session_state.editor_df,
        column_config={col: st.column_config.NumberColumn(format="%.1f") for col in MONTHS},
        use_container_width=True
    )

    # --- The "Calculate" Button ---
    if st.button("Calculate & Update Totals", type="primary"):
        st.session_state.editor_df = edited_inputs
        st.header("2. Final Report")

        report_df = pd.DataFrame(index=ALL_METRICS, columns=MONTHS + ['Full Year'], dtype=float)

        report_df.loc["Subscribers (Budget) (M)", MONTHS] = [x / 1_000_000 for x in [1000000, 1005000, 1010000, 1015000, 1020000, 1025000, 1030000, 1035000, 1040000, 1045000, 1050000, 1055000]]
        report_df.loc["ARPU (Budget)", MONTHS] = [50.0, 50.1, 50.2, 50.3, 50.4, 50.5, 50.6, 50.7, 50.8, 50.9, 51.0, 51.1]
        report_df.loc[st.session_state.editor_df.index, MONTHS] = st.session_state.editor_df

        # --- Perform All Calculations ---
        report_df.loc['Revenue (Budget) (M)'] = report_df.loc['Subscribers (Budget) (M)'] * report_df.loc['ARPU (Budget)']
        report_df.loc['Revenue (Actual) (M)'] = report_df.loc['Subscribers (Actual) (M)'] * report_df.loc['ARPU (Actual)']
        report_df.loc['Revenue Impact (M)'] = report_df.loc['Revenue (Actual) (M)'] - report_df.loc['Revenue (Budget) (M)']
        opex_multiplier = 1 - (opex_as_percent_of_revenue / 100)
        report_df.loc['EBITDA (Budget) (M)'] = report_df.loc['Revenue (Budget) (M)'] * opex_multiplier
        report_df.loc['EBITDA (Actual) (M)'] = report_df.loc['Revenue (Actual) (M)'] * opex_multiplier
        report_df.loc['EBITDA Impact (M)'] = report_df.loc['EBITDA (Actual) (M)'] - report_df.loc['EBITDA (Budget) (M)']

        for metric in report_df.index:
            if "ARPU" in metric:
                report_df.loc[metric, 'Full Year'] = report_df.loc[metric, MONTHS].mean()
            else:
                report_df.loc[metric, 'Full Year'] = report_df.loc[metric, MONTHS].sum()

        st.session_state.final_report_df = report_df

        # --- Display the Final, Calculated Table ---
        def highlight_impact(row):
            style = [''] * len(row)
            if "Impact" in row.name:
                for i, val in enumerate(row):
                    if pd.notna(val): style[i] = f'color: {"green" if val >= 0 else "red"}'
            return style

        arpu_rows = [m for m in ALL_METRICS if "ARPU" in m]
        million_rows = [m for m in ALL_METRICS if "(M)" in m]

        st.dataframe(
            report_df.style
                .format("{:,.1f}", subset=pd.IndexSlice[million_rows, :])
                .format("{:,.2f}", subset=pd.IndexSlice[arpu_rows, :])
                .apply(highlight_impact, axis=1),
            use_container_width=True
        )

# --- PAGE 2: The Graphical Analysis ---
elif page == "Graphical Analysis":
    st.header("Graphical Performance Analysis")

    if 'final_report_df' not in st.session_state:
        st.warning("Please go to the 'Financial Model' page and click 'Calculate & Update Totals' first to generate data for the graphs.")
    else:
        df = st.session_state.final_report_df

        def create_comparison_chart(title, budget_row, actual_row):
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=MONTHS, y=df.loc[budget_row, MONTHS], mode='lines+markers', name='Budget', line=dict(dash='dot')))
            fig.add_trace(go.Scatter(x=MONTHS, y=df.loc[actual_row, MONTHS], mode='lines+markers', name='Actual'))
            yaxis_title = "Value (M)" if "(M)" in title else "Value"
            fig.update_layout(title_text=title, yaxis_title=yaxis_title, legend_title_text='Legend')
            st.plotly_chart(fig, use_container_width=True)

        create_comparison_chart("Subscribers Performance (M)", "Subscribers (Budget) (M)", "Subscribers (Actual) (M)")
        create_comparison_chart("ARPU Performance", "ARPU (Budget)", "ARPU (Actual)")
        create_comparison_chart("Revenue Performance (M)", "Revenue (Budget) (M)", "Revenue (Actual) (M)")

