from collections import Counter
import re
import argparse
import json
import requests
from bs4 import BeautifulSoup


class FileAnalyzer:
    """Analyze markup files and show their various characteristics."""

    _response_body = None
    _markup_information = None
    _useful_information = None
    _script = None
    _style = None
    _soup = None

    def __init__(self, args):
        self.arguments = self._parse_arguments(args)
        self._most_common_tag = None

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

        self._scrape(file_format)
        self._write(file_format)

    @staticmethod
    def define_file_format(file_path):
        """Return file format and flag if file is local."""
        # Very simple check for whether uri is url or path to file
        # ! Will fail if file is in '.htm' format
        if (
                file_path.endswith('.html')
                and not file_path.startswith('http')
                and not file_path.startswith('www')
        ):
            file_format = 'html'
            is_local = True

        # ! Fill fail if filename starts with these prefixes
        elif file_path.startswith('http') or file_path.startswith('www'):
            # TODO: decode response (get rid of such shit - &#1055;)
            file_format = 'html'
            is_local = False
        elif (
                file_path.endswith('.xml')
                and not file_path.startswith('http')
                and not file_path.startswith('www')
        ):
            file_format = 'xml'
            is_local = True
        elif file_path.startswith('http') or file_path.startswith('www'):
            file_format = 'html'
            is_local = False
        elif (
                file_path.endswith('.json')
                and not file_path.startswith('http')
                and not file_path.startswith('www')
        ):
            file_format = 'json'
            is_local = True
        elif file_path.startswith('http') or file_path.startswith('www'):
            file_format = 'json'
            is_local = False

        return file_format, is_local

    def _scrape(self, file_format):
        if file_format == 'html':
            self._html_scrape()
        elif file_format == 'xml':
            self._xml_scrape()
        elif file_format == 'json':
            self._json_scrape()

    def _write(self, file_format):
        self.write_response(f'results/response.{file_format}')
        self.write_markup_information(f'results/tags.{file_format}')
        self.write_useful_information('results/useful_info.txt')

    def _xml_scrape(self):
        self._markup_information = re.findall(r'<+/?.*?>+', self._response_body)

        #  Write only useful text to file
        # ! Pronably invalid. Check how to extract info from xml
        # soup = BeautifulSoup(self._response_body, "xml.parser")
        # ! Need lxml to parse XML
        soup = BeautifulSoup(self._response_body, 'html.parser')
        self._soup = soup

        tags = Counter((tag.name for tag in soup.find_all()))
        # Get first tuple from most common tags list
        # And tag name from tuple
        self._most_common_tag = tags.most_common(1)[0][0]

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
        if isinstance(input_json_file, list):
            # ! HARDCODE, fix it
            if input_json_file:
                if isinstance(input_json_file[0], dict):
                    for value in input_json_file:
                        self._get_keys_and_values_json(value, destination)
                else:
                    destination.extend(str(value) for value in input_json_file)
        else:
            for key, value in input_json_file.items():
                destination.append(key)
                if isinstance(value, list):
                    self._get_keys_and_values_json(value, destination)
                elif isinstance(value, dict):
                    self._get_keys_and_values_json(value, destination)
                else:
                    destination.append(str(value))

    def _json_scrape(self):
        # ! Doesnt handle such values^ {ip}
        # ! Doesn't count /t and spaces
        self._markup_information = re.findall(
            # TODO: add meaning of regular expression
            r'(\t{1,}|^\s{4,}|"|:|{|}|\[|\]|\,)',
            self._response_body
        )

        spaces = 0
        for char in self._response_body:
            if char == ' ':
                spaces += 1
        self._markup_information.extend(' ' * spaces)

        parsed_json = json.loads(self._response_body)
        self._useful_information = []

        self._get_keys_and_values_json(parsed_json, self._useful_information)

    def _html_scrape(self):
        #  Write only useful text to file
        soup = BeautifulSoup(self._response_body, "html.parser")
        self._soup = soup

        tags = Counter((tag.name for tag in soup.find_all()))
        # Get first tuple from most common tags list
        # And tag name from tuple
        self._most_common_tag = tags.most_common(1)[0][0]
        # quiet straight forward solution, change in future
        scripts = soup.find_all('script')
        if scripts:
            self._script = []
            for script in scripts:
                # ! str(line).strip() need to remove empty strings
                self._script.extend(
                    line + '\n' for line in script.text.splitlines() if str(line).strip())
                if self._script:
                    self._script[-1] = re.sub('\n', '', self._script[-1])

        styles = soup.find_all('style')
        if styles:
            self._style = []
            for style in styles:
                # ! str(line).strip() need to remove empty strings
                self._style.extend(
                    line + '\n' for line in style.text.splitlines() if str(line).strip())
                # self._style[-1] = re.sub('\n', '', self._style[-1])

        # Remove script and style elements
        for extra in soup(["script", "style"]):
            extra.extract()

        # Break into lines, remove leading and trailing space on each
        # And get rid of blank lines
        self._useful_information = tuple(
            line.strip() for line in soup.get_text().splitlines() if line
        )

        response_body_copy = self._response_body
        for line in self._useful_information:
            response_body_copy = re.sub(line, '\1', response_body_copy)
        self._markup_information = response_body_copy

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

        argument_parser.add_argument('file_path', help='path to local file or URL')

        return argument_parser.parse_args(args)

    @property
    def markup_information_symbols(self):
        return sum((len(line) for line in self._markup_information))

    @property
    def markup_information_words(self):
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
        return sum(len(line) for line in self._script)

    @property
    def markup_information_style(self):
        """Count amount of CSS styles in chars."""
        # Also count '\n' symbols
        return sum(len(line) for line in self._style) + len(self._style) - 1

    @property
    def useful_information_symbols(self):
        """Count amount of useful (displayed to user) information in chars."""
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
        return self.useful_information_symbols / (self.total_symbols_number - self.useful_information_symbols)

    @property
    def most_common_tag(self):
        return self._most_common_tag

    def write_response(self, output_file):
        """Write response to file.

        Arguments:
            output_file {str} -- path to output file.
        """
        with open(output_file, 'w+', encoding="utf-8") as output:
            output.write(self._response_body)

    def write_useful_information(self, output_file_path):
        """Write us useful information to file.

        Arguments:
            output_file {str} -- path to output file.
        """
        with open(output_file_path, 'w+', encoding='utf-8') as output:
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

    def collect_data(self, output_file_path):
        with open(output_file_path, 'a') as output_file:
            output_file.write(
                f'{self.total_symbols_number} '
                + f'{self.markup_information_symbols} '
                + f'{self.markup_information_words} '
                + f'{self.useful_information_symbols} '
                + f'{self.useful_information_words} '
                + f'{self.useful_info_to_markup_info_ratio:.2f}\n'
            )
