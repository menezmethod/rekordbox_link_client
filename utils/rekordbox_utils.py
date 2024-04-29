import os
import time
import pygetwindow as gw
import logging
from config.settings import REKORDBOX_PATH


def open_rekordbox():
    if not any("rekordbox" in win.lower() for win in gw.getAllTitles()):
        logging.info("Launching Rekordbox...")
        os.system(f'open "{REKORDBOX_PATH}"')
        time.sleep(10)
    else:
        logging.info("Rekordbox is already running.")
