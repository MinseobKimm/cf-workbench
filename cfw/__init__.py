from pathlib import Path
import os
import sys

_ROOT = Path(__file__).resolve().parent.parent
_SRC = _ROOT / "src"
if _SRC.exists():
    sys.path.insert(0, str(_SRC))
_UCRT64_BIN = Path(r"C:\msys64\ucrt64\bin")
if (_UCRT64_BIN / "g++.exe").exists():
    os.environ["PATH"] = f"{_UCRT64_BIN}{os.pathsep}{os.environ.get('PATH', '')}"

from cf_workbench import __version__

__all__ = ["__version__"]
