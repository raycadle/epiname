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

def print_output(newNames: list[str]) -> None:
    for name in newNames:
        print(f"Output: {name}")

    return None

def rename_files(files: list[str], newNames: list[str]) -> None:
    for file, newName in zip(files, newNames):
        f = Path(file)
        f.rename(Path(f.parent, newName))

    return None

def prep_rename(files: list[str], newNames: list[str], assumeYes: bool, dryRun: bool) -> None:
    # Append episode titles to the files
    if len(files) == len(newNames):
        print(f"Renaming {len(files)} files...")
        if dryRun:
            print_output(newNames)
            print(f"Dry run complete!")
            sys.exit(0)

        if assumeYes:
            rename_files(files, newNames)
            print(f"All files renamed!")
        else:
            print_output(newNames)
            confirmed: str = input("Are these changes okay? (y|n): ")
            if confirmed == "n":
                print(f"Changes cancelled. Exiting...")
            else:
                rename_files(files, newNames)
                print(f"All files renamed!")
    else:
        print(f"Error: the number of files ({len(files)}) and titles ({len(newNames)}) do not match!")
        sys.exit(10)

    return None

def prep_names(files: list[str], titles: list[str]) -> list[str]:
    newNames: list[str] = []
    for file, title in zip(fileNames, titles):
        f = Path(file)
        name, ext = f.stem, f.suffix
        newName: str = f"{name} - {title}{ext}"
        newNames.append(newName)

    return newNames

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

def get_files(workingDir: str) -> list[str]:
    files: list[str] = []
    ext: list[str] = [".mkv", ".mp4"]
    print(f"Searching {workingDir} for media files...")
    files = find_by_ext(workingDir, ext)
    print(f"Found {len(files)} files in {workingDir}.")

    return files

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

def find_titles_file(workingDir: str) -> str or None:
    ext: list[str] = [".txt"]
    result = find_by_ext(workingDir, ext)
    file = str(result[0])
    if check_file(file):
        titlesFile = file
        print(f"Found {titlesFile}! Scanning...")
    else:
        print(f"Warning: No text files were found in {workingDir}.")

    return titlesFile if 'titlesFile' in locals() else None

def prompt_titles(workingDir: str) -> str:
    while True:
        answer = input("Please enter the title file's location or the show's name (leave blank to search current directory; q to quit): ")
        if answer == "":
            print(f"Searching {workingDir} for text files...")
            titlesSource = find_titles_file(workingDir)
            if titlesSource != None:
                break
        elif answer == "q":
            sys.exit(0)
        else:
            if check_file(answer):
                titlesSource = answer
                print(f"Scanning {answer}...")
                if titlesSource != None:
                    break
            elif check_dir(answer):
                titlesSource = find_titles_file(workingDir)
                if titlesSource != None:
                    break
            else:
                print(f"Warning: {answer} is not a file!")
                titlesSource = search_show(workingDir, answer)
                if titlesSource != None:
                    break

    return titlesSource

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

def get_info(answerDir: str, answerTitles: str) -> str:
    if answerDir:
        if check_dir(answerDir):
            workingDir = answerDir
        else:
            print(f"Warning: {answerDir} is not a directory!")
            workingDir = prompt_dir()
    else:
        workingDir = prompt_dir()

    if answerTitles:
        if check_file(answerTitles):
            titlesFile = answerTitles
        elif check_dir(answerTitles):
            result = find_titles_file(answerTitles)
            if result != None:
                titlesFile = result
            else:
                print(f"Warning: no titles file was found at {answerTitles}")
                titlesFile = prompt_titles(workingDir)
        else:
            print(f"Warning: {answerTitles} is not a file!")
            result = search_show(workingDir, answerTitles)
            if result != None:
                titlesFile = result
            else:
                print(f"Warning: no show info was found for {answerTitles}")
                titlesFile = prompt_titles(workingDir)
    else:
        result = find_titles_file(workingDir)
        if result != None:
            titlesFile = result
        else:
            print(f"Warning: no titles file was found at {workingDir}")
            titlesFile = prompt_titles(workingDir)

    return workingDir, titlesFile

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
    assumeYes: bool = False

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
            assumeYes = True

        workingDir, titlesFile = get_info(args.dir, args.titles)

    files = get_files(workingDir)
    titles = get_titles(titlesFile, editFirst)
    newNames = prep_names(files, titles)
    prep_rename(files, newNames, assumeYes, dryRun)

if __name__ == '__main__':
    main()
