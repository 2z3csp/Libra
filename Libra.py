# Libra.py（リポジトリ直下）
import sys
from pathlib import Path

# src を import 探索パスに追加
ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from libra.app import main

if __name__ == "__main__":
    main()
