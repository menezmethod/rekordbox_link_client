# Rekordbox Link Client

The Rekordbox Link Client is a Python script that automates the process of finding and selecting similar tracks in Rekordbox based on the currently playing track on each deck. It utilizes optical character recognition (OCR) to extract track information from the Rekordbox user interface and interacts with the Rekordbox database to find compatible tracks.

## Features

- Automatically detects the currently playing track on each deck
- Retrieves track information (title, artist, BPM, key, duration, genre) from the Rekordbox database
- Finds similar tracks based on BPM, key compatibility, and genre
- Selects the most suitable track for the other deck when the current track is nearing its end
- Provides logging and error handling for smooth operation

## Prerequisites

- Python 3.x
- Rekordbox 6 or later

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/menezmethod/rekordbox-link-client.git
   ```

2. Navigate to the project directory:
   ```
   cd rekordbox-link-client
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Configuration

1. Open the  file and update the following variables:
   - : Set the path to the folder where screenshots will be saved.
   - : Set the path to the Rekordbox application.

2. Ensure that Rekordbox is properly installed and configured on your system.

## Usage

1. Make sure Rekordbox is running and the desired tracks are loaded into the decks.

2. Run the script:
   ```
   python main.py
   ```

3. The script will automatically detect the currently playing tracks on each deck and find similar tracks to play next.

4. The selected tracks will be logged in the console output.

## Folder Structure

- : Contains configuration settings
- : Manages database connections
- : Handles image processing and OCR
- : Contains utility functions for file handling, Rekordbox, and music-related operations
- : Contains the main functionality of the application, including track management, deck management, and the main entry point

## Contributing

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).

## Disclaimer

This script is provided as-is and may not be suitable for all setups or use cases. Use it at your own risk. Make sure to test it thoroughly before using it in a live performance setting.

