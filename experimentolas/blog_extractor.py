# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""Right now this only supports wordpress. Working on it."""

from collections import namedtuple
import itertools
import rfc3987 as iri
import HTMLParser
from bs4 import BeautifulSoup
import requests
from requests.exceptions import RequestException


Blog = namedtuple('Blog', ['title', 'subtitle', 'url', 'posts'])
empty_blog = Blog('', '', '', [])
Post = namedtuple('Post', ['id', 'title', 'subtitle', 'image_url', 'content'])
empty_post = Post('', '', '', '', '')

empty_parser = BeautifulSoup('')


class BlogException(Exception):
    pass


def _is_valid_url(url):
    iri_match = iri.match(url, rule='absolute_IRI')
    return iri_match is not None


def page_requester(url):
    assert _is_valid_url(url)

    try:
        return _request_page(url)
    except RequestException:
        return empty_html


def _request_page(url):
    response = requests.get(url)
    if response and response.ok:
        return BeautifulSoup(response.text)
    else:
        return empty_parser


def get_blog_data_from(url, page_requester, max_pages):
    def get_blog_title():
        blog_parser = page_requester(url)
        return blog_parser.find('h1', 'site-title').text

    if not url:
        return empty_blog
    if not _is_valid_url(url):
        raise BlogException('Invalid blog url "%s"' % url)

    title = get_blog_title()
    page_iterator = iterate_pages(url, page_requester, max_pages)
    posts = [post for page in page_iterator
             for post in get_all_post_data_from(page)]

    return Blog(title=title or '', subtitle='', url=url, posts=posts)


def iterate_pages(base_url, page_requester, max_pages):
    """max_pages is an int > 0"""

    def form_page_url(page):
        prefix_slash = '' if base_url.endswith('/') else '/'
        return '%s%spage/%d' % (base_url, prefix_slash, page)

    assert _is_valid_url(base_url)
    assert max_pages > 0

    page = 1
    while page <= max_pages:
        url = form_page_url(page)
        page_parser = page_requester(url)
        assert isinstance(page_parser, BeautifulSoup)

        if page_parser != empty_parser:
            yield page_parser
        else:
            return
        page += 1


def get_all_post_data_from(page_parser):
    def get_content_parser():
        return page_parser.find('main') or BeautifulSoup('')

    content_parser = get_content_parser()
    posts = find_all_posts(content_parser)
    return [try_get_post_data_from(post) for post in posts]


def find_all_posts(content_parser):
    post_tag = 'article'
    current_post = content_parser.find(post_tag)
    while current_post is not None:
        yield current_post
        current_post = current_post.find_next(post_tag)


def try_get_post_data_from(post_parser):
    try:
        return _get_post_data_from(post_parser)
    except (KeyError, HTMLParser.HTMLParseError):
        return empty_post


def _get_post_data_from(post_parser):
    post_id = post_parser['id']
    header = post_parser.find('header')
    title = header.find('a').text
    image = header.find('img')
    if image and 'src' in image.attrs:
        image = image['src']
    content_parser = post_parser.find('div', 'entry-content')
    content = ''.join(map(str, content_parser.children))
    return Post(id=post_id, title=title, subtitle='', image_url=image or '',
                content=content)


def main():
    pass

if __name__ == '__main__':
    main()
