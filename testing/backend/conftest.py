import sys
from pathlib import Path

# Add the repo root to sys.path so imports like 'from main.xxx import ...' resolve
# This works whether pytest is run from the repo root or from testing/backend/
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
