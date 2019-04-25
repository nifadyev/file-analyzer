#  -*- coding: utf-8 -*-
import requests
import re
from bs4 import BeautifulSoup
import argparse


class FileAnalyzer:
    """Analyze markup files and show their various characteristics."""

    _response_body = None
    _markup_information = None
    _useful_information = None
    _url = False
    _soup = None

    def __init__(self, args):
        self.arguments = self._parse_arguments(args)
        self.uri = self.arguments.file_path
        self._scrape()
        self.write_response('results/response.html')
        self.write_markup_information('results/tags.txt')
        self.write_useful_information('results/useful_info.txt')

    def _scrape(self):
        self._response_body = requests.get(
            self.uri, headers={'Content-Type': 'text/html;charset=UTF-8'}).text

        self._markup_information = re.findall(
            r'<+/?.*?>+', self._response_body
        )

        #  Write only useful text to file
        soup = BeautifulSoup(self._response_body, "html.parser")
        self._soup = soup

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        self._useful_information = soup.get_text(separator=' ')

        # Break into lines and remove leading and trailing space on each
        lines = (line.strip()
                 for line in self._useful_information.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip()
                  for line in lines for phrase in line.split("  "))
        # Drop blank lines
        self._useful_information = '\n'.join(
            chunk for chunk in chunks if chunk)

    def validate_file_path(self, file_path):
        """ """

        return file_path

    def _parse_arguments(self, args):
        """Handle command line arguments using argparse.

        Arguments:
            args {list} -- command line arguments.

        Raises:
            argparse.ArgumentTypeError -- invalid argument type.

        Returns:
            argparse.Namespace -- parsed arguments of valid type.
        """

        argument_parser = argparse.ArgumentParser(
            description="Markup file analyzer")

        argument_parser.add_argument(
            "file_path", help="path to local file or URL", type=self.validate_file_path
        )

        return argument_parser.parse_args(args)

    @property
    def markup_information_symbols(self):
        return sum((len(line) for line in self._markup_information))

    @property
    def useful_information_symbols(self):
        return sum((len(line) for line in self._useful_information))

    @property
    def useful_information_words(self):
        return len(self._useful_information.split(' '))

    @property
    def useful_info_to_markup_info_ratio(self):
        return self.useful_information_symbols / self.markup_information_symbols

    def write_response(self, output_file):
        """ """

        with open(output_file, 'w+', encoding="utf-8") as output:
            output.write(self._soup.prettify().replace('&amp;', '&'))

    def write_useful_information(self, output_file_path):
        with open(output_file_path, 'w+', encoding='utf-8') as output:
            output.write(self._useful_information)

    def write_markup_information(self, output_file_path):
        with open(output_file_path, 'w+') as output:
            for string in self._markup_information:
                output.write(string+'\n')

    def get_total_symbols_amount(self):
        return sum((len(line) for line in self.request.text))
