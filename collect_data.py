# import subprocess

# with open('examples/html/sites.txt') as sites:
#     # Right now works only for 1 site in txt file
#     # for site in sites.read():
#     subprocess.run(['python3.7', '/media/storage/YandexDisk/Programming/Git/file-analyzer/main.py', sites.read()])

from src.file_analyzer import FileAnalyzer

SITES = (
    # 'http://www.unn.ru',
    # 'http://www.itmm.unn.ru/studentam/raspisanie/',
    # 'https://www.github.com',
    # 'https://stackoverflow.com',
    # 'https://lifehacker.ru',

    'https://www.google.com',
    'https://www.example.com',
    'https://www.yandex.ru',
    'https://translate.google.ru/',
    'https://www.bing.com/',
    'https://lightweightsites.com/',
    'https://medium.com/nuances-of-programming/%D1%87%D0%B5%D0%BC%D1%83-%D1%8F-%D0%BD%D0%B0%D1%83%D1%87%D0%B8%D0%BB%D1%81%D1%8F-%D0%B7%D0%B0-%D0%BF%D0%B5%D1%80%D0%B2%D1%8B%D0%B5-%D0%B4%D0%B2%D0%B0-%D0%B3%D0%BE%D0%B4%D0%B0-%D1%80%D0%B0%D0%B1%D0%BE%D1%82%D1%8B-%D0%BF%D1%80%D0%BE%D0%B3%D1%80%D0%B0%D0%BC%D0%BC%D0%B8%D1%81%D1%82%D0%BE%D0%BC-3867eccc5856',
    'https://nuancesprog.ru/p/3433/',
    'https://trello.com',
    'https://git-scm.com/docs/git-credential-store',
    # ! Multiple repeat error re example
    # 'https://docs.python.org/3.7/library/string.html',
)

# open('results/json_data.txt', "w").close()
# for file_number in range(1, 11):
#     file_analyzer = FileAnalyzer([f'examples/json/{str(file_number)}.json'])
#     file_analyzer.collect_data('results/json_data.txt')

open('results/html_data.txt', "w").close()
for site in SITES:
    file_analyzer = FileAnalyzer([site])
    file_analyzer.collect_data('results/html_data.txt')

    # Count avg metrics here
