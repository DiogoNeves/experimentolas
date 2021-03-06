# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""Right now this only supports wordpress. Working on it."""

from collections import namedtuple
from datetime import datetime
from dateutil.parser import parse
from dateutil.tz import tzoffset, tzlocal
import itertools
import re
import rfc3987 as iri
import HTMLParser
from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException


null_date = datetime.fromordinal(1).replace(tzinfo=tzlocal())

Blog = namedtuple('Blog', ['title', 'url', 'posts'])
empty_blog = Blog('', '', ())
Post = namedtuple('Post', ['id', 'title', 'date', 'images', 'content'])
empty_post = Post('', '', null_date, (), '')

empty_parser = BeautifulSoup('')


def try_parse_date(date_string):
    try:
        return _parse_date(date_string)
    except (ValueError, AttributeError):
        return null_date


def _parse_date(date_string):
    if not date_string:
        return null_date

    parsed = parse(date_string, default=null_date)
    # pylint: disable=E1103
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=tzlocal())

    return parsed


def get_parser(content_html):
    return BeautifulSoup(content_html)


class BlogException(Exception):
    pass


def valid_url(url):
    iri_match = iri.match(url, rule='absolute_IRI')
    return iri_match is not None


def page_requester(url):
    assert valid_url(url)

    try:
        return _request_page(url)
    except RequestException:
        return empty_parser


def _request_page(url):
    response = requests.get(url)
    if response and response.ok:
        return get_parser(response.text)
    else:
        return empty_parser


def get_blog_data_from(url, requester, max_pages):
    def get_blog_title():
        blog_parser = requester(url)
        valid_attributes = ['id', 'class']
        valid_classes = ['site-title', 'blog-title']
        title = ''
        for title_query in itertools.product(valid_attributes, valid_classes):
            title_element = blog_parser.find('h1', dict([title_query]))
            if title_element:
                title = title_element.text
                break
        return title

    if not url:
        return empty_blog
    if not valid_url(url):
        raise BlogException('Invalid blog url "%s"' % url)

    title = get_blog_title()
    page_iterator = iterate_pages(url, requester, max_pages)
    posts = [post for page in page_iterator
             for post in get_all_post_data_from(page)]

    return Blog(title=title or '', url=url, posts=tuple(posts))


def iterate_pages(base_url, requester, max_pages):
    """max_pages is an int > 0"""

    def form_page_url(page):
        prefix_slash = '' if base_url.endswith('/') else '/'
        return '%s%spage/%d' % (base_url, prefix_slash, page)

    assert valid_url(base_url)
    assert max_pages > 0

    page = 1
    while page <= max_pages:
        url = form_page_url(page)
        page_parser = requester(url)
        assert isinstance(page_parser, BeautifulSoup)

        if page_parser != empty_parser:
            yield page_parser
        else:
            return
        page += 1


def get_all_post_data_from(page_parser):
    return tuple([try_get_post_data_from(post)
                  for post in iterate_all_posts(page_parser)])


def iterate_all_posts(content_parser):
    post_matcher = re.compile('^post-')
    current_post = content_parser.find(id=post_matcher)
    while current_post is not None:
        yield current_post
        current_post = current_post.find_next(id=post_matcher)


def try_get_post_data_from(post_parser):
    try:
        return _get_post_data_from(post_parser)
    except (KeyError, HTMLParser.HTMLParseError):
        return empty_post


def _get_post_data_from(post_parser):
    post_id = post_parser['id']
    header = post_parser.find(class_='entry-title')
    title = header.find('a').text
    date = _get_post_date(post_parser)
    images = [image['src'] for image in post_parser.find_all('img')
              if 'src' in image.attrs]
    content_parser = post_parser.find('div', 'entry-content')
    content = ''.join(map(str, content_parser.children))
    return Post(id=post_id, title=title, date=date, images=tuple(images),
                content=content)


def _get_post_date(post_parser):
    date_element = _find_date_element(post_parser)
    if date_element:
        return _find_date_in(date_element.attrs.values())
    else:
        return null_date


def _find_date_element(post_parser):
    return post_parser.find(class_='published')


def _find_date_in(attribute_values):
    date = null_date
    for parsed_date in itertools.imap(try_parse_date, attribute_values):
        if parsed_date != null_date:
            date = parsed_date
            break
    return date


def main():
    pass

if __name__ == '__main__':
    main()
