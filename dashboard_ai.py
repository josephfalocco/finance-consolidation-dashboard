import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from query_engine import ask_financial_question, get_data_summary

# === PASSWORD PROTECTION ===
def check_password():
    """Returns True if the user entered the correct password."""
    
    def password_entered():
        """Checks whether the password entered is correct."""
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store password
        else:
            st.session_state["password_correct"] = False

    # First run, show input
    if "password_correct" not in st.session_state:
        st.text_input(
            "Password", 
            type="password", 
            on_change=password_entered, 
            key="password",
            placeholder="Enter password to access dashboard"
        )
        st.caption("This demo is password protected. Contact Joey for access.")
        return False
    
    # Password was wrong, show input + error
    elif not st.session_state["password_correct"]:
        st.text_input(
            "Password", 
            type="password", 
            on_change=password_entered, 
            key="password",
            placeholder="Enter password to access dashboard"
        )
        st.error("😕 Incorrect password. Please try again.")
        return False
    
    # Password correct
    else:
        return True

# === PAGE CONFIG ===
st.set_page_config(
    page_title="AI-Powered Finance Dashboard",
    page_icon="🤖",
    layout="wide"
)

# === CONFIGURATION ===
DATA_PATH = os.path.join(os.path.dirname(__file__), "data", "consolidated_master.csv")
CHART_TEMPLATE = "plotly_dark"

# === LOAD DATA ===
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"])
    df["Month"] = df["Date"].dt.to_period("M").astype(str)
    return df

# === INITIALIZE SESSION STATE FOR CHAT ===
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# === MAIN APP ===
def main():
    st.title("🤖 AI-Powered Finance Dashboard")
    st.markdown("**Automated consolidation + Natural language queries**")
    st.markdown("*Ask questions about your financial data in plain English*")
    
    df = load_data()
    
    # === SIDEBAR FILTERS ===
    st.sidebar.header("Filters")
    
    all_departments = ["All Departments"] + sorted(df["Department"].unique().tolist())
    selected_dept = st.sidebar.selectbox("Select Department", all_departments)
    
    min_date = df["Date"].min().date()
    max_date = df["Date"].max().date()
    
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    
    all_categories = ["All Categories"] + sorted(df["Category"].unique().tolist())
    selected_category = st.sidebar.selectbox("Select Category", all_categories)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About This Demo")
    st.sidebar.markdown("""
    This dashboard demonstrates:
    
    **1. Automated Consolidation**
    4 department CSVs → 1 unified view
    
    **2. AI-Powered Queries**
    Ask questions in plain English.
    The AI writes pandas code, executes 
    it against real data, and shows 
    its work.
    
    *No hallucinated numbers — every 
    answer is computed from actual data.*
    """)
    
    filter_key = f"{selected_dept}_{date_range}_{selected_category}"
    
    # Apply filters
    filtered_df = df.copy()
    
    if selected_dept != "All Departments":
        filtered_df = filtered_df[filtered_df["Department"] == selected_dept]
    
    if len(date_range) == 2:
        start_date, end_date = date_range
        filtered_df = filtered_df[
            (filtered_df["Date"].dt.date >= start_date) & 
            (filtered_df["Date"].dt.date <= end_date)
        ]
    
    if selected_category != "All Categories":
        filtered_df = filtered_df[filtered_df["Category"] == selected_category]
    
    st.markdown("---")
    
    # === CALCULATE KPIs ===
    total_revenue = filtered_df[filtered_df["Type"] == "Revenue"]["Amount"].sum()
    total_expenses = filtered_df[filtered_df["Type"] == "Expense"]["Amount"].sum()
    net_income = total_revenue - total_expenses
    profit_margin = (net_income / total_revenue * 100) if total_revenue > 0 else 0
    
    # === KPI CARDS ROW ===
    st.subheader("Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    col1.metric("Total Revenue", f"${total_revenue/1_000_000:.2f}M")
    col2.metric("Total Expenses", f"${total_expenses/1_000_000:.2f}M")
    col3.metric("Net Income", f"${net_income/1_000_000:.2f}M")
    col4.metric("Profit Margin", f"{profit_margin:.1f}%" if total_revenue > 0 else "N/A")
    
    st.markdown("---")
    
    # === CHARTS ROW 1: Revenue and Expenses by Department ===
    chart_col1, chart_col2 = st.columns(2)
    
    # --- Revenue by Department ---
    with chart_col1:
        st.subheader("Revenue by Department")
        
        revenue_by_dept = filtered_df[filtered_df["Type"] == "Revenue"].groupby("Department")["Amount"].sum().reset_index()
        revenue_by_dept.columns = ["Department", "Revenue"]
        revenue_by_dept = revenue_by_dept.sort_values("Revenue", ascending=False)
        
        if len(revenue_by_dept) > 0:
            fig_revenue = px.bar(
                revenue_by_dept,
                x="Department",
                y="Revenue",
                color="Department",
                text=revenue_by_dept["Revenue"].apply(lambda x: f"${x/1_000_000:.1f}M"),
                color_discrete_sequence=["#2ecc71"],
                template=CHART_TEMPLATE
            )
            
            y_max = revenue_by_dept["Revenue"].max() * 1.2
            
            fig_revenue.update_layout(
                showlegend=False,
                yaxis_title="Revenue ($)",
                xaxis_title="",
                yaxis_tickformat="$,.0f",
                yaxis_range=[0, y_max],
                height=400,
                bargap=0.5,
                uniformtext_minsize=10,
                uniformtext_mode='show'
            )
            
            fig_revenue.update_traces(
                textposition="outside",
                textfont_size=12,
                marker_line_width=0,
                width=0.5
            )
            
            st.plotly_chart(fig_revenue, use_container_width=True, key=f"rev_dept_{filter_key}")
        else:
            st.info("No revenue data for selected filters.")
    
    # --- Expenses by Department ---
    with chart_col2:
        st.subheader("Expenses by Department")
        
        expenses_by_dept = filtered_df[filtered_df["Type"] == "Expense"].groupby("Department")["Amount"].sum().reset_index()
        expenses_by_dept.columns = ["Department", "Expenses"]
        expenses_by_dept = expenses_by_dept.sort_values("Expenses", ascending=False)
        
        if len(expenses_by_dept) > 0:
            fig_expenses = px.bar(
                expenses_by_dept,
                x="Department",
                y="Expenses",
                color="Department",
                text=expenses_by_dept["Expenses"].apply(lambda x: f"${x/1_000_000:.1f}M"),
                color_discrete_sequence=px.colors.qualitative.Set2,
                template=CHART_TEMPLATE
            )
            
            y_max = expenses_by_dept["Expenses"].max() * 1.2
            
            fig_expenses.update_layout(
                showlegend=False,
                yaxis_title="Expenses ($)",
                xaxis_title="",
                yaxis_tickformat="$,.0f",
                yaxis_range=[0, y_max],
                height=400,
                bargap=0.5,
                uniformtext_minsize=10,
                uniformtext_mode='show'
            )
            
            fig_expenses.update_traces(
                textposition="outside",
                textfont_size=12,
                marker_line_width=0,
                width=0.5
            )
            
            st.plotly_chart(fig_expenses, use_container_width=True, key=f"exp_dept_{filter_key}")
        else:
            st.info("No expense data for selected filters.")
    
    st.markdown("---")
    
    # === CHARTS ROW 2: Monthly Trend and Expense Breakdown ===
    chart_col3, chart_col4 = st.columns([2, 1])
    
    # --- Monthly Trend ---
    with chart_col3:
        st.subheader("Monthly Trend: Revenue vs Expenses")
        
        monthly_revenue = filtered_df[filtered_df["Type"] == "Revenue"].groupby("Month")["Amount"].sum().reset_index()
        monthly_revenue.columns = ["Month", "Revenue"]
        
        monthly_expenses = filtered_df[filtered_df["Type"] == "Expense"].groupby("Month")["Amount"].sum().reset_index()
        monthly_expenses.columns = ["Month", "Expenses"]
        
        monthly_trend = pd.merge(monthly_revenue, monthly_expenses, on="Month", how="outer").fillna(0)
        monthly_trend = monthly_trend.sort_values("Month")
        monthly_trend["Net Income"] = monthly_trend["Revenue"] - monthly_trend["Expenses"]
        
        if len(monthly_trend) > 0:
            fig_trend = go.Figure()
            
            fig_trend.add_trace(go.Scatter(
                x=monthly_trend["Month"],
                y=monthly_trend["Revenue"],
                mode="lines+markers",
                name="Revenue",
                line=dict(color="#2ecc71", width=3),
                marker=dict(size=8)
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=monthly_trend["Month"],
                y=monthly_trend["Expenses"],
                mode="lines+markers",
                name="Expenses",
                line=dict(color="#e74c3c", width=3),
                marker=dict(size=8)
            ))
            
            fig_trend.add_trace(go.Scatter(
                x=monthly_trend["Month"],
                y=monthly_trend["Net Income"],
                mode="lines+markers",
                name="Net Income",
                line=dict(color="#3498db", width=2, dash="dash"),
                marker=dict(size=6)
            ))
            
            fig_trend.update_layout(
                yaxis_title="Amount ($)",
                xaxis_title="Month",
                yaxis_tickformat="$,.0f",
                height=450,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                ),
                hovermode="x unified",
                template=CHART_TEMPLATE
            )
            
            st.plotly_chart(fig_trend, use_container_width=True, key=f"trend_{filter_key}")
        else:
            st.info("No data available for selected filters.")
    
    # --- Expense Breakdown by Category (Pie Chart) ---
    with chart_col4:
        st.subheader("Expenses by Category")
        
        expenses_by_cat = filtered_df[filtered_df["Type"] == "Expense"].groupby("Category")["Amount"].sum().reset_index()
        expenses_by_cat.columns = ["Category", "Amount"]
        expenses_by_cat = expenses_by_cat.sort_values("Amount", ascending=False)
        
        if len(expenses_by_cat) > 8:
            top_cats = expenses_by_cat.head(8)
            other_amount = expenses_by_cat.tail(len(expenses_by_cat) - 8)["Amount"].sum()
            other_row = pd.DataFrame({"Category": ["Other"], "Amount": [other_amount]})
            expenses_by_cat = pd.concat([top_cats, other_row], ignore_index=True)
        
        if len(expenses_by_cat) > 0:
            fig_pie = px.pie(
                expenses_by_cat,
                values="Amount",
                names="Category",
                hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Set2,
                template=CHART_TEMPLATE
            )
            
            fig_pie.update_layout(
                height=450,
                showlegend=True,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=-0.3,
                    xanchor="center",
                    x=0.5,
                    font=dict(size=10)
                )
            )
            
            fig_pie.update_traces(
                textposition="inside",
                textinfo="percent",
                hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>"
            )
            
            st.plotly_chart(fig_pie, use_container_width=True, key=f"pie_{filter_key}")
        else:
            st.info("No expense data for selected filters.")
    
    st.markdown("---")
    
    # ===================================================================
    # === AI CHAT INTERFACE - THE NEW SECTION ===
    # ===================================================================
    
    st.subheader("🤖 Ask Your Data a Question")
    st.markdown("*Type a question in plain English. The AI writes code, executes it against real data, and shows its work.*")
    
    # Example question buttons
    st.markdown("**Try these examples:**")
    example_col1, example_col2, example_col3, example_col4 = st.columns(4)
    
    with example_col1:
        if st.button("💰 Total Revenue?", use_container_width=True):
            st.session_state.example_question = "What was total revenue for the year?"
    
    with example_col2:
        if st.button("📊 Top Expenses?", use_container_width=True):
            st.session_state.example_question = "What are the top 5 expense categories?"
    
    with example_col3:
        if st.button("🏢 Biggest Spender?", use_container_width=True):
            st.session_state.example_question = "Which department had the highest expenses?"
    
    with example_col4:
        if st.button("📈 Q1 Marketing?", use_container_width=True):
            st.session_state.example_question = "What were Marketing expenses in Q1?"
    
    # Check if an example button was clicked
    default_value = st.session_state.get("example_question", "")
    if default_value:
        # Clear the example after using it
        st.session_state.example_question = ""
    
    # Question input
    user_question = st.text_input(
        "Your question:",
        value=default_value,
        placeholder="e.g., What was our profit margin in Q3? Which month had the highest revenue?",
        key="question_input"
    )
    
    # Process question
    if user_question:
        with st.spinner("🔍 Analyzing your data..."):
            result = ask_financial_question(user_question)
        
        # Display the answer prominently
        st.markdown("### Answer")
        if result["success"]:
            # Use st.code for multi-line answers (preserves formatting)
            if "\n" in result["answer"]:
                st.success("Query executed successfully!")
                st.text(result["answer"])
            else:
                st.success(result["answer"])
        else:
            st.error(result["answer"])
        
        # Show the code in an expander (the audit trail)
        with st.expander("🔧 View the code that generated this answer", expanded=False):
            if result["code"]:
                st.code(result["code"], language="python")
                if result["explanation"]:
                    st.markdown(f"**Explanation:** {result['explanation']}")
            else:
                st.info("No code was generated for this query.")
        
        # Add to chat history
        st.session_state.chat_history.append({
            "question": user_question,
            "answer": result["answer"],
            "code": result["code"],
            "success": result["success"]
        })
    
    # Show recent chat history
    if len(st.session_state.chat_history) > 1:
        with st.expander("📜 Previous Questions", expanded=False):
            # Show in reverse order (newest first), skip the most recent (already shown above)
            for i, chat in enumerate(reversed(st.session_state.chat_history[:-1])):
                st.markdown(f"**Q:** {chat['question']}")
                st.markdown(f"**A:** {chat['answer']}")
                st.markdown("---")
    
    st.markdown("---")
    
    # === DATA TABLE (Expandable) ===
    with st.expander("📋 View Detailed Transaction Data", expanded=False):
        st.markdown("**Filtered Transactions**")
        
        display_df = filtered_df.copy()
        display_df["Date"] = display_df["Date"].dt.strftime("%Y-%m-%d")
        display_df["Amount"] = display_df["Amount"].apply(lambda x: f"${x:,.2f}")
        display_df = display_df[["Date", "Department", "Category", "Type", "Amount", "Description"]]
        
        search_term = st.text_input("Search transactions", placeholder="Type to search...", key="search_transactions")
        
        if search_term:
            mask = display_df.apply(lambda row: search_term.lower() in row.astype(str).str.lower().str.cat(sep=' '), axis=1)
            display_df = display_df[mask]
        
        st.dataframe(display_df, use_container_width=True, height=400)
        st.caption(f"Showing {len(display_df):,} transactions")
    
    # === FOOTER ===
    st.markdown("---")
    col_foot1, col_foot2, col_foot3 = st.columns(3)
    
    with col_foot1:
        st.caption(f"📅 Data Range: {df['Date'].min().strftime('%Y-%m-%d')} to {df['Date'].max().strftime('%Y-%m-%d')}")
    
    with col_foot2:
        st.caption(f"📊 Total Transactions: {len(filtered_df):,} of {len(df):,}")
    
    with col_foot3:
        st.caption(f"🤖 AI-Powered Demo by Joseph Falocco")

if __name__ == "__main__":
    if check_password():
        main()