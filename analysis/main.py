from pathlib import Path

from analyze import analyze
from settings import CLEAN_DATA_FOLDER, RAW_DATA_FOLDER, GRAPHS_DATA_FOLDER
from transform import transform


def main(raw_data: Path, clean_data: Path, graphs_path: Path) -> None:
    file = transform(raw_data, clean_data)
    analyze(file, graphs_path)


if __name__ == "__main__":
    main(RAW_DATA_FOLDER, CLEAN_DATA_FOLDER, GRAPHS_DATA_FOLDER)
