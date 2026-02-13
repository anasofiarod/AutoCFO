import argparse
import sys
import subprocess
from pathlib import Path
from src.engine import FinancialEngine

def launch_dashboard() -> None:
    """Helper to run the Streamlit app"""
    print("[INFO] Launching Web Dashboard...")
    script_path = Path("src") / "dashboard.py"
    subprocess.run([sys.executable, "-m", "streamlit", "run", str(script_path)])

def main() -> None:
    parser = argparse.ArgumentParser(description="Auto-CFO: Financial Automation Suite")
    
    parser.add_argument("client_name", nargs='?', default="demo_client", help="Client folder name")
    parser.add_argument("--web", action="store_true", help="Launch the Interactive Web Dashboard")
    parser.add_argument("--demo", action="store_true", help="Use the examples folder (Default for portfolio)")

    args = parser.parse_args()

    if args.web:
        launch_dashboard()
        return

    print(f"[INFO] Starting Auto-CFO Engine for '{args.client_name}'...")
    
    # Determine folder (Client vs Example)
    base_dir = "examples" if args.demo else "clients"
    project_root = Path.cwd()
    client_path = project_root / base_dir / args.client_name

    try:
        engine = FinancialEngine(str(client_path))
        engine.run()
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()