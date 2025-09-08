from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# List of relative paths where we want .gitkeep files
FOLDERS = [
    "data/raw",
    "data/processed",
    "notebooks",
    "scripts",
    "outputs/maps",
    "outputs/reports",
    "docs",
]


def add_gitkeeps(base_path: Path | str = ".") -> None:
    base = Path(base_path)
    for rel in FOLDERS:
        folder = base / rel
        folder.mkdir(parents=True, exist_ok=True)
        keep_path = folder / ".gitkeep"
        keep_path.touch(exist_ok=True)
        logger.info(".gitkeep ensured: %s", keep_path)


if __name__ == "__main__":
    add_gitkeeps()
