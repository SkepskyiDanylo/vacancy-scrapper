import configparser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

config = configparser.ConfigParser()
config_path = BASE_DIR / "config.cfg"
config.read(config_path)

RAW_DATA_FOLDER = BASE_DIR / Path(config["global"]["raw_data_folder"])
CLEAN_DATA_FOLDER = BASE_DIR / Path(config["analysis"]["clean_data_folder"])
GRAPHS_DATA_FOLDER = BASE_DIR / Path(config["analysis"]["graphs_folder"])
