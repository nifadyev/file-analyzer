#  -*- coding: utf-8 -*-
import re
import argparse
import requests
from bs4 import BeautifulSoup
import json

# TODO: выполнить выборку из например 1000 сайтов и файлов, сравнить, мб построить графики
# Привести общую инфу по форматам и сравнить их харки
# !!! TODO: WRITE TESTS USING PYTEST
# TODO: get rid of too many if else
# TODO: adaptate either functions or parsing useful json info to 1 standard

class FileAnalyzer:
    """Analyze markup files and show their various characteristics."""

    # This fields are the same to class
    _response_body = None
    _markup_information = None
    _useful_information = None
    _script = None
    _style = None
    # _url = False
    _soup = None

    def __init__(self, args):
        # This one are unique to each class entity
        self.arguments = self._parse_arguments(args)
        self.uri = self.arguments.file_path
        
        self.is_html = False
        self.is_xml = False
        self.is_json = False
        # ? Maybe do this that way
        # self.response = None

        # TODO: move this if else to separate function
        # Very simple check for whether uri is url or path to file
        # ! Will fail if file is in '.htm' format
        if self.uri.endswith('.html')\
                and not self.uri.startswith('http')\
                and not self.uri.startswith('www'):

            self.is_html = True
            self.is_xml = False
            self.is_json = False

            with open(self.uri, 'r') as html:
                self._response_body = html.read()
        # ! Fill fail if filename starts with these prefixes
        elif self.uri.startswith('http') or self.uri.startswith('www'):
            # TODO: decode response (get rid of such shit - &#1055;)

            self.is_html = True
            self.is_xml = False
            self.is_json = False

            self._response_body = requests.get(
                self.uri,
                headers={'Content-Type': 'text/html;charset=UTF-8'}
            ).text

        elif self.uri.endswith('.xml')\
                and not self.uri.startswith('http')\
                and not self.uri.startswith('www'):

            self.is_html = False
            self.is_xml = True
            self.is_json = False

            with open(self.uri) as xml:
                self._response_body = xml.read()
        elif self.uri.startswith('http') or self.uri.startswith('www'):

            self.is_html = False
            self.is_xml = True
            self.is_json = False

            self._response_body = requests.get(
                self.uri,
                headers={'Content-Type': 'text/xml;charset=UTF-8'}
            ).text

        elif self.uri.endswith('.json')\
                and not self.uri.startswith('http')\
                and not self.uri.startswith('www'):

            self.is_html = False
            self.is_xml = False
            self.is_json = True

            with open(self.uri) as json:
                self._response_body = json.read()
        elif self.uri.startswith('http') or self.uri.startswith('www'):

            self.is_html = False
            self.is_xml = False
            self.is_json = True

            self._response_body = requests.get(
                self.uri,
                headers={'Content-Type': 'text/json;charset=UTF-8'}
            ).text

        if self.is_html:
            self._html_scrape()
            self.is_html = False
        elif self.is_xml:
            self._xml_scrape()
        elif self.is_json:
            self._json_scrape()

        self.write_response('results/response.html')
        self.write_markup_information('results/tags.txt')
        self.write_useful_information('results/useful_info.txt')
        # self.request = requests.get(uri)


    def _xml_scrape(self):
        self._markup_information = re.findall(
            r'<+/?.*?>+',  # TODO: add meaning of regular expression
            self._response_body
        )

        #  Write only useful text to file
        # ! Pronably invalid. Check how to extract info from xml
        # soup = BeautifulSoup(self._response_body, "xml.parser")
        soup = BeautifulSoup(self._response_body, "html.parser")
        self._soup = soup

        # get text
        # text = soup.get_text()
        # ? Why separator is being used
        self._useful_information = soup.get_text(separator=' ')

        # break into lines and remove leading and trailing space on each
        lines = (line.strip()
                for line in self._useful_information.splitlines())
        # break multi-headlines into a line each
        # ? For what
        chunks = (phrase.strip()
                for line in lines for phrase in line.split("  "))
        # drop blank lines
        self._useful_information = '\n'.join(
            chunk for chunk in chunks if chunk)

    def _get_keys_and_values_json(self, json, destination):
        for key, value in json.items():
            destination.append(key)
            if isinstance(value, dict):
                self._get_keys_and_values_json(value, destination)
            else:
                destination.append(value)

    def _json_scrape(self):
        print(self._response_body)
        # ! Doesnt handle such values^ {ip}
        self._markup_information = re.findall(
            r'["|:|{|}|\[|\]]',  # TODO: add meaning of regular expression
            self._response_body
        )
        # print(self._markup_information)
        # def get_keys(dl, keys_list):
        #     if isinstance(dl, dict):
        #         keys_list += dl.keys()
        #         map(lambda x: get_keys(x, keys_list), dl.values())
        #     elif isinstance(dl, list):
        #         map(lambda x: get_keys(x, keys_list), dl)

        # keys = []
        # get_keys(jdata, keys)
        parsed_json = json.loads(self._response_body)
        self._useful_information = []

        self._get_keys_and_values_json(parsed_json, self._useful_information)
        # self._useful_information.extend(parsed_json.keys())
        # self._useful_information.extend(parsed_json.values())
        print(self._useful_information)

    def _html_scrape(self):
        # ! Example of scraping xml tags is presented in regex cheatsheet
        self._markup_information = re.findall(
            r'<+/?.*?>+',  # TODO: add meaning of regular expression
            self._response_body
        )

        #  Write only useful text to file
        soup = BeautifulSoup(self._response_body, "html.parser")
        self._soup = soup
        # Use this for counting most frequent tag (use Counter)
        # print([tag.name for tag in soup.find_all()])

        # quiet straight forward solution, change in future
        script_with_empty_strings = [
            line.strip() for line in soup.find('script').text.splitlines() if line
        ]
        self._script = [line for line in script_with_empty_strings if line]
        # print(self._script)

        style_with_empty_strings = [
            line.strip() for line in soup.find('style').text.splitlines() if line
        ]
        self._style = [line for line in style_with_empty_strings if line]
        # print(self._style)
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()

        # get text
        # text = soup.get_text()
        # ? Why separator is being used
        self._useful_information = soup.get_text(separator=' ')

        # break into lines and remove leading and trailing space on each
        lines = (line.strip()
                for line in self._useful_information.splitlines())
        # break multi-headlines into a line each
        # ? For what
        chunks = (phrase.strip()
                for line in lines for phrase in line.split("  "))
        # drop blank lines
        # self._useful_information = '\n'.join(
        #     chunk for chunk in chunks if chunk)
        self._useful_information = tuple(line for line in chunks if line)

    def validate_file_path(self, file_path):
        """Check file path for validity."""

        # TODO: regex for check if file_path is valid url
        # if url:
        #     _url = True
        # TODO: or valid path to file

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
        # argument_parser.add_argument(
        #     "-v", "--verbose", help="verbose output about errors",
        #     action='store_true'
        # )

        return argument_parser.parse_args(args)

    @property
    def markup_information_symbols(self):
        return sum((len(line) for line in self._markup_information))

    @property
    def markup_information_words(self):
        # ? How to count attr values if they are grouped using comma
        # ? Also how to get rid of '=' cause its not wrapped with spaces

        # length = 0
        # for tag in self._markup_information:
        #     print(tag.split(), len(tag.split()))
        #     tags_and_attrs = tag.split()
        #     if len(tags_and_attrs) == 1:
        #         length += len(tags_and_attrs)
        #     else:
        #         length += sum(sum(len(w) for w in word.split('=')) for word in tags_and_attrs)
            # length += len(tag.split().split('='))

        # Count both opening and closing tags WITHOUT attributes
        return len(self._markup_information)
        # return length

    @property
    def markup_information_script(self):
        """Count amount of JS code in chars (without tabs)."""

        return sum(len(line) for line in self._script)

    @property
    def markup_information_style(self):
        """Count amount of CSS styles in chars."""

        return sum(len(line) for line in self._style)

    @property
    def useful_information_symbols(self):
        """Count amount of useful (displayed to user) information in chars."""

        # Remove '\n' from total number of markup symbols
        # Last string doesn't have trailing '\n'
        # return len(self._useful_information)\
        #     - len(self._useful_information.splitlines())\
        #     + 1
        return sum(len(line) for line in self._useful_information)


    @property
    def useful_information_words(self):
        """Count amount of useful (displayed to user) information in words."""
        # FIXME: cannot count words if there are more than 1 space
        # TODO: remove this wrapping spaces while scraping

        # FIXME: dont count words correctly because last word in Title wont count
        # ! Thats why use hardcoded +1 length
        # return len(self._useful_information.split(' '))\
        #     + 1
        print(self._useful_information)
        return sum(len(line.split(' ')) for line in self._useful_information)

    @property
    def useful_info_to_markup_info_ratio(self):
        """Count ratio of displayed information to markup information."""

        return self.useful_information_symbols / self.markup_information_symbols

    def write_response(self, output_file):
        """Write response to file.

        Arguments:
            output_file {str} -- path to output file.
        """
        # TODO: may differ for json
        with open(output_file, 'w+', encoding="utf-8") as output:
            # str_list = list(filter(None, request.text))
            # for line in request.text.split('\n'):
                    # Only 1 line, need another solution
                    # output.write(line or '')
            # output.write(request.text.replace('\n', ''))
            # output.write(self._response_body.replace('\t', '    '))
            # output.write(self._soup.prettify())
            output.write(self._soup.prettify().replace('&amp;', '&'))

    def write_useful_information(self, output_file_path):
        """Write us useful information to file.

        Arguments:
            output_file {str} -- path to output file.
        """
        with open(output_file_path, 'w+', encoding='utf-8') as output:
            # output.write(self._useful_information)
            for line in self._useful_information:
                output.write(line + '\n')

    def write_markup_information(self, output_file_path):
        """Write markup information to file.

        Arguments:
            output_file {str} -- path to output file.
        """
        with open(output_file_path, 'w+') as output:
            for string in self._markup_information:
                output.write(string+'\n')

    @property
    def total_symbols_number(self):
        return len(self._response_body)

    # @property
    # def get_uri(self):
    #     return self.uri + 'sdfsd'


# a = FileAnalyzer('http://www.unn.ru/')
# print(a.get_uri)
