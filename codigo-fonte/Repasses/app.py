import sys
from pathlib import Path


SOURCE_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SOURCE_ROOT))

from app import app


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5051, debug=True)
