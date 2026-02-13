# AutoCFO

Automated Financial Officer - A tool to automate financial reporting and visualization.

## Features
- **Financial Engine**: Processes raw transaction data (CSV) and categorizes expenses.
- **Excel Reports**: Generates detailed Excel reports with Pivot Tables and Charts.
- **Interactive Dashboard**: A Streamlit-based web dashboard to visualize financial data.

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd AutoCFO
    ```

2.  **Set up a Virtual Environment**:
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Quick Start (Demo)
To run the analysis on the included demo client:

```bash
# Using the helper script (Mac/Linux)
./run_demo.sh

# Or manually
python3 main.py --demo
```

### Web Dashboard
To launch the interactive dashboard:

```bash
python3 main.py --web
```

### Processing a Client
To process a specific client folder (must exist in `clients/`):

```bash
python3 main.py client_folder_name
```

## Project Structure
- `src/`: Source code for the engine and dashboard.
- `clients/`: Place client data folders here.
- `examples/`: Example data for demonstration.
- `main.py`: Entry point for the application.

## Requirements
- Python 3.8+
- pandas, openpyxl, streamlit, plotly
