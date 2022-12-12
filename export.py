
import argparse
import os
import re

import bz2
import xml.sax

import wikitextparser as wtp


class WiktionaryXmlHandler(xml.sax.handler.ContentHandler):

    def __init__(self, handler):
        self.current_tag = None
        self.current_title = None
        self.current_text = None
        self.handler = handler

    def startElement(self, tag, attributes):
        self.current_tag = tag
        if tag == 'page':
            self.current_title = None
            self.current_text = str()

    def characters(self, content):
        if self.current_tag == 'title':
            if len(content.strip()) != 0:
                self.current_title = content
        elif self.current_tag == 'text':
            self.current_text += content

    def endElement(self, tag):
        if tag == 'page':
            self.handler.page(
                title=self.current_title,
                content=self.current_text
            )


class WiktionaryPageHandler:

    META_PAGE_TITLE = re.compile(r'([^:]+):.*')

    def __init__(self, languages=None):
        self.languages = languages

    def page(self, title, content):

        # Skip meta pages
        if self.META_PAGE_TITLE.fullmatch(title):
            return

        parsed = wtp.parse(content)
        for section in parsed.sections:

            # Skip all sections that are not at level 2 (languages)
            if section.title is None or section.level != 2:
                continue

            language = section.title.strip()
            # Skip non-included languages
            if self.languages is not None and language not in self.languages:
                continue

            self._language(title, language, section)

    def _language(self, title, language, section):
        pass


if __name__ == '__main__':

    parser = argparse.ArgumentParser(os.path.basename(__file__))
    parser.add_argument('dumpfile')
    args = parser.parse_args()

    page_handler = WiktionaryPageHandler()
    xml_handler = WiktionaryXmlHandler(page_handler)

    if args.dumpfile.endswith('.bz2'):
        with bz2.open(args.dumpfile, 'r') as dump:
            xml.sax.parse(dump, xml_handler)
    else:
        with open(args.dumpfile, 'r') as dump:
            xml.sax.parse(dump, xml_handler)

