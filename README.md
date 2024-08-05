# Upload Helper

Welcome to Upload Helper! This tool is designed to simplify media uploading tasks by automating several processes. It might not be perfect, but it aims to make your life easier.

> [!NOTE]
> This project is a fork of an existing repository, which I have customized and maintained according to my specific needs. While it retains core functionality from the original project, there may be slight variations to better suit my use cases. You are welcome to use this fork as you see fit.

## Features
  - **Media Information:** Generates and parses MediaInfo/BDInfo.
  - **Screenshots:** Generates and uploads screenshots.
  - **Filename Correction:** Uses srrdb to fix scene filenames.
  - **Descriptions:** Retrieves descriptions from PTP (automatically on filename match or via argument) / BLU (via argument).
  - **Identifiers:** Obtains TMDb/IMDb/MAL identifiers.
  - **Anime Season/Episode Numbering:** Converts absolute to season and episode numbering for anime.
  - **Custom Torrents:** Generates custom .torrents without unnecessary top-level folders or .nfo files.
  - **Reuse Torrents:** Reuses existing torrents instead of creating new ones.
  - **Naming:** Generates appropriate names for your uploads using MediaInfo/BDInfo and TMDb/IMDb, conforming to site rules.
  - **Duplicate Check:** Checks for existing releases on the site.
  - **Queuing:** Supports manual or automated queuing.
  - **Client Integration:** Adds to your client with fast resume, seeding instantly (compatible with rtorrent/qbittorrent/deluge/watch folder).
  - **Minimal Input Required:** Operates with minimal user input.
  - **File Formats:** Currently supports .mkv, .mp4, Blu-ray, DVD, HD-DVDs (or any format with --full-directory applied).

## Supported Sites

<details>

<summary>Click Here For Sites List</summary>

| Site  |
|-------|
| ACM   |
| AITHER|
| ANT   |
| BHDTV |
| BLU   |
| FL    |
| FNP   |
| HDB   |
| HDT   |
| HUNO  |
| JPTV  |
| LCD   |
| LDU   |
| LST   |
| LT    |
| MB    |
| MTV   |
| NBL   |
| OE    |
| OINK  |
| OTW   |
| PTER  |
| PTT   |
| R4E   |
| RF    |
| RTF   |
| SN    |
| STC   |
| TDC   |
| TL    |
| TTG   |
| TTR   |
| ULCX  |
| UTP   |
| VHD   |

</details>

> [!TIP]
> To ensure proper functionality with Upload Helper, please use the exact site names as listed here. For instance, "Aither" should be referred to as "AITHER" rather than "ATH". This requirement applies to all sites listed, so please verify that you are using the correct name.

## Upcoming Features
  - Enhanced support for FANRES & Adult Content.
  - Improved support for Music & Ebooks.

## Setup
1) **Prerequisites:**
   - Python 3.7 or higher, with pip3.
     - For Python 3.7, install qbittorrent-api==2023.9.53 or a compatible version.
   - [Mono](https://www.mono-project.com/) is required on Linux systems for BDInfo.
   - MediaInfo and ffmpeg must be installed.
2) **Installation:**
   - **Windows:** Add ffmpeg to PATH. Use [Scoop](https://scoop.sh/) for easy installation or follow this [manual guide](https://windowsloop.com/install-ffmpeg-windows-10/).
   - **Linux:** Install ffmpeg via your package manager.
   - **MacOS:** Install ffmpeg using Homebrew or place static builds in `/usr/bin` or `$HOME/.local/bin`. Update PATH in `$HOME/.zshrc` with `export PATH="$PATH:$HOME/.local/bin"`.
3) **Clone the Repository:**
     ```
     git clone https://github.com/RegEdits-TSC/Uploader-Helper.git
     ```
4) **Configure:**
   - Copy and rename `data/backup/example-config.py` to `data/config.py`.
   - Edit `config.py` with your information. Detailed instructions are available in the [wiki](https://github.com/L4GSP1KE/Upload-Assistant/wiki).
     - Obtain a TMDb API (v3) key from [TMDb](https://developer.themoviedb.org/docs/getting-started).
     - Acquire image host API keys from their respective sites.
   - Install necessary Python modules:
     ```
     pip3 install --user -U -r requirements.txt
     ```    
   
## Updating
To update your installation:
1) Navigate to the Uploader-Helper directory:
   ```
   cd Uploader-Helper
   ```
2) Pull the latest changes:
   ```
   git pull
   ```
3) Update Python dependencies:
   ```
   python3 -m pip install --user -U -r requirements.txt
   ```

## CLI Usage

Run the tool using:
```
python3 upload.py "/path/to/media" --args
```
Example: 
```
python3 upload.py "/home/regedits/torrents/qbittorrent/uploads/Avengers.Age.of.Ultron.2015.2160p.DSNP.WEB-DL.DDP5.1.Atmos.DV.HDR.H.265-RegEdits.mkv" --args -tk AITHER -ns -pr -d [code]This release is sourced from DisneyPlus[/code] -s 5 -c movie -tmdb 99861 -edition hybrid -webdv
```

Arguments are optional. For a list of acceptable arguments, use `--help`. For an overview of arguments with descriptions, navigate to the `arguments.txt` file in the main directory.

## Docker Usage
Special thanks to __l1mo__ for the Dockerfile setup and __dare__ for the command. Run the tool using Docker with one of the following commands:
```
docker run --rm -it --network=host \
-v /path/to/config.py:/Uploadrr/data/config.py \
-v /path/to/media:/media \
-v /path/to/BT_backup:/BT_backup \
ghcr.io/z-ink/uploadrr:master "/path/to/media" --args
```
__OR__
```
docker run --rm -it --network=host -v /path/to/config.py:/Uploadrr/data/config.py -v /path/to/media:/media -v /path/to/BT_backup:/BT_backup ghcr.io/z-ink/uploadrr:master "/path/to/media" --args
```
