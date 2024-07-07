# Epiname

Easily add episode titles to TV shows.

## Features

- Scan given directory recursively for video files.
- Scan given file for episode titles.
- Search Wikipedia for episode titles if file not given.
- Optionally edit episode titles before committing changes.
- Optionally preview changes before committing.

## Naming Guidelines

All files must be named according to the below guidelines. This keeps all the files alphabetically ordered when renaming.

- Single digit numbers must be padded with leading zeroes, like so: `01.mkv`.
- When renaming multiple seasons, this format is recommended: `S01E01.mkv`.

### Recommended Directory Structure

Media files are expected to be in a directory that may or may not match the name of the show. Subdirectories for seasons and parts are scanned, so their respective files must be named appropriately, i.e. `S01E01.mkv` and `S02E01.mkv`. Having `01.mkv` in both seasons 1 and 2 may cause ordering issues (not verified, YMMV).

The recommended directory structure: `'Anime Name'/'Season 01'/S01E01.mkv`

## Usage

First, let's clone the repo.
```
git clone https://github.com/raycadle/epiname.git
cd epiname
```

Now, let's install dependencies. We can use `pip` to simplify this process. If `pip` is not installed, or you're unsure what it is, see [here](https://pip.pypa.io/en/stable/installation/).

```
pip install -r requirements.txt
```

Finally, we can run the script.
```
python3 epiname.py
```