import datetime
from pathlib import Path

import numpy as np
import pandas as pd
import glob
import os


def read_all_csv(path: Path) -> pd.DataFrame:
    csv_files = glob.glob(os.path.join(path, "*.csv"))
    dfs = [pd.read_csv(file) for file in csv_files]
    return pd.concat(dfs, ignore_index=True)


def clean(dt: pd.DataFrame) -> pd.DataFrame:
    dt = dt.drop_duplicates(subset="vacancy_link")
    dt = dt.replace(["n/a", "N/A", None], np.nan)

    exp_map = {"senior": 5, "middle": 3, "junior": 0}

    dt["experience"] = (
        dt["experience"]
        .str.lower()
        .map(exp_map)
        .combine_first(pd.to_numeric(dt["experience"], errors="coerce"))
    )

    dt = dt.dropna(subset=["skills"])

    return dt


def save(dt: pd.DataFrame, path: Path) -> Path:
    os.makedirs(path, exist_ok=True)
    csv_filename = f"vacancies-{datetime.datetime.now():%Y-%m-%d_%H-%M}.csv"
    file_path = path / csv_filename
    dt.to_csv(
        file_path,
        index=False,
    )
    return file_path


def transform(raw_path: Path, clean_path: Path) -> Path:
    dt = read_all_csv(raw_path)
    dt = clean(dt)
    return save(dt, clean_path)
