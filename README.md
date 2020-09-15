# File Analyzer

![](https://img.shields.io/badge/python-v3.8-blue) ![](https://img.shields.io/badge/BeautifulSoup-4-blue) ![](https://img.shields.io/badge/platform-windows%20%7C%20linux-lightgrey)

Tool for analyzing HTML, JSON and XML files and output some characteristics such as nesting and other .

## Requirements
- python3.8+
- pip
- Beautiful Soup 4
- requests
- virtualenv (optional)

### Pip packages
Install required packages using `virtualenv`

```bash
python -m virtualenv env && source env/bin/activate
python -m pip install -r requirements.txt
```

## Usage

The only available option is:

 * `--file_path`: path to local file or URL

## Example

Parse `yandex.ru`

`python main.py yandex.ru`
