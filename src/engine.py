import pandas as pd
import json
import logging
from pathlib import Path
from typing import Dict, Any, List
from openpyxl import load_workbook
from openpyxl.chart import LineChart, BarChart, DoughnutChart, Reference, Series
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.formatting.rule import DataBarRule
from openpyxl.worksheet.table import Table, TableStyleInfo
from openpyxl.utils import get_column_letter

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

class FinancialEngine:
    def __init__(self, client_folder_path: str):
        self.client_path = Path(client_folder_path)
        self.config_path = self.client_path / 'config.json'
        
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config missing: {self.config_path}")
            
        with open(self.config_path, 'r') as f:
            self.config: Dict[str, Any] = json.load(f)

    def _get_category(self, description: str) -> str:
        desc_lower = str(description).lower()
        for category, keywords in self.config['categories'].items():
            for keyword in keywords:
                if keyword in desc_lower:
                    return category
        return "Uncategorized"

    def run(self) -> None:
        # 1. Load & Process Data
        input_path = self.client_path / self.config['files']['input']
        output_path = self.client_path / self.config['files']['output']
        
        logger.info(f"[INFO] Processing: {input_path}")
        df = pd.read_csv(input_path)
        
        # Column Mapping
        mapping = self.config['column_mapping']
        df = df.rename(columns={
            mapping['date']: 'Date',
            mapping['description']: 'Description',
            mapping['amount']: 'Amount'
        })
        
        # Cleaning
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        df = df.dropna(subset=['Date'])
        df['Description'] = df['Description'].fillna("").astype(str).str.strip()
        df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce').fillna(0)
        df['Category'] = df['Description'].apply(self._get_category)
        
        # --- PREPARE DATA FOR DASHBOARD ---
        
        # 1. Expense Breakdown (Total)
        expenses = df[df['Category'] != 'Revenue']
        category_summary = expenses.groupby('Category')['Amount'].sum().reset_index()
        category_summary = category_summary.sort_values('Amount', ascending=False)
        
        # 2. Year-over-Year Matrix (For the "Accurate" Chart)
        # We pivot data: Index=Month(1-12), Columns=Year
        df['Year'] = df['Date'].dt.year
        df['MonthNum'] = df['Date'].dt.month
        df['MonthName'] = df['Date'].dt.strftime('%b') # Jan, Feb...
        
        # Create the Pivot Table for the Chart
        yoy_chart_data = df.pivot_table(index='MonthNum', columns='Year', values='Amount', aggfunc='sum').fillna(0)
        # Add Month Names for readability
        month_map = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun', 
                     7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
        yoy_chart_data.insert(0, 'Month', yoy_chart_data.index.map(month_map))
        
        # 3. Yearly Tables Data (For separate tables)
        # We will extract these dynamically in the writing phase
        
        # --- WRITE TO EXCEL ---
        logger.info(f"[INFO] Designing Year-over-Year Dashboard...")
        
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Sheet 1: Dashboard - Expense Table (Top Left)
            category_summary.to_excel(writer, sheet_name='Dashboard', startrow=3, startcol=1, index=False)
            
            # Sheet 2: Hidden Data for Chart (YoY Pivot)
            yoy_chart_data.to_excel(writer, sheet_name='ChartData', index=False)
            
            # We will write the yearly tables manually using openpyxl next
            # Raw Data
            df.to_excel(writer, sheet_name='Raw Data', index=False)

        # Apply Styles & Generate Dynamic Tables
        self._style_excel(output_path, category_summary, df)
        logger.info("[SUCCESS] Multi-Year Dashboard Generated.")

    def _style_excel(self, file_path: Path, cat_summary: pd.DataFrame, full_df: pd.DataFrame) -> None:
        wb = load_workbook(file_path)
        ws = wb['Dashboard']
        ws_chart = wb['ChartData']
        
        # --- 0. HEADER ---
        report_title = self.config.get('report_title', 'Executive Financial Report')
        ws['B2'] = report_title
        ws['B2'].font = Font(size=22, bold=True, color="2F5597") 
        ws.sheet_view.showGridLines = False 

        # --- 1. EXPENSE TABLE (Top Left) ---
        cat_rows = len(cat_summary)
        t1_end = 4 + cat_rows
        tab1 = Table(displayName="ExpenseTable", ref=f"B4:C{t1_end}")
        style = TableStyleInfo(name="TableStyleMedium9", showRowStripes=True)
        tab1.tableStyleInfo = style
        ws.add_table(tab1)
        
        # Currency Format for Expense Table
        for cell in ws[f"C5:C{t1_end}"]:
            cell[0].number_format = '"$"#,##0.00_-'

        # --- 2. DOUGHNUT CHART (Right of Expense Table) ---
        chart1 = DoughnutChart()
        chart1.title = "Total Expense Distribution"
        chart1.style = 26
        cats = Reference(ws, min_col=2, min_row=5, max_row=t1_end)
        data = Reference(ws, min_col=3, min_row=4, max_row=t1_end)
        chart1.add_data(data, titles_from_data=True)
        chart1.set_categories(cats)
        ws.add_chart(chart1, "E4")

        # --- 3. DYNAMIC YEARLY TABLES (Stacked Below) ---
        # Get list of years from data, sorted
        years = sorted(full_df['Year'].unique())
        
        current_row = t1_end + 4 # Start placing yearly tables below the first table
        
        for year in years:
            # Filter data for this year
            year_data = full_df[full_df['Year'] == year]
            # Group by Month
            monthly = year_data.groupby('MonthNum')['Amount'].sum().reset_index()
            monthly['Month'] = monthly['MonthNum'].apply(lambda x: pd.to_datetime(str(x), format='%m').strftime('%B'))
            monthly = monthly[['Month', 'Amount']] # Keep clean cols
            
            # Write Header
            ws[f'B{current_row}'] = f"{year} Financial Performance"
            ws[f'B{current_row}'].font = Font(bold=True, size=14, color="2F5597")
            current_row += 1
            
            # Write Data
            # Header Row
            ws[f'B{current_row}'] = "Month"
            ws[f'C{current_row}'] = "Revenue"
            start_table_row = current_row
            
            # Data Rows
            for _, row in monthly.iterrows():
                current_row += 1
                ws[f'B{current_row}'] = row['Month']
                ws[f'C{current_row}'] = row['Amount']
                ws[f'C{current_row}'].number_format = '"$"#,##0.00_-'

            # Create Table Object
            table_name = f"Table_{year}"
            tab = Table(displayName=table_name, ref=f"B{start_table_row}:C{current_row}")
            tab.tableStyleInfo = style
            ws.add_table(tab)
            
            # Add Data Bars
            rule = DataBarRule(start_type='min', end_type='max', color="638EC6")
            ws.conditional_formatting.add(f"C{start_table_row+1}:C{current_row}", rule)
            
            # Add Spacer for next year
            current_row += 3

        # --- 4. YEAR-OVER-YEAR CHART (The "Accurate" Graph) ---
        # We build a Line Chart comparing columns from the 'ChartData' sheet
        chart2 = LineChart()
        chart2.title = "Year-Over-Year Growth Comparison"
        chart2.style = 12
        chart2.y_axis.title = "Revenue ($)"
        chart2.x_axis.title = "Month"
        chart2.height = 15
        chart2.width = 25
        
        # Data is in 'ChartData' sheet
        # Row 1 is Headers (Month, 2024, 2025...)
        # Col 1 is Month Names
        max_col = ws_chart.max_column
        max_row = ws_chart.max_row
        
        # Categories (Jan-Dec) -> Column A
        cats = Reference(ws_chart, min_col=1, min_row=2, max_row=max_row)
        
        # Data Series (One series per Year column)
        data = Reference(ws_chart, min_col=2, min_row=1, max_row=max_row, max_col=max_col)
        
        chart2.add_data(data, titles_from_data=True)
        chart2.set_categories(cats)
        
        # Place this big chart on the right side
        ws.add_chart(chart2, "H4")

        # Adjust Column Widths
        ws.column_dimensions['B'].width = 20
        ws.column_dimensions['C'].width = 18

        wb.save(file_path)