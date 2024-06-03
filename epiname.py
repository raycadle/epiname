#!/usr/bin/python

# To Do
# feat: prompt for confirm before rename, skip with -y, --noprompt  
# impr: store titles in cache when failure

# Library Import
import os
import sys
import argparse
import tempfile
import subprocess
import wikipedia
import requests
from bs4 import BeautifulSoup
from pathlib import Path

def check_file(file):
    if Path(file).is_file():
        validFile = True
    else:
        validFile = False
    return validFile

def check_dir(directory):
    if Path(directory).is_dir():
        validDir = True
    else:
        validDir = False
    return validDir

def rename_files(filenames, episodeTitles, dryrun):
    # Append episode titles to the files
    if len(filenames) == len(episodeTitles):
        for file, title in zip(filenames, episodeTitles):
            f = Path(file)
            name, ext = f.stem, f.suffix
            newName = name + ' - ' + title + ext
            if dryrun:
                print(f"New filename: {newName}")
            elif not dryrun:
                f.rename(Path(f.parent, newName))
        print(f"All files renamed!")
    else:
        print(f"Error: the number of files ({len(filenames)}) and titles ({len(episodeTitles)}) do not match!")
        sys.exit(10)

def get_filenames(workingDir):
    files = []
    ext = ['.mkv', '.mp4']
    print(f"Searching {workingDir} for media files...")
    # Get a list of files to rename
    path = Path(workingDir)
    for p in sorted(path.rglob('*')):
      file = Path(p)
      if file.is_file():
        if file.suffix in ext:
          files.append(file)

    print(f"Found {len(files)} files in {workingDir}.")
    return files

def get_titles(titlesFile, editFirst):
    titles = []
    # Get a list of episode titles
    editor = os.environ.get('EDITOR', 'vi')
    if editFirst:
        subprocess.call([editor, titlesFile])
    
    with open(titlesFile, "r") as file:
        for line in file:
            titles.append(line.rstrip())
      
    print(f"Found {len(titles)} titles.")
    return titles

def prompt_dir():
    while True:
        answer = input("Please enter the directory to search for media files (leave blank to search current directory): ")
        if answer == "":
            workingDir = Path.cwd()
            break
        else:
            if check_dir(answer):
                workingDir = answer
                break
            else:
                print(f"Error: ${answer} is not a valid directory.")

    return workingDir

def search_show(showName):
    print(f"Searching for {showName}...")
    searchQuery = "List of " + showName + " episodes"
    searchResult = wikipedia.search(searchQuery, results=1)
    if searchResult:
        print(f"Found title information for {showName}.")
        showPage = wikipedia.page(searchResult[0], pageid = None, auto_suggest = False)
        response = requests.get(url=showPage.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find(id="mw-content-text").find_all(class_="summary")
        tempFile = tempfile.NamedTemporaryFile().name
        with open(tempFile, "w") as file:
            for item in items:
                print(item.get_text(), file=file)
        
        subprocess.run(['sed', '-i', '/^List of.*episodes$/d;/^Release$/d;s/^"//g;s/".*$//g;s/:/-/g;s/?/_/g', tempFile])
    else:
        print(f"Error: no results were found for {showName}.")

    return tempFile if 'tempFile' in locals() else None

def prompt_titles():
    while True:
        answer = input("Please enter the title file's location or the show's name (leave blank to search current directory): ")
        if answer == "":
            workingDir = Path.cwd()
            print(f"Searching {workingDir} for text files...")
            path = Path(workingDir)
            for p in sorted(path.rglob('*')):
                file = Path(p)
                if file.is_file():
                    if file.suffix == ".txt":
                        print(f"Found {file}! Scanning...")
                        titlesSource = file
                        break
            break
        else:
            if check_file(answer):
                titlesSource = answer
                break
            else:
                print(f"Error: {answer} is not a valid file!")
                titlesSource = search_show(answer)
                if titleSource != None:
                    break

    return titlesSource

def main():
    # Parse Arguments
    parser = argparse.ArgumentParser(description='Add episode titles to the episode files of a show.')
    parser.add_argument('-e', '--edit', action='store_true', help='edit episode titles before renaming episode files')
    parser.add_argument('-n', '--nochange', action='store_true', help='perform mock-run and print')
    parser.add_argument('-q', '--quiet', action='store_true', help='show no output')
    parser.add_argument('-d', '--dir', help='directory containing the media files')
    parser.add_argument('-t', '--titles', help='source of episode titles')
    args = parser.parse_args()

    if len(sys.argv) <= 1:
        workingDir = prompt_dir()
        filenames = get_filenames(workingDir)
        titlesFile = prompt_titles()
        episodeTitles = get_titles(titlesFile, True)
        rename_files(filenames, episodeTitles, True)
    else:
        if args.dir:
            if check_dir(args.dir):
                workingDir = args.dir
            else:
                print(f"Error: {args.dir} is not a directory!")
                workingDir = prompt_dir()
        else:
            workingDir = prompt_dir()

        filenames = get_filenames(workingDir)
        
        if args.titles:
            if check_file(args.titles):
                titlesFile = args.titles
            else:
                print(f"Error: {args.titles} is not a directory!")
                titlesFile = prompt_titles()
        else:
            titlesFile = prompt_titles()

        if args.edit:
            episodeTitles = get_titles(titlesFile, True)
        else:
            episodeTitles = get_titles(titlesFile, False)

        if args.nochange:
            rename_files(filenames, episodeTitles, True)
        else:
            rename_files(filenames, episodeTitles, False)

if __name__ == '__main__':
    main()
