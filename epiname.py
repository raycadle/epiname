#!/usr/bin/python

import os
import sys
import argparse
import tempfile
import subprocess
import wikipedia
import requests
from bs4 import BeautifulSoup
from pathlib import Path

parser = argparse.ArgumentParser(description='Add episode titles to the episode files of a show.')
parser.add_argument('-e', '--edit', action='store_true', help='edit episode titles before renaming episode files')
parser.add_argument('-n', '--nochange', action='store_true', help='print outcome but make no changes to episode files')
parser.add_argument('-d', '--dir', help='directory containing the episode files to be renamed')
parser.add_argument('-f', '--file', help='file containing existing episode titles')
parser.add_argument('show', help='name of the show to search for episode titles of')

args = parser.parse_args()
titles = []
files = []

def get_files():
  if args.dir:
    if Path(args.dir).is_dir():
      workingDir = args.dir
    else:
      print('error:', args.dir, 'is not a directory')
      sys.exit(2)
  else:
    workingDir = Path.cwd()
  
  path = Path(workingDir)
  for path in sorted(path.rglob('*')):
    file = Path(path)
    ext = ['.mkv', '.mp4']
    if file.is_file():
      if file.suffix in ext:
        files.append(file)

def get_titles():
  editor = os.environ.get('EDITOR', 'vi')
  if args.file:
    if Path(args.file).is_file():
      titleFile = args.file
    else:
      print('error:', args.file, 'is not a file')
      sys.exit(2)
  else:
    titleFile = tempfile.NamedTemporaryFile().name
    showName = args.show
    searchQuery = "List of " + showName + " episodes"
    searchResult = wikipedia.search(searchQuery, results=1)
    
    if searchResult:
      showPage = wikipedia.page(searchResult[0], pageid = None, auto_suggest = False)
      response = requests.get(url=showPage.url)
      soup = BeautifulSoup(response.content, 'html.parser')
      items = soup.find(id="mw-content-text").find_all(class_="summary")
      
      with open(titleFile, "w") as file:
        for item in items:
          print(item.get_text(), file=file)
      
      subprocess.run(['sed', '-i', '/^List of.*episodes$/d;/^Release$/d;s/^"//g;s/".*$//g;s/:/-/g;s/\?/_/g', titleFile])
      
  if args.edit == True:
    subprocess.call([editor, titleFile])
    
  with open(titleFile, "r") as file:
    for line in file:
      titles.append(line.rstrip())

def rename_files():
  if len(files) == len(titles):
    for file, title in zip(files, titles):
      f = Path(file)
      name, ext = f.stem, f.suffix
      newName = name + ' - ' + title + ext
      if args.nochange == True:
        print(newName)
      else:
        f.rename(newName)
  else:
    print('error: the number of files (', len(files), ') and titles (', len(titles), ') do not match')
    sys.exit(1)

get_titles()
get_files()
rename_files()