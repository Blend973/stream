# Stream

A command-line tool to search and stream movies and TV shows directly from your terminal using the MPV media player.

## Features

-   Search for movies and TV shows from the command line.
-   Season and episode selection for TV series.
-   Configurable video quality (Best, 1080p, 720p, etc.).
-   Automatic subtitle fetching for the configured language.
-   Autoplay support for binging episodes.
-   Customizable `mpv` player options for a tailored viewing experience.
-   Persistent settings via an automatically generated `stream_config.json` file.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

1.  **Python 3**: The script is written in Python 3.
2.  **MPV Player**: A free, open-source, and cross-platform media player. You must install it and ensure it's available in your system's PATH.
    -   **macOS (via [Homebrew](https://brew.sh/)):** `brew install mpv`
    -   **Debian/Ubuntu:** `sudo apt-get install mpv`
    -   **Arch Linux:** `sudo pacman -S mpv`
    -   **Windows (via [Chocolatey](https://chocolatey.org/)):** `choco install mpv`

## Installation

1.  **Download the script**:
    ```bash
    curl -o yt-browser.py https://raw.githubusercontent.com/Blend973/stream/main/stream.py
    ```

2.  **Install Python Dependencies**
    Open your terminal and install the required Python libraries using pip:
    ```bash
    pip install requests beautifulsoup4
    ```
    or using pipx,
    ```bash
    pipx install requests beautifulsoup4
    ```
    or you can use package manager of your Distro.

3.  **Make the Script Executable (for Linux/macOS)**
    Navigate to the script's directory and run:
    ```bash
    chmod +x stream.py
    ```
3.  **Move it to your PATH**:
    Move the script to a directory in your system's `PATH` to make it accessible from anywhere. A common choice is `/usr/local/bin`.
    ```bash
    sudo mv stream.py /usr/local/bin/stream
    ```
## Usage Instructions

1.  **Run the script from your terminal:**
    ```bash
    stream
    ```
    On Windows, you might run it using:
    ```bash
    python stream.py
    ```
    On the first run, a `stream_config.json` file will be created in the same directory with default settings.

2.  **Search for Media:**
    When prompted, type a movie or TV show title and press Enter.
    ```
    Search/Command ('s' settings, 'q' quit): The Mandalorian
    ```

3.  **Select from Results:**
    The script will display a list of search results. Enter the number corresponding to your choice.
    ```
    Select Media:
      1. The Mandalorian (TV) [2019]
      2. The Mandalorian (Movie) [2023]
    Number > 1
    ```

4.  **Select Season and Episode (for TV shows):**
    If you selected a TV show, you will be prompted to choose a season and then a starting episode.

5.  **Enjoy the Stream:**
    The selected media will automatically start playing in a new `mpv` window.

### In-App Commands

-   `s` or `settings`: Enter the settings menu to configure the script.
-   `q` or `quit`: Exit the application.
-   `b` or `back`: Go back from a selection menu.

## Configuration

The script's behavior can be customized via the `stream_config.json` file or the in-app `settings` menu.

| Setting       | Description                                                                          | Default Value     | Options                               |
|---------------|--------------------------------------------------------------------------------------|-------------------|---------------------------------------|
| `base_url`    | The base URL of the streaming source website.                                        | `https://flixhq.to` | Any compatible URL                    |
| `provider`    | The preferred streaming provider.                                                    | `Vidcloud`        | `Vidcloud`, `UpCloud`                 |
| `quality`     | The desired video quality. The script selects the best stream up to this limit.      | `Best`            | `Best`, `1080`, `720`, `480`, `360`     |
| `sub_language`| The preferred language for subtitles.                                                | `english`         | e.g., `spanish`, `french`, `german`   |
| `autoplay`    | Toggles automatically playing the next episode.                                      | `false`           | `true`, `false`                       |
| `mpv_options` | Command-line arguments to pass to `mpv` (e.g., `--fs` for fullscreen).               | `--fs --force-window=immediate` | Any valid `mpv` flags |

## Disclaimer

This script is provided for educational purposes only. The user is solely responsible for ensuring that they comply with all applicable copyright laws in their region. The developers of this script assume no responsibility for its misuse.
