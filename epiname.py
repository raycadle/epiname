#!/usr/bin/python

# To Do
# major rewrite: fork bulky.py and add function to title files (from existing file or search show), with syntax specification from user, position (basically the current insert function of bulky.py adapted to titling show episodes)
# feat: group seasons, if appli.
# feat: specify naming format
# feat: interactive when no args
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

def pars_args():
  # Parse Arguments
  parser = argparse.ArgumentParser(description='Add episode titles to the episode files of a show.')
  parser.add_argument('-e', '--edit', action='store_true', help='edit episode titles before renaming episode files')
  parser.add_argument('-n', '--nochange', action='store_true', help='perform mock-run and print')
  parser.add_argument('-d', '--dir', help='directory containing the media files')
  parser.add_argument('-f', '--file', help='file containing titles')
  parser.add_argument('-s', '--show', help='name of the show to search for')
  args = parser.parse_args()

def get_files():
  # Get a list of files to rename
  if args.dir:
    if Path(args.dir).is_dir():
      workingDir = args.dir
    else:
      print('error:', args.dir, 'is not a directory')
      sys.exit(20)
  else:
    workingDir = Path.cwd()
  
  path = Path(workingDir)
  print('searching for media files in', workingDir)
  for p in sorted(path.rglob('*')):
    file = Path(p)
    ext = ['.mkv', '.mp4']
    if file.is_file():
      if file.suffix in ext:
        files.append(file)
  print('found', len(files), 'files in', workingDir)

def get_titles():
  # Get a list of episode titles
  showName = args.show
  if args.file:
    if Path(args.file).is_file():
      titleFile = args.file
    else:
      print('error:', args.file, 'is not a file')
      sys.exit(30)
  else:
    titleFile = tempfile.NamedTemporaryFile().name
    print('searching for', showName)
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
      
    else:
      print('error: no results were found for ', showName)
      sys.exit(40)
  
  editor = os.environ.get('EDITOR', 'vi')
  if args.edit == True:
    subprocess.call([editor, titleFile])
    
  with open(titleFile, "r") as file:
    for line in file:
      titles.append(line.rstrip())
      
  print('found', len(titles), 'titles for', showName)

def rename_files():
  # Append episode titles to the files
  if len(files) == len(titles):
    for file, title in zip(files, titles):
      f = Path(file)
      name, ext = f.stem, f.suffix
      newName = name + ' - ' + title + ext
      if args.nochange == True:
        print(newName)
      else:
        print('renaming', len(files), 'files')
        f.rename(Path(f.parent, newName))
  else:
    print('error: the number of files (', len(files), ') and titles (', len(titles), ') do not match')
    sys.exit(10)

def main():
  files = []
  titles = []

  if not len(sys.argv) > 1:
    # prompt for dir
    get_files()
    # prompt for title file
    get_titles()
    # prompt for show name
    get_show()
  else:
    pars_args()
    get_files()
    get_titles()
    
  rename_files()

main()
