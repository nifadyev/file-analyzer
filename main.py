#  -*- coding: utf-8 -*-
import requests
import re
from bs4 import BeautifulSoup

request = requests.get('http://www.unn.ru/')

#  Write response body to file
with open('response.txt', 'w+', encoding="utf-8") as output:
    # str_list = list(filter(None, request.text))
    # for line in request.text.split('\n'):
        # Only 1 line, need another solution
        # output.write(line or '')
    # output.write(request.text.replace('\n', ''))
    output.write(request.text.replace('\t', '    '))

total_chars = 0
for line in request.text:
    total_chars += len(line)

print(total_chars)
# tags_and_attributes = re.search('<+\/?.*?>+', request.text)
#  Write only tags, their attributes and scripts to file
# TODO: add meaming of regular expresion
tags_and_attributes = re.findall(r'<+/?.*?>+', request.text)
with open('tags.txt', 'w+') as output:
    for string in tags_and_attributes:
        output.write(string+'\n')

tags_and_attributes_chars = 0
for line in tags_and_attributes:
    tags_and_attributes_chars += len(line)

print(tags_and_attributes_chars)

# print(len([i for i in tags_and_attributes]))
# print(len(tags_and_attributes))
# print(len(request.text))
# print(re.subn('<+\/?.*?>+', '', request.text))
# print(tags_and_attributes)


#  Write only useful text to file
url = "http://news.bbc.co.uk/2/hi/health/2284783.stm"
html = request.text
soup = BeautifulSoup(html, "html.parser")
# Use this for counting most frequent tag (use Counter)
# print([tag.name for tag in soup.find_all()])

# kill all script and style elements
for script in soup(["script", "style"]):
    script.extract()    # rip it out

# get text
# text = soup.get_text()
text = soup.get_text(separator=' ')
# text = soup.body.get_text(separator= ' ')

# break into lines and remove leading and trailing space on each
lines = (line.strip() for line in text.splitlines())
# break multi-headlines into a line each
chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
# drop blank lines
text = '\n'.join(chunk for chunk in chunks if chunk)

useful_text_chars = 0
for line in text:
    useful_text_chars += len(line)

print(useful_text_chars)
print(useful_text_chars + tags_and_attributes_chars)

with open('useful_text.txt', 'w+', encoding="utf-8") as output:
    output.write(text)

# First charactiristic
useful_info_to_markup_info_ratio = useful_text_chars / tags_and_attributes_chars
words_useful_info = len(text.split(' '))

# HTML file features (or characteristics)
print('Number of chars (markup information):', tags_and_attributes_chars)
# print('Number of tags (markup information):', )
print('Number of chars (displayed information):', useful_text_chars)
print('Number of words (displayed information):', words_useful_info)
print('Displayed information to markup information ratio:',
      f'{useful_info_to_markup_info_ratio:.2f}')
