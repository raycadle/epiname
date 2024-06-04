#!/usr/bin/python

import os
import sys
import argparse
import subprocess
import wikipedia
import requests
from bs4 import BeautifulSoup
from pathlib import Path

def check_file(file: str) -> bool:
    validFile: bool = False
    if Path(file).is_file():
        validFile = True

    return validFile

def check_dir(directory: str) -> bool:
    validDir: bool = False
    if Path(directory).is_dir():
        validDir = True

    return validDir

def find_by_ext(directory: str, ext: list[str]) -> list[str]:
    filePaths: list[str] = []
    path = Path(directory)
    for p in sorted(path.rglob('*')):
        file = Path(p)
        if file.is_file():
            if file.suffix in ext:
                filePaths.append(file)

    return filePaths

def print_new_names(fileNames: list[str], episodeTitles: list[str]) -> None:
    for file, title in zip(fileNames, episodeTitles):
        f = Path(file)
        name, ext = f.stem, f.suffix
        newName: str = f"{name} - {title}{ext}"
        print(f"Output: {newName}")

    return None

def rename_files(fileNames: list[str], episodeTitles: list[str]) -> None:
    for file, title in zip(fileNames, episodeTitles):
        f = Path(file)
        name, ext = f.stem, f.suffix
        newName: str = f"{name} - {title}{ext}"
        f.rename(Path(f.parent, newName))

    return None

def prep_rename(fileNames: list[str], episodeTitles: list[str], yesCommit: bool, dryRun: bool) -> None:
    # Append episode titles to the files
    if len(fileNames) == len(episodeTitles):
        print(f"Renaming {len(fileNames)} files...")
        if yesCommit:
            if dryRun:
                print_new_names(fileNames, episodeTitles)
                print(f"Dry run complete!")
            else:
                rename_files(fileNames, episodeTitles)
                print(f"All files renamed!")
        else:
            print_new_names(fileNames, episodeTitles)
            confirmed: str = input("Are these changes okay? (y|n): ")
            if confirmed == "n":
                print(f"Pending changes cancelled. Exiting...")
            else:
                if dryRun:
                    print(f"Dry run complete!")
                else:
                    rename_files(fileNames, episodeTitles)
                    print(f"All files renamed!")
    else:
        print(f"Error: the number of files ({len(fileNames)}) and titles ({len(episodeTitles)}) do not match!")
        sys.exit(10)

    return None

def get_filenames(workingDir: str) -> list[str]:
    files: list[str] = []
    ext: list[str] = [".mkv", ".mp4"]
    print(f"Searching {workingDir} for media files...")
    files = find_by_ext(workingDir, ext)
    print(f"Found {len(files)} files in {workingDir}.")

    return files

def get_titles(titlesFile: str, editFirst: bool) -> list[str]:
    titles: list[str] = []
    editor = os.environ.get('EDITOR', 'vi')
    if editFirst:
        subprocess.call([editor, titlesFile])
    
    with open(titlesFile, "r") as file:
        for line in file:
            titles.append(line.rstrip())
      
    print(f"Found {len(titles)} titles.")

    return titles

def prompt_dir() -> str:
    while True:
        answer = input("Please enter the directory to search for media files (leave blank to search current directory; q to quit): ")
        if answer == "":
            workingDir = Path.cwd()
            break
        elif answer == "q":
            sys.exit(0)
        else:
            if check_dir(answer):
                workingDir = answer
                break
            else:
                print(f"Error: ${answer} is not a valid directory.")

    return workingDir

def search_show(workingDir: str, showName: str) -> str or None:
    print(f"Searching for information on {showName}...")
    searchQuery: str = f"List of {showName} episodes"
    searchResult = wikipedia.search(searchQuery, results=1)
    if searchResult:
        print(f"Found title information for {showName}.")
        showPage = wikipedia.page(searchResult[0], pageid = None, auto_suggest = False)
        response = requests.get(url=showPage.url)
        soup = BeautifulSoup(response.content, 'html.parser')
        items = soup.find(id="mw-content-text").find_all(class_="summary")
        titlesFile: str = f"{workingDir}/titles.txt"
        with open(titlesFile, "a") as file:
            for item in items:
                print(item.get_text(), file=file)
        
        subprocess.run(['sed', '-i', '/^List of.*episodes$/d;/^Release$/d;s/^"//g;s/".*$//g;s/:/-/g;s/?/_/g', titlesFile])
    else:
        print(f"Error: no results were found for {showName}.")

    return titlesFile if 'titlesFile' in locals() else None

def prompt_titles(workingDir) -> str:
    while True:
        answer = input("Please enter the title file's location or the show's name (leave blank to search current directory; q to quit): ")
        if answer == "":
            currentDir = Path.cwd()
            ext = [".txt"]
            print(f"Searching {currentDir} for text files...")
            result = find_by_ext(currentDir, ext)
            titlesSource = str(result[0])
            if check_file(titlesSource):
                print(f"Found {titlesSource}! Scanning...")
                break
            else:
                print(f"Warning: No text files were found in {currentDir}.")
        elif answer == "q":
            sys.exit(0)
        else:
            if check_file(answer):
                titlesSource = answer
                print(f"Scanning {answer}...")
                break
            elif check_dir(answer):
                ext: list[str] = [".txt"]
                result = find_by_ext(answer, ext)
                titlesSource = str(result[0])
                if check_file(titlesSource):
                    print(f"Found {titlesSource}! Scanning...")
                    break
                else:
                    print(f"Warning: No text files were found in {answer}.")
            else:
                print(f"Warning: {answer} is not a file!")
                titlesSource = search_show(workingDir, answer)
                if titlesSource != None:
                    break

    return titlesSource

def main() -> None:
    # Parse Arguments
    parser = argparse.ArgumentParser(description='Add episode titles to the episode files of a show.')
    parser.add_argument('-e', '--edit', action='store_true', help='edit episode titles before renaming episode files')
    parser.add_argument('-n', '--nochange', action='store_true', help='perform mock-run and print')
    parser.add_argument('-y', '--yes', action='store_true', help='yes to confirm changes')
    parser.add_argument('-d', '--dir', help='directory containing the media files')
    parser.add_argument('-t', '--titles', help='source of episode titles')
    args = parser.parse_args()

    editFirst: bool = False
    dryRun: bool = False
    yesCommit: bool = False

    if len(sys.argv) <= 1:
        workingDir = prompt_dir()
        titlesFile = prompt_titles(workingDir)
        editFirst = True
    else:
        if args.edit:
            editFirst = True

        if args.nochange:
            dryRun = True

        if args.yes:
            yesCommit = True

        if args.dir:
            if check_dir(args.dir):
                workingDir = args.dir
            else:
                print(f"Warning: {args.dir} is not a directory!")
                workingDir = prompt_dir()
        else:
            workingDir = prompt_dir()

        if args.titles:
            if check_file(args.titles):
                titlesFile = args.titles
            else:
                print(f"Warning: {args.titles} is not a file!")
                titlesFile = prompt_titles(workingDir)
        else:
            titlesFile = prompt_titles(workingDir)

    fileNames = get_filenames(workingDir)
    episodeTitles = get_titles(titlesFile, editFirst)
    prep_rename(fileNames, episodeTitles, yesCommit, dryRun)

if __name__ == '__main__':
    main()
