# -*- coding: utf-8 -*-
from urlparse import urljoin

from HTMLParser import HTMLParser

import requests

from editor.models import Format


class LinksParser(HTMLParser):
    """ Collects all links from given url. """

    def __init__(self, url, *args, **kwargs):
        self.links = []
        self.in_a = False
        self.url = url
        HTMLParser.__init__(self, *args, **kwargs)

    def handle_starttag(self, tag, attrs):
        """ Collects all attributes of the link, extends relative paths."""
        if tag == 'a':
            self.in_a = True
            link = {val: key for val, key in attrs}
            href = link.get('href', '')
            if not href.startswith('http'):
                # this is not absolute path.
                link['href'] = urljoin(self.url, href)
            self.links.append(link)

    def handle_endtag(self, tag):
        if tag == 'a':
            self.in_a = False

    def handle_data(self, data):
        """ Updates last link found with `a` text. """
        if self.in_a:
            self.links[-1]['text'] = data.strip()


def get_links(url):
    """ Gets content from url, finds all links in the content and returns the list of dict.

    Args:
        url (str):

    Returns:
        list of dicts: for example [{'text': 'Yandex', 'href': 'http://ya.ru', 'title': 'Yandex'}]

    """
    resp = requests.get(url)
    assert resp.status_code == 200

    parser = LinksParser(url)
    parser.feed(resp.content)
    return parser.links


def filter_links(links, include_extensions=None):
    """ Removes all links who disagree with given extensions.

    Args:
        links (list of dicts): links to filter.
        include_extensions (list or None): extensions to match to. If empty, returns
            given links without any changes.

    Returns:
        filtered links (list of dicts):

    """

    if not include_extensions:
        return links

    filtered_links = []
    for link in links:
        for ext in include_extensions:
            if link['href'].endswith(ext):
                filtered_links.append(link)
    return filtered_links


def guess_format(links):
    """ Guesses format of the each link from given list of links.

    Args:
        links (list of dicts):

    Returns:
        list of dicts:

    """
    guessed_links = []
    for link in links:
        link['format'] = {}
        format = Format.guess_by_path(link['href'])
        if format:
            link['format']['id'] = format.id
            link['format']['name'] = format.name
        link['file_name'] = link['href'].split('/')[-1]
        link['truncated_href'] = truncate_value(link['href'])
        guessed_links.append(link)
    return guessed_links


def truncate_value(value):
    """ If value is longer then max length, then replaces excess chars in the middle
        with `...`.
    """
    URL_MAX_LENGTH = 60
    if len(value) > URL_MAX_LENGTH:
        value = u'%s...%s' % (value[:40], value[-20:])
    return value
