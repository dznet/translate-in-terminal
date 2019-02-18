# -*- coding: utf-8 -*-
import argparse
import pyperclip
from googletrans import Translator

LANG = {'ko': 'en', 'en': 'ko'}

try:
    pyperclip.paste()
    CLIPBOARD_MESSAGE = 'Using clipboard data.'
except pyperclip.PyperclipException:
    CLIPBOARD_MESSAGE = """
    This error should only appear on Linux (not Windows or Mac). 
    You can fix this by installing one of the copy/paste mechanisms:
    
    sudo apt-get install xsel to install the xsel utility.
    sudo apt-get install xclip to install the xclip utility.
    pip install gtk to install the gtk Python module.
    pip install PyQt4 to install the PyQt4 Python module.
    """
    del pyperclip


def translate(text: list):
    text = ' '.join(text)
    text = text.replace('\n', ' ')

    # Translating each text message
    translator = Translator()
    lang = translator.detect(text).lang
    if lang not in ('ko', 'en'):
        raise ValueError('Unsupported Language. English, Korean Only.')
    data = translator.translate(text, dest=LANG[lang]).text
    return data


def clipboard():
    if 'pyperclip' not in globals():
        raise argparse.ArgumentError(None, CLIPBOARD_MESSAGE)
    text = pyperclip.paste()
    return [text]


class TranslateAction(argparse._StoreAction):
    def __init__(self, option_strings, dest, nargs=None, const=None,
                 default=None, type=None, choices=None, required=False,
                 help=None, metavar=None ):

        super(TranslateAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=default,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(self, parser:argparse.ArgumentParser, namespace, values,
                 option_string=None):
        text = values
        if 'clipboard' in namespace and getattr(namespace, 'clipboard'):
            text = clipboard()
        setattr(namespace, self.dest, text)


def parser(*args, **kwargs):
    _parser = argparse.ArgumentParser(description='Terminal translator',
                                      argument_default=argparse.SUPPRESS)
    _parser.register('action', 'translate', TranslateAction)
    _parser.add_argument('-c', '--clipboard', action='store_true',
                         help=CLIPBOARD_MESSAGE)
    _parser.add_argument('-d', '--dumb', action='store_true', default=False,
                         help='No showing output data.')
    _parser.add_argument('data', metavar='text', nargs='*', action='translate',
                         default=None, help='The text to query.')
    args = _parser.parse_args(*args)
    return args, _parser


def main(*argv):
    args, _parser = parser(*argv)
    if not args.data:
        raise _parser.error('No text to translate.')

    try:
        result = translate(args.data)
    except ValueError as e:
        raise _parser.error(str(e))

    if 'pyperclip' in globals():
        pyperclip.copy(result)
    if not args.dumb:
        print(result)
    return result


if __name__ == '__main__':
    main()
