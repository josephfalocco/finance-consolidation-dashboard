# 📊 Finance Consolidation Dashboard

**Automated departmental finance consolidation — from 4 separate files to one live dashboard in seconds.**

🔗 **[Live Demo](https://finance-consolidation-dashboard.streamlit.app)**

---

## The Problem

Every finance team knows this pain:

- 4 departments submit separate expense/revenue reports
- Someone manually copies and pastes data into a master spreadsheet
- Hours of reconciliation, error-checking, and formatting
- By the time the report is ready, leadership is already asking for updates

**Traditional process: 2-4 hours**

---

## The Solution

Departments drop their files into a shared folder. Automation handles the rest.

- ✅ Files automatically consolidated into a single dataset
- ✅ Data validated and standardized
- ✅ Live dashboard updates instantly
- ✅ Filter by department, date range, or category
- ✅ Search any transaction in seconds

**Automated process: 12 seconds**

---

## Dashboard Features

| Feature | Description |
|---------|-------------|
| **KPI Cards** | Total Revenue, Expenses, Net Income, Profit Margin |
| **Revenue by Department** | Bar chart with drill-down capability |
| **Expenses by Department** | Comparative view across cost centers |
| **Monthly Trend** | Line chart showing Revenue vs Expenses vs Net Income |
| **Expense Breakdown** | Pie chart by category |
| **Transaction Search** | Expandable table with full-text search |
| **Dynamic Filters** | Department, date range, and category filters |

---

## Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     SHAREPOINT                              │
│                                                             │
│   📁 Department-Submissions/                                │
│      ├── sales_weekly.csv                                   │
│      ├── marketing_weekly.csv                               │
│      ├── operations_weekly.csv                              │
│      └── finance_weekly.csv                                 │
│                                                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼ Python consolidation script
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                                                             │
│   📁 Consolidated-Output/                                   │
│      └── consolidated_master.csv                            │
│                                                             │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼ Streamlit dashboard
                      │
┌─────────────────────┴───────────────────────────────────────┐
│                                                             │
│   🌐 Live Dashboard                                         │
│      finance-consolidation-dashboard.streamlit.app          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Data Storage** | SharePoint / CSV |
| **Processing** | Python, pandas |
| **Visualization** | Plotly |
| **Dashboard** | Streamlit |
| **Deployment** | Streamlit Cloud |

---

## Sample Data

This demo uses realistic synthetic financial data representing a mid-size company:

| Department | Revenue | Expenses | Transactions |
|------------|---------|----------|--------------|
| Sales | $19.9M | $2.0M | 389 |
| Marketing | — | $2.5M | 327 |
| Operations | — | $3.3M | 406 |
| Finance | — | $1.0M | 247 |
| **Total** | **$19.9M** | **$8.8M** | **1,369** |

Data includes realistic seasonality, expense categories, vendor names, and transaction descriptions.

---

## Local Development
```bash
# Clone the repo
git clone https://github.com/josephfalocco/finance-consolidation-dashboard.git
cd finance-consolidation-dashboard

# Install dependencies
pip install -r requirements.txt

# Run the dashboard
streamlit run dashboard.py
```

---

## About

Built by **Joseph Falocco** — Finance & Data Professional

I help finance teams escape spreadsheet chaos by building automated reporting systems that deliver answers in seconds, not days.

🌐 [josephfalocco.com](https://josephfalocco.com)  

---

## License

MIT — use it, learn from it, build on it.
