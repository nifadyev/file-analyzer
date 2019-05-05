from src.file_analyzer import FileAnalyzer
import sys

file_analyzer = FileAnalyzer(sys.argv[1:])
# file_analyzer.validate_arguments()

#  Write only tags, their attributes and scripts to file



# HTML file features (or characteristics)
print('Total number of chars: ', file_analyzer.total_symbols_number)
print('Number of chars (markup information):', file_analyzer.markup_information_symbols)
print('Number of tags (markup information):', file_analyzer.markup_information_words)
# print('Number of chars in script tags (markup information):', file_analyzer.markup_information_script)
# print('Number of chars in style tags (markup information):', file_analyzer.markup_information_style)
print('Number of chars (displayed information):', file_analyzer.useful_information_symbols)
print('Number of words (displayed information):', file_analyzer.useful_information_words)
print('Displayed information to markup information ratio:',
      f'{file_analyzer.useful_info_to_markup_info_ratio:.2f}')