def convert_key_to_camelot(key):
    """Convert musical key to Camelot Wheel code"""
    key_to_camelot = {
        "C": "8B",
        "C#": "3B",
        "Db": "3B",
        "D": "10B",
        "D#": "5B",
        "Eb": "5B",
        "E": "12B",
        "F": "7B",
        "F#": "2B",
        "Gb": "2B",
        "G": "9B",
        "G#": "4B",
        "Ab": "4B",
        "A": "11B",
        "A#": "6B",
        "Bb": "6B",
        "B": "1B",
        "Cb": "1B",
        "Cm": "5A",
        "C#m": "12A",
        "Dbm": "12A",
        "Dm": "7A",
        "D#m": "2A",
        "Ebm": "2A",
        "Em": "9A",
        "Fm": "4A",
        "F#m": "11A",
        "Gbm": "11A",
        "Gm": "6A",
        "G#m": "1A",
        "Abm": "1A",
        "Am": "8A",
        "A#m": "3A",
        "Bbm": "3A",
        "Bm": "10A",
        "Cbm": "10A",
    }
    return key_to_camelot.get(key, "0A")


def camelot_to_key(camelot_key):
    """Convert Camelot Wheel code to musical key"""
    camelot_to_key_map = {
        "8B": "C",
        "3B": "C#",
        "10B": "D",
        "5B": "D#",
        "12B": "E",
        "7B": "F",
        "2B": "F#",
        "9B": "G",
        "4B": "G#",
        "11B": "A",
        "6B": "A#",
        "1B": "B",
        "5A": "Cm",
        "12A": "C#m",
        "7A": "Dm",
        "2A": "D#m",
        "9A": "Em",
        "4A": "Fm",
        "11A": "F#m",
        "6A": "Gm",
        "1A": "G#m",
        "8A": "Am",
        "3A": "A#m",
        "10A": "Bm",
    }
    return camelot_to_key_map.get(camelot_key, "Unknown Key")


def adjust_bpm(bpm):
    """Adjust the BPM value from the database if needed"""
    return bpm / 100 if bpm > 1000 else bpm


match_camelot_wheel = {
    "1A": ["1A", "2A", "12A", "12B"],
    "2A": ["2A", "1A", "3A", "1B"],
    "3A": ["3A", "2A", "4A", "2B"],
    "4A": ["4A", "3A", "5A", "3B"],
    "5A": ["5A", "4A", "6A", "4B"],
    "6A": ["6A", "5A", "7A", "5B"],
    "7A": ["7A", "6A", "8A", "6B"],
    "8A": ["8A", "7A", "9A", "7B"],
    "9A": ["9A", "8A", "10A", "8B"],
    "10A": ["10A", "9A", "11A", "9B"],
    "11A": ["11A", "10A", "12A", "10B"],
    "12A": ["12A", "11A", "1A", "11B"],
    "1B": ["1B", "2B", "12B", "12A"],
    "2B": ["2B", "1B", "3B", "1A"],
    "3B": ["3B", "2B", "4B", "2A"],
    "4B": ["4B", "3B", "5B", "3A"],
    "5B": ["5B", "4B", "6B", "4A"],
    "6B": ["6B", "5B", "7B", "5A"],
    "7B": ["7B", "6B", "8B", "6A"],
    "8B": ["8B", "7B", "9B", "7A"],
    "9B": ["9B", "8B", "10B", "8A"],
    "10B": ["10B", "9B", "11B", "9A"],
    "11B": ["11B", "10B", "12B", "10A"],
    "12B": ["12B", "11B", "1B", "11A"],
}
