#!/usr/bin/python

import sys
import re
import wikipedia
import requests
from bs4 import BeautifulSoup

showName = sys.argv[1]
outputFile = sys.argv[2]
searchQuery = "List of " + showName + " episodes"
searchResult = wikipedia.search(searchQuery, results=1)

if searchResult:

    showPage = wikipedia.page(searchResult[0], pageid = None, auto_suggest = False)

    response = requests.get(
        url=showPage.url,
    )

    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.find(id="mw-content-text").find_all(class_="summary")
    
    with open(outputFile, "w") as f:
        for item in items:
            print(item.get_text(), file=f)

else :
    sys.exit(1)
