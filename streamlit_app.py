import sys
from pathlib import Path

# Add the project root to sys.path to ensure 'app' package is findable
# when running from the root directory.
PROJECT_ROOT = Path(__file__).parent.absolute()
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Now import and run the app
from app.ui_streamlit import run_streamlit_app

if __name__ == "__main__":
    run_streamlit_app()
