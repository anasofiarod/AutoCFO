# AutoCFO: Automated Financial Reporting Engine

**AutoCFO** is a powerful financial automation tool designed to streamline the process of categorizing transactions, generating professional Excel reports, and visualizing financial health via an interactive dashboard.

Turn raw transaction data into executive-level financial insights in seconds.

## Features

-   **Multi-Client Support**: Dynamically manage and switch between multiple client portfolios.
-   **Automated Financial Engine**: Processes raw bank CSV exports, cleans data, and categorizes expenses automatically based on configurable rules.
-   **Professional Excel Reports**: Generates "Board-Ready" Excel files containing:
    -   **Executive Dashboard** with KPIs (Revenue, Expenses, Net Profit).
    -   **Expense Breakdown** with distribution analysis.
    -   **Yearly & Monthly Trends** with automated formatting and conditional styling.
    -   **Embedded Charts** for visual data interpretation.
-   **Interactive Web Dashboard**: A Streamlit-based app to explore data:
    -   Filter by **Client**, **Year**, and **Month**.
    -   Visualize Cash Flow Trends and Expense Composition.
    -   View real-time KPIs.

##  Project Structure

```text
AutoCFO/
├── clients/             # Store client data here (e.g., clients/AcmeCorp/data.csv)
├── examples/            # Demo data for testing
├── src/
│   ├── engine.py        # Core logic for data processing & Excel generation
│   └── dashboard.py     # Streamlit web application
├── main.py              # CLI Entry point
└── requirements.txt     # Python dependencies
```


### Prerequisites

-   Python 3.8+
-   Git

### Installation

1.  **Clone the repository**:
    ```bash
    git clone <your-repo-url>
    cd AutoCFO
    ```

2.  **Set up the Virtual Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Windows: .venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## 🛠️ Usage

### 1. Run the Web Dashboard
Launch the interactive dashboard to view financial data in your browser.
```bash
./.venv/bin/python main.py --web
```
*Select `demo_client` from the sidebar to see it in action.*

### 2. Process a New Client
1.  Create a folder in `clients/`:
    ```bash
    mkdir clients/MynewClient
    ```
2.  Add their raw `data.csv` to that folder.
3.  Run the engine to generate their Excel report:
    ```bash
    ./.venv/bin/python main.py MynewClient
    ```
    *This creates `Financial_Report.xlsx` in the client's folder.*

### 3. Run with Demo Data
Generate a report for the included demo data:
```bash
./.venv/bin/python main.py --demo
```

## Data Format
Input `data.csv` files should have the following columns (headers are configurable in `src/engine.py` if needed):
-   `Date`: Transaction date (e.g., YYYY-MM-DD)
-   `Memo` / `Description`: Transaction details
-   `Cost` / `Amount`: Transaction value

---
*Built with Python, pandas, openpyxl, and Streamlit.*
