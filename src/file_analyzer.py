#  -*- coding: utf-8 -*-
import requests
import re
from bs4 import BeautifulSoup
import argparse

# TODO: count script
# TODO: count css
# TODO: выполнить выборку из например 1000 сайтов и файлов, сравнить, мб построить графики
# Привести общую инфу по форматам и сравнить их харки


class FileAnalyzer:
    """Analyze markup files and show their various characteristics."""

    # This fields are the same to class
    _response_body = None
    _markup_information = None
    _useful_information = None
    _url = False
    _soup = None

    def __init__(self, args):
        # This one are unique to each class entity
        self.arguments = self._parse_arguments(args)
        self.uri = self.arguments.file_path
        self._scrape()
        self.write_response('results/response.html')
        self.write_markup_information('results/tags.txt')
        self.write_useful_information('results/useful_info.txt')
        # self.request = requests.get(uri)

    def _scrape(self):
        # TODO: decode response (get rid of such shit - &#1055;)
        # self._response_body = requests.get(
            # self.uri, headers={'Content-Type': 'text/html;charset=UTF-8'}).text

        with open(self.uri, 'r') as html:
            self._response_body = html.read()

        # print(self._response_body)

        # TODO: add meaning of regular expression
        self._markup_information = re.findall(
            r'<+/?.*?>+', self._response_body
        )

        # print(self._markup_information)

        #  Write only useful text to file
        soup = BeautifulSoup(self._response_body, "html.parser")
        self._soup = soup
        # Use this for counting most frequent tag (use Counter)
        # print([tag.name for tag in soup.find_all()])

        # TODO: this is text of script tag, need to count number of chars in it
        script = soup.find('script')
        # print(script.text)

        # TODO: this is text of script tag, need to count number of chars in it
        style = soup.find('style')
        # print(style.text)
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.extract()

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
        # print(self._useful_information)

    def validate_file_path(self, file_path):
        """ """

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

        # def raise_value_error(err_msg):
        #     raise argparse.ArgumentTypeError(err_msg)

        # argument_parser.error = raise_value_error

        # try:
        #     return argument_parser.parse_args(args)
        # except BaseException:
        #     print(sys.exc_info()[1])
        #     sys.exit()
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
    def useful_information_symbols(self):
        # Remove '\n' from total number of markup symbols
        # Last string doesn't have trailing '\n'
        return len(self._useful_information) - len(self._useful_information.splitlines()) + 1

    @property
    def useful_information_words(self):
        # FIXME: cannot count words if there are more than 1 space
        # FIXME: dont count words correctly because last word in Title wont count
        # ! Thats why use hardcoded +1 length

        return len(self._useful_information.split(' ')) + 1

    @property
    def useful_info_to_markup_info_ratio(self):
        return self.useful_information_symbols / self.markup_information_symbols

    def write_response(self, output_file):
        """ """

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


# a = FileAnalyzer('http://www.unn.ru/')
# print(a.get_uri)
