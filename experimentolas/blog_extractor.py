# !/usr/bin/env python
# -*- coding: utf-8 -*-

"""Right now this only supports wordpress. Working on it."""

from collections import namedtuple


Blog = namedtuple('Blog', ['title', 'subtitle', 'url', 'posts'])
Post = namedtuple('Post', ['title', 'subtitle', 'image_url', 'popularity',
                           'data'])


class BlogException(Exception):
    pass


def get_blog_data_from(url):
    pass


def iterate_all_pages(base_url):
    pass


def get_posts_data_from(page):
    pass


def posts_in(page):
    pass


def get_post_data_from(post_parser):
    pass


def main():
    pass

if __name__ == '__main__':
    main()
