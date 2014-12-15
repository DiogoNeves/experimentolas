# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""Right now this only supports wordpress. Working on it."""

from collections import namedtuple


Blog = namedtuple('Blog', ['title', 'subtitle', 'url', 'posts'])
Post = namedtuple('Post', ['id', 'title', 'subtitle', 'image_url', 'content'])


class BlogException(Exception):
    pass


def get_blog_data_from(url, page_requester):
    pass


def find_all_pages(base_url):
    pass


def get_all_post_data_from(page_html):
    pass


def find_all_posts(page_parser):
    pass


def get_post_data_from(post_parser):
    pass


def main():
    pass

if __name__ == '__main__':
    main()
