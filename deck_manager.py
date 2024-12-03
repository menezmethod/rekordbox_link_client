import re
import logging

from database.db_manager import managed_database_connection
from ocr.ocr import capture_and_process_image, perform_ocr
from utils.file_utils import save_image
from track_manager import get_track_info_from_db, select_track_for_deck

regions = {
    "deck1_bpm": (210, 125, 50, 15),
    "deck1_current_bpm": (617, 275, 80, 30),
    "deck1_key": (258, 125, 25, 15),
    "deck1_time_elapsed": (617, 330, 80, 18),
    "deck1_time_remaining": (617, 355, 80, 18),
    "deck1_track_name": (55, 106, 595, 20),
    "deck2_bpm": (1233, 125, 50, 15),
    "deck2_key": (1283, 125, 25, 15),
    "deck2_current_bpm": (1112, 275, 80, 30),
    "deck2_time_elapsed": (1112, 330, 80, 18),
    "deck2_time_remaining": (1112, 355, 80, 18),
    "deck2_track_name": (1080, 106, 595, 20),
    "browser2": (400, 432, 1360, 618),
}


def process_and_save_screenshot(region_key, filename, max_retries=5):
    attempts = 0
    while attempts < max_retries:
        processed_img = capture_and_process_image(regions[region_key])
        save_image(processed_img, filename)
        ocr_text = perform_ocr(processed_img)
        if ocr_text:
            logging.debug(f"OCR output for {region_key}: {ocr_text}")
            return ocr_text
        attempts += 1
        logging.warning(
            f"Empty OCR output for {region_key}. Retrying... Attempt {attempts}"
        )
    logging.error(
        f"Failed to get OCR output for {region_key} after {max_retries} attempts."
    )
    return None


def parse_time(time_str):
    try:
        time_str = re.sub("[^0-9:]", "", time_str)
        minutes, seconds = map(float, time_str.split(":"))
        return minutes * 60 + seconds
    except ValueError:
        logging.error(f"Failed to parse time: {time_str}")
        return None


def process_deck_info(deck_number, other_deck_number, deck_event, other_deck_event):
    previous_track_name = ""
    total_track_duration = None

    with managed_database_connection() as dbt:
        while True:
            track_name = process_and_save_screenshot(
                f"deck{deck_number}_track_name", f"deck{deck_number}_track_name.png"
            )
            time_remaining = process_and_save_screenshot(
                f"deck{deck_number}_time_remaining",
                f"deck{deck_number}_time_remaining.png",
            )
            time_elapsed = process_and_save_screenshot(
                f"deck{deck_number}_time_elapsed", f"deck{deck_number}_time_elapsed.png"
            )

            if track_name != previous_track_name:
                logging.info(f"Track name changed on deck {deck_number}: {track_name}")
                previous_track_name = track_name

                # Fetch track info from database
                track_info = get_track_info_from_db(track_name, dbt)
                if track_info:
                    bpm = track_info["bpm"]
                    key = track_info["key"]
                    genre = track_info["genre"]
                    total_track_duration = track_info["duration"]
                    minutes = (
                            total_track_duration // 60
                    )  # Integer division to get the number of whole minutes
                    seconds = total_track_duration % 60
                    logging.info(
                        f"Retrieved track info from DB for {track_name} on deck {deck_number}: BPM={bpm}, Key={key}, "
                        f"Genre={genre}, Duration={minutes}m {seconds}s"
                    )

                else:
                    logging.warning(
                        f"Track info not found in DB for {track_name}: Falling back to OCR for BPM and Key"
                    )
                    bpm = process_and_save_screenshot(
                        f"deck{deck_number}_bpm", f"deck{deck_number}_bpm.png"
                    )
                    key = process_and_save_screenshot(
                        f"deck{deck_number}_key", f"deck{deck_number}_key.png"
                    )
                    # Here you may want to set a default duration or attempt another method to retrieve it

            elapsed_time = parse_time(time_elapsed) if time_elapsed else None
            remaining_time = parse_time(time_remaining) if time_remaining else None

            if (
                    track_name
                    and elapsed_time is not None
                    and remaining_time is not None
                    and total_track_duration is not None
            ):
                current_total_time = elapsed_time + remaining_time
                if (
                        abs(total_track_duration - current_total_time) > 2
                ):  # Minor variance allowed
                    logging.debug(
                        f"Time mismatch detected on deck {deck_number}: Expected {total_track_duration}, "
                        f"got {current_total_time}"
                    )

            if time_remaining and re.search(r"-00:[0-3]\d", time_remaining):
                logging.info(
                    f"Track nearing end on deck {deck_number}. Time remaining: {time_remaining}"
                )
                if track_info:
                    similar_track = select_track_for_deck(other_deck_number, track_info)
                    if similar_track:
                        logging.info(
                            f"Similar track found for deck {other_deck_number}: {similar_track}"
                        )
                    else:
                        logging.warning(
                            f"No similar track found for deck {other_deck_number}"
                        )
