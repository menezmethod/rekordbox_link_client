import logging
import threading
from utils.rekordbox_utils import open_rekordbox
from deck_manager import process_deck_info

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def main():
    open_rekordbox()

    # Create events for synchronization
    deck1_event = threading.Event()
    deck2_event = threading.Event()

    # Initialize threads with the correct arguments
    deck1_thread = threading.Thread(
        target=process_deck_info, args=(1, 2, deck1_event, deck2_event)
    )
    deck2_thread = threading.Thread(
        target=process_deck_info, args=(2, 1, deck2_event, deck1_event)
    )

    deck1_thread.start()
    deck2_thread.start()

    deck1_thread.join()
    deck2_thread.join()


if __name__ == "__main__":
    main()
