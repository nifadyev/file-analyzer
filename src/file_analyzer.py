#  -*- coding: utf-8 -*-
import re
import argparse
import json
import requests
from bs4 import BeautifulSoup
from collections import Counter

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
        self._most_common_tag = None

        # ? Maybe do this that way
        # self.response = None

        file_format, is_local = self.define_file_format(self.arguments.file_path)

        if is_local:
            with open(self.arguments.file_path, 'r') as input_file:
                self._response_body = input_file.read()
        else:
            self._response_body = requests.get(
                self.arguments.file_path,
                headers={
                    'Content-Type': f'text/{file_format};charset=UTF-8'
                }
            ).text

        print(self._response_body)
        self._scrape(file_format)
        self._write(file_format)

    # Might be better to do it classmethod
    # @classmethod
    def define_file_format(self, file_path):
        """ """
        # Very simple check for whether uri is url or path to file
        # ! Will fail if file is in '.htm' format
        if file_path.endswith('.html')\
                and not file_path.startswith('http')\
                and not file_path.startswith('www'):

            file_format = 'html'
            is_local = True
        # ! Fill fail if filename starts with these prefixes
        elif file_path.startswith('http') or file_path.startswith('www'):
            # TODO: decode response (get rid of such shit - &#1055;)

            file_format = 'html'
            is_local = False
        elif file_path.endswith('.xml')\
                and not file_path.startswith('http')\
                and not file_path.startswith('www'):

            file_format = 'xml'
            is_local = True
        elif file_path.startswith('http') or file_path.startswith('www'):
            file_format = 'html'
            is_local = False
        elif file_path.endswith('.json')\
                and not file_path.startswith('http')\
                and not file_path.startswith('www'):

            file_format = 'json'
            is_local = True
        elif file_path.startswith('http') or file_path.startswith('www'):
            file_format = 'json'
            is_local = False

        return file_format, is_local

    def _scrape(self, file_format):
        """ """
        if file_format == 'html':
            self._html_scrape()
        elif file_format == 'xml':
            self._xml_scrape()
        elif file_format == 'json':
            self._json_scrape()

    def _write(self, file_format):
        """ """

        self.write_response(f'results/response.{file_format}')
        self.write_markup_information(f'results/tags.{file_format}')
        self.write_useful_information('results/useful_info.txt')

    def _xml_scrape(self):
        self._markup_information = re.findall(
            r'<+/?.*?>+',  # TODO: add meaning of regular expression
            self._response_body
        )

        #  Write only useful text to file
        # ! Pronably invalid. Check how to extract info from xml
        # soup = BeautifulSoup(self._response_body, "xml.parser")
        # ! Need lxml to parse XML
        soup = BeautifulSoup(self._response_body, "html.parser")
        self._soup = soup

        tags = Counter((tag.name for tag in soup.find_all()))
        # Get first tuple from most common tags list
        # And tag name from tuple
        self._most_common_tag = tags.most_common(1)[0][0]

        # ? Why separator is being used
        self._useful_information = soup.get_text(separator=' ')

        # break into lines and remove leading and trailing space on each
        lines = (
            line.strip() for line in self._useful_information.splitlines()
        )
        # break multi-headlines into a line each
        # ? For what
        chunks = (
            phrase.strip() for line in lines for phrase in line.split("  ")
        )
        # drop blank lines
        self._useful_information = '\n'.join(
            chunk for chunk in chunks if chunk)

    def _get_keys_and_values_json(self, input_json_file, destination):
        for key, value in input_json_file.items():
            destination.append(key)
            if isinstance(value, dict):
                self._get_keys_and_values_json(value, destination)
            else:
                destination.append(value)

    def _json_scrape(self):
        # ! Doesnt handle such values^ {ip}
        self._markup_information = re.findall(
            r'["|:|{|}|\[|\]]',  # TODO: add meaning of regular expression
            self._response_body
        )

        parsed_json = json.loads(self._response_body)
        self._useful_information = []

        # self._get_keys_and_values_json(parsed_json, self._useful_information:=[])
        self._get_keys_and_values_json(parsed_json, self._useful_information)

    def _html_scrape(self):
        #  Write only useful text to file
        soup = BeautifulSoup(self._response_body, "html.parser")
        self._soup = soup

        # ! Read about it
        tags = Counter((tag.name for tag in soup.find_all()))
        # Get first tuple from most common tags list
        # And tag name from tuple
        self._most_common_tag = tags.most_common(1)[0][0]

        # quiet straight forward solution, change in future
        # ! script tags may be more than one
        scripts = soup.find_all('script')
        if scripts:
            self._script = []
            for script in scripts:
                # ! str(line).strip() need to remove empty strings
                self._script.extend(line + '\n' for line in script.text.splitlines() if str(line).strip())
                # self._script.extend(line for line in script.text.splitlines() if str(line))
                self._script[-1] = re.sub('\n', '', self._script[-1])
            print(self._script)
        # if soup.find('script'):
            # self._script = [line for line in soup.find('script').text.splitlines() if str(line).strip()]
            # print(self._script)

        # ! style tags may be more than one
        if soup.find('style'):
            self._style = [line for line in soup.find('style').text.splitlines() if str(line).strip()]
            # print(self._style)
        # Remove script and style elements
        for extra in soup(["script", "style"]):
            extra.extract()

        # ? Why separator is being used
        # self._useful_information = soup.get_text(separator=' ')

        # Break into lines, remove leading and trailing space on each
        # And get rid of blank lines
        self._useful_information = tuple(
            line.strip() for line in soup.get_text().splitlines() if line
        )
        # for line in lines:
        #     print(line)
        # Split each line into separate words
        # ! Should we split by " " or by "  "
        # self._useful_information = tuple(
        #     phrase.strip() for line in lines for phrase in line.split()
        # )
        # drop blank lines
        # self._useful_information = '\n'.join(
        #     chunk for chunk in chunks if chunk)
        # self._useful_information = tuple(line for line in chunks)

        response_body_copy = self._response_body
        # response_body_copy = self._soup.prettify(formatter=None)
        for line in self._useful_information:
            response_body_copy = re.sub(line, '', response_body_copy)
        self._markup_information = response_body_copy
        print(self._markup_information)
        # print(response_body_copy)
        # print(self._useful_information)

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
        print(self._markup_information)
        return sum((len(line) for line in self._markup_information))

    @property
    def markup_information_words(self):
        # TODO: Rename func to markup_information_tags
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
        # return len([line for line in self._markup_information.splitlines() if line.lstrip()])

        # ! Propably wont find inline tags
        return len(re.findall(
                # ! (?#comment) in regex
                # Opening tags with leading tabs or spaces
                r'<[^/?][^>]+>',
                self._response_body
            )
        )

    @property
    def markup_information_script(self):
        """Count amount of JS code in chars."""

        # Also count '\n' symbols
        # return sum(len(line) for line in self._script) + len(self._script) - 1
        return sum(len(line) for line in self._script)

    @property
    def markup_information_style(self):
        """Count amount of CSS styles in chars."""

        # Also count '\n' symbols
        return sum(len(line) for line in self._style) + len(self._style) - 1

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
        # Split each line into separate words
        # ! Check for empty linesREGEX
        words = tuple(
            phrase.strip() for line in self._useful_information for phrase in line.split()
        )

        return len(words)

    @property
    def useful_info_to_markup_info_ratio(self):
        """Count ratio of displayed information to markup information."""

        # return self.useful_information_symbols / self.markup_information_symbols
        return self.useful_information_symbols / (self.total_symbols_number - self.useful_information_symbols)

    @property
    def most_common_tag(self):
        """ """
        return self._most_common_tag

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
            # output.write(self._soup.prettify().replace('&amp;', '&'))
            # r = re.compile(r'^(\s*)', re.MULTILINE)
            # def prettify_2space(s, encoding=None, formatter="minimal"):
            #     return r.sub(r'\1\1', s.prettify(encoding, formatter))
        # print(soup.decode(pretty_print=True))
            # output.writelines(self._response_body)
            # output.writelines(prettify_2space(self._soup))
            output.write(self._response_body)
            # output.write(self._soup.prettify(formatter=None))

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
