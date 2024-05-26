#!/usr/bin/python

# To Do
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

# Parse Arguments
parser = argparse.ArgumentParser(description='Add episode titles to the episode files of a show.')
parser.add_argument('-e', '--edit', action='store_true', help='edit episode titles before renaming episode files')
parser.add_argument('-n', '--nochange', action='store_true', help='perform mock-run and print')
parser.add_argument('-v', '--verbose', action='store_true', help='show all output')
parser.add_argument('-q', '--quiet', action='store_true', help='show no output')
parser.add_argument('-d', '--dir', help='directory containing the media files')
parser.add_argument('-f', '--file', help='file containing titles')
parser.add_argument('-s', '--show', help='name of the show to search for')
args = parser.parse_args()

def get_filenames():
  files = []
  ext = ['.mkv', '.mp4']
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
  print('> searching for media files in', path)
  for p in sorted(path.rglob('*')):
    file = Path(p)
    if file.is_file():
      if file.suffix in ext:
        files.append(file)
  print('> found', len(files), 'files in', workingDir)
  return files

def get_titles():
  titles = []
  # Get a list of episode titles
  if args.file:
    if Path(args.file).is_file():
      titleFile = args.file
    else:
      print('error:', args.file, 'is not a file')
      sys.exit(30)
  else:
    titleFile = tempfile.NamedTemporaryFile().name
    if args.show:
      showName = args.show
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
        
        subprocess.run(['sed', '-i', '/^List of.*episodes$/d;/^Release$/d;s/^"//g;s/".*$//g;s/:/-/g;s/?/_/g', titleFile])
        
      else:
        print('error: no results were found for ', showName)
        sys.exit(40)
    else:
      print('error: must provide show name if no titles file is provided')
      sys.exit(40)
      
  
  editor = os.environ.get('EDITOR', 'vi')
  if args.edit == True:
    subprocess.call([editor, titleFile])
    
  with open(titleFile, "r") as file:
    for line in file:
      titles.append(line.rstrip())
      
  if args.file:
    print('> found', len(titles), 'titles in', args.file)
  elif args.show:
    print('> found', len(titles), 'titles for' + showName)
  return titles

filenames = get_filenames()
episodeTitles = get_titles()

def rename_files():
  # Append episode titles to the files
  if len(filenames) == len(episodeTitles):
    print('> renaming', len(filenames), 'files')
    for file, title in zip(filenames, episodeTitles):
      f = Path(file)
      name, ext = f.stem, f.suffix
      newName = name + ' - ' + title + ext
      if args.verbose == True:
        print('> renaming', f.name, 'to ' + newName + '...')
        if args.nochange == True:
          print('output: ' + newName)
        else:
          f.rename(Path(f.parent, newName))
        print('> done')
      else:
        if args.nochange == True:
          print('output: ' + newName)
        else:
          f.rename(Path(f.parent, newName))
    print('> all files renamed')
  else:
    print('error: the number of files (', len(filenames), ') and titles (', len(episodeTitles), ') do not match')
    sys.exit(10)

def main():
  #if not len(sys.argv) > 1:
    # prompt for dir
    #get_filenames()
    # prompt for title file
    #get_titles()
    # prompt for show name
    #get_show()
  #else:
    #parse_args()
    #get_filenames()
    #get_titles()
    
  rename_files()

main()
