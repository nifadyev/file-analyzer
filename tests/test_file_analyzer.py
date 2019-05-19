import pytest
from src.file_analyzer import FileAnalyzer

# class TestBasics:
#     def 

@pytest.fixture()
def simple_html_file_analyzer():
    yield FileAnalyzer(['examples/simple.html'])
class TestHTML:
    def test_simple_local_file(self):
        file_analyzer = FileAnalyzer(['examples/simple.html'])

    def test_total_chars_number(self, simple_html_file_analyzer):
        assert simple_html_file_analyzer.total_symbols_number == 527

    def test_markup_chars_number(self, simple_html_file_analyzer):
        assert simple_html_file_analyzer.markup_information_symbols == 505

    def test_tags_number(self, simple_html_file_analyzer):
        assert simple_html_file_analyzer.markup_information_words == 12

    def test_style_chars_number(self, simple_html_file_analyzer):
        assert simple_html_file_analyzer.markup_information_style == 62

    def test_script_chars_number(self, simple_html_file_analyzer):
        assert simple_html_file_analyzer.markup_information_script == 99

    def test_displayed_info_chars_number(self, simple_html_file_analyzer):
        assert simple_html_file_analyzer.useful_information_symbols == 22

    def test_displayed_info_word_number(self, simple_html_file_analyzer):
        assert simple_html_file_analyzer.useful_information_words == 4

    def test_most_common_tag(self, simple_html_file_analyzer):
        assert simple_html_file_analyzer.most_common_tag == 'meta'

    # ? How to compare float numbers
    # def test_ratio(self, simple_html_file_analyzer):
        # assert simple_html_file_analyzer.useful_info_to_markup_info_ratio == 0.04
