# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""Right now this only supports wordpress. Working on it."""

from collections import namedtuple
import itertools
import rfc3987 as iri


Blog = namedtuple('Blog', ['title', 'subtitle', 'url', 'posts'])
empty_blog = Blog('', '', '', [])
Post = namedtuple('Post', ['id', 'title', 'subtitle', 'image_url', 'content'])
empty_post = Post('', '', '', '', '')


class BlogException(Exception):
    pass


def _is_valid_url(url):
    iri_match = iri.match(url, rule='absolute_IRI')
    return iri_match is not None


def get_blog_data_from(url, page_requester):
    if not url:
        return empty_blog
    if not _is_valid_url(url):
        raise BlogException('Invalid blog url "%s"' % url)


def find_all_page_urls(base_url):
    def form_page_url(page):
        prefix_slash = '' if base_url.endswith('/') else '/'
        return '%s%spage/%d' % (base_url, prefix_slash, page)

    assert _is_valid_url(base_url)
    return (form_page_url(i) for i in itertools.count(1))


def get_all_post_data_from(page_html):
    return []


def find_all_posts(page_parser):
    return (i for i in xrange(0))


def get_post_data_from(post_parser):
    return empty_post


def main():
    pass

if __name__ == '__main__':
    main()
