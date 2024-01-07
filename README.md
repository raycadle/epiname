# Epiname

Title your TV episodes with little effort.

## Features:
- Scan directories and sub-directories for video files.
- Search Wikipedia for episode titles.
- Edit episode titles before committing changes.
- Preview changes before committing.

## Dependencies:
- os
- argparse
- tempfile
- subprocess
- wikipedia
- requests
- bs4/BeautifulSoup
- pathlib/Path

## Requirements:
- Files must be named properly to have the script move through the files lexographically to match the timeline of the show.

### Filename Format
Shows must be in a directory and can be broken into sub-directories to separate seasons and parts.

The recommended filename format is as follows:
`'Anime Name'/'Season 1'/'Part 1'/S01E01.mkv`

## Python Rewrite To-Do
- look for video files only (match file extension)
- (maybe) use show name to add properly formatted show name to front of episode filenames
- proper error reporting
- optimize wikipedia scraping, if possible
- clean up code and help text