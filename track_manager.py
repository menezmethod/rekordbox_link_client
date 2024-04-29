import logging

from database.db_manager import managed_database_connection
from utils.music_utils import (
    convert_key_to_camelot,
    camelot_to_key,
    adjust_bpm,
    match_camelot_wheel,
)
from pyrekordbox.db6 import DjmdContent


def get_track_info_from_db(track_name, db):
    content = db.session.query(DjmdContent).filter(DjmdContent.Title.like(f"{track_name}%")).first()
    if content:
        genre_name = "Unknown Genre"
        if content.Genre:
            genre_name = content.Genre.Name

        return {
            "ID": content.ID,
            "title": content.Title,
            "artist": content.Artist.Name if content.Artist else "Unknown Artist",
            "bpm": adjust_bpm(content.BPM),
            "key": convert_key_to_camelot(
                content.Key.ScaleName if content.Key else "Unknown Key"
            ),
            "duration": content.Length,
            "genre": genre_name,
        }
    else:
        return {
            "title": track_name,
            "artist": "Unknown Artist",
            "bpm": 0,
            "key": "Unknown Key",
            "duration": 0,
            "genre": "Unknown Genre",
        }


def get_related_tracks_from_db(
        track_info_db,
        db,
        current_track_id=None,
        other_deck_track_id=None,
        initial_bpm_tolerance=0,
        expanded_bpm_tolerances=[5, 10],
        key_match=True,
):
    def query_related_tracks(bpm_tolerance, current_track_id_related, other_deck_track_id_related):
        query = db.get_content()
        min_bpm = track_info_db["bpm"] - bpm_tolerance
        max_bpm = track_info_db["bpm"] + bpm_tolerance
        query = query.filter(DjmdContent.BPM.between(min_bpm * 100, max_bpm * 100))

        if key_match and track_info_db["key"]:
            traditional_key = camelot_to_key(track_info_db["key"])
            key_id = db.get_key(ScaleName=traditional_key).first()
            if key_id:
                query = query.filter(DjmdContent.KeyID == key_id.ID)

        # Exclude the currently playing track and the track on the other deck
        if current_track_id_related:
            query = query.filter(DjmdContent.ID != current_track_id_related)
        if other_deck_track_id_related:
            query = query.filter(DjmdContent.ID != other_deck_track_id_related)
        return query.all()

    # Start with the initial BPM tolerance
    related_tracks_db = query_related_tracks(
        initial_bpm_tolerance, current_track_id, other_deck_track_id
    )
    if related_tracks_db:
        logging.info(
            f"Found {len(related_tracks_db)} related tracks with BPM tolerance of {initial_bpm_tolerance}."
        )
        related_tracks_info = [
            get_track_info_from_db(track.Title, db) for track in related_tracks_db
        ]
        return related_tracks_info

    # If no tracks found, expand the BPM tolerance
    for tolerance in expanded_bpm_tolerances:
        related_tracks_db = query_related_tracks(
            tolerance, current_track_id, other_deck_track_id
        )
        if related_tracks_db:
            logging.info(
                f"Found {len(related_tracks_db)} related tracks with expanded BPM tolerance of {tolerance}."
            )
            related_tracks_info = [
                get_track_info_from_db(track.Title, db) for track in related_tracks_db
            ]
            return related_tracks_info

    logging.warning("No related tracks found with any of the specified BPM tolerances.")
    return []


def find_similar_track(track_list, current_track_info, current_track_clean=True):
    if not current_track_info:
        logging.warning("No current track info provided for finding similar tracks.")
        return None

    logging.info(
        f"Attempting to find similar {'clean' if current_track_clean else 'clean or dirty'} track for BPM: {current_track_info['bpm']}, Key: {current_track_info['key']}, Genre: {current_track_info['genre']}"
    )
    harmonically_compatible_keys = match_camelot_wheel.get(current_track_info["key"], [])
    logging.debug(
        f"Harmonically compatible keys for {current_track_info['key']}: {harmonically_compatible_keys}"
    )

    def filter_tracks(bpm_tolerance, strict_genre=True):
        bpm = current_track_info["bpm"]
        # Define BPM variations
        bpm_variations = [
            (bpm, strict_genre),
            (bpm * 0.5, strict_genre),
            (bpm * 2, strict_genre),
        ]  # (BPM value, strict_genre_flag)

        filtered_tracks = [
            track
            for track in track_list
            if track
               and any(
                bpm_variation - bpm_tolerance
                <= track.get("bpm", 0)
                <= bpm_variation + bpm_tolerance
                and (
                        (track.get("genre") == current_track_info.get("genre")
                         if strict_genre_flag
                         else True)
                        and (
                                (("clean" in track.get("title").lower()) == current_track_clean)
                                or not current_track_clean
                        )
                )
                for bpm_variation, strict_genre_flag in bpm_variations
            )
               and track.get("key") in harmonically_compatible_keys
               and track.get("ID") != current_track_info.get("ID")
        ]
        logging.info(
            f"Checked {len(track_list)} tracks, found {len(filtered_tracks)} with BPM tolerance {bpm_tolerance}, "
            f"harmonic compatibility, and genre considerations."
        )
        return filtered_tracks

    # First pass: strict genre adherence
    similar_tracks = filter_tracks(0, True)
    if not similar_tracks:
        logging.info(
            "No tracks found with zero BPM tolerance within same genre, expanding BPM tolerance to 5 within "
            "same genre."
        )
        similar_tracks = filter_tracks(5, True)

    # Second pass: if no suitable tracks found, relax genre condition
    if not similar_tracks:
        logging.info(
            "No tracks found within the same genre, searching across all genres."
        )
        similar_tracks = filter_tracks(0, False)
        if not similar_tracks:
            logging.info(
                "No tracks found with zero BPM tolerance across genres, expanding BPM tolerance to 5 across "
                "genres."
            )
            similar_tracks = filter_tracks(5, False)

    if similar_tracks:
        # Sorting to choose the best match, prefer exact BPM match first
        similar_tracks.sort(
            key=lambda x: (
                min(
                    abs(x["bpm"] - bpm_variation)
                    for bpm_variation, _ in [
                        (current_track_info["bpm"], True),
                        (current_track_info["bpm"] * 0.5, True),
                        (current_track_info["bpm"] * 2, True),
                    ]
                ),
                -harmonically_compatible_keys.index(x["key"]),
            )
        )
        selected_track = similar_tracks[0]
        logging.info(
            f"Selected track: {selected_track['title']} with BPM: {selected_track['bpm']} and Key: {selected_track['key']}, Genre: {selected_track['genre']}"
        )
        return selected_track
    else:
        logging.warning(
            f"No similar track found for BPM: {current_track_info['bpm']}, Key: {current_track_info['key']}, "
            f"Genre: {current_track_info['genre']} after all attempts."
        )
        return None


def select_track_for_deck(deck_number, current_track_info):
    if not current_track_info:
        logging.warning(
            f"No track info available for deck {deck_number}. Skipping track selection."
        )
        return None

    with managed_database_connection() as dbt:
        related_tracks_select = get_related_tracks_from_db(current_track_info, dbt)
        if related_tracks_select:
            selected_track = find_similar_track(
                related_tracks_select, current_track_info
            )
            if selected_track:
                logging.info(f"Selected track for deck {deck_number}: {selected_track}")
                return selected_track
            else:
                logging.warning(f"No similar track found for deck {deck_number}")
        else:
            logging.warning(
                f"No related tracks found in database for deck {deck_number}"
            )

    return None
