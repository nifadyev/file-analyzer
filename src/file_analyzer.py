#  -*- coding: utf-8 -*-
import requests
import re
from bs4 import BeautifulSoup


class FileAnalyzer:
    """ """

    _response_body = None
    _markup_information = None
    _useful_information = None

    def __init__(self, uri):
        self.uri = uri
        # self.request = requests.get(uri)

    def _scrape(self):
        self._response_body = requests.get(self.uri).text

        self._markup_information = re.findall(
            r'<+/?.*?>+', self._response_body)

        #  Write only useful text to file
        soup = BeautifulSoup(self._response_body, "html.parser")
        # Use this for counting most frequent tag (use Counter)
        # print([tag.name for tag in soup.find_all()])

        # kill all script and style elements
        for script in soup(["script", "style"]):
            script.extract()    # rip it out

        # get text
        # text = soup.get_text()
        self._useful_information = soup.get_text(separator=' ')
        # text = soup.body.get_text(separator= ' ')

        # break into lines and remove leading and trailing space on each
        lines = (line.strip()
                 for line in self._useful_information.splitlines())
        # break multi-headlines into a line each
        chunks = (phrase.strip()
                  for line in lines for phrase in line.split("  "))
        # drop blank lines
        self._useful_information = '\n'.join(
            chunk for chunk in chunks if chunk)

    @property
    def markup_information_symbols(self):
        return sum((len(line) for line in self._markup_information))

    # @property
    # def markup_information_words(self):

    @property
    def useful_information_symbols(self):
        return sum((len(line) for line in self._useful_information))

    @property
    def useful_information_words(self):
        return len(self._useful_information.split(' '))

    @property
    def useful_info_to_markup_info_ratio(self):
        return self.useful_information_symbols / self.markup_information_symbols

    def write_response(self, response, output_file):
        """ """

        with open(output_file, 'w+', encoding="utf-8") as output:
            # str_list = list(filter(None, request.text))
            # for line in request.text.split('\n'):
                # Only 1 line, need another solution
                # output.write(line or '')
            # output.write(request.text.replace('\n', ''))
            output.write(response.replace('\t', '    '))

    def write_useful_information(self, output_file_path):
        with open(output_file_path, 'w+', encoding='utf-8') as output:
            output.write(self._useful_information)

    def write_markup_information(self, output_file_path):
        with open(output_file_path, 'w+') as output:
            for string in self._markup_information:
                output.write(string+'\n')

    # TODO: read about properties
    # @property
    def get_total_symbols_amount(self):
        return sum((len(line) for line in self.request.text))

    # @property
    # def get_uri(self):
    #     return self.uri + 'sdfsd'


a = FileAnalyzer('http://www.unn.ru/')
print(a.get_uri)

#  Write only tags, their attributes and scripts to file
# TODO: add meaming of regular expresion


# HTML file features (or characteristics)
# print('Number of chars (markup information):', tags_and_attributes_chars)
# # print('Number of tags (markup information):', )
# print('Number of chars (displayed information):', useful_text_chars)
# print('Number of words (displayed information):', words_useful_info)
# print('Displayed information to markup information ratio:',
#       f'{useful_info_to_markup_info_ratio:.2f}')
