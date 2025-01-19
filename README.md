# SongbookPro Groups Backup

A Python script to backup songs from [SongbookPro Groups](https://songbook-pro.com/groups/) cloud library to local files.

## Background

[SongbookPro](https://songbook-pro.com/) offers a group option called SongbookPro Groups, which provides a shared music library for multiple musicians. However, it lacks a built-in backup functionality to export and save the cloud-hosted song library locally.

This script automates backing up your SongbookPro Groups library by:

-   Logging into your SongbookPro Groups account
-   Iterating through all songs in the library
-   Saving each song in both "Chord over Lyrics" (.crd) and "ChordPro" (.cho) formats

## Prerequisites

-   Python 3.13 or higher
-   A SongbookPro Groups account

## Installation

1. Clone this repository
2. Create a virtual environment and activate it:

```sh
uv sync
```

## Configuration

1. Copy the template environment file:
    ```
    cp .env.tpl .env
    ```
2. Edit `.env` and set your credentials
    ```
    MAIL=your.email@example.com
    PASSWORD=your-password
    EXPORT_PATH=/path/to/backup/folder
    ```

## Usage

Run the backup script:

```
uv run songbookpro-group-backup.py
```

The script will:

1. Launch a headless browser
1. Log into your SongbookPro Groups account
1. Export all songs to the specified export directory
1. Save each song in both formats with filenames like:  
   `Artist - Title.crd` and `Artist - Title.cho`

## Features

-   Automated backup of entire song library
-   Exports in both Chord over Lyrics and ChordPro formats
-   Detects and only updates changed songs
-   Sanitizes filenames for cross-platform compatibility
-   Headless browser operation

## Dependencies

-   Playwright - Browser automation
-   Pydantic - Settings management
-   python-dotenv - Environment variable loading
-   pathvalidate - Filename sanitization
