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

empty_html = ''


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
        return response.text
    else:
        return empty_html


def get_blog_data_from(url, page_requester, page_limit):
    def get_parser(html):
        return BeautifulSoup(html)

    if not url:
        return empty_blog
    if not _is_valid_url(url):
        raise BlogException('Invalid blog url "%s"' % url)

    page_parser = None
    posts = []
    for page_url in find_all_page_urls(url, page_limit):
        page_html = page_requester(page_url)
        if page_html:
            page_parser = get_parser(page_html)
            posts.extend(get_all_post_data_from(page_parser))
        else:
            break

    if page_parser:
        title = page_parser.find('h1', 'site-title').text
    return Blog(title=title or '', subtitle='', url=url, posts=posts)


def find_all_page_urls(base_url, page_limit):
    def form_page_url(page):
        prefix_slash = '' if base_url.endswith('/') else '/'
        return '%s%spage/%d' % (base_url, prefix_slash, page)

    assert _is_valid_url(base_url)
    assert page_limit > 0
    return (form_page_url(i) for i in xrange(1, page_limit + 1))


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
