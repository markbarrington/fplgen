from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
CODE_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"


def data_file(filename, for_write=False):
    if for_write:
        DATA_DIR.mkdir(exist_ok=True)
        return DATA_DIR / filename

    candidates = [
        DATA_DIR / filename,
        Path.cwd() / filename,
        CODE_DIR / filename,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate

    searched = ", ".join(str(candidate) for candidate in candidates)
    raise FileNotFoundError("%s not found. Searched: %s" % (filename, searched))
