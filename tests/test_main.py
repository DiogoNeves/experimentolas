# !/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from bs4 import BeautifulSoup
from experimentolas.blog_extractor import Post, Blog, BlogException, \
    empty_blog, empty_post
from experimentolas.blog_extractor import get_blog_data_from, \
    find_all_page_urls, get_all_post_data_from, find_all_posts, get_post_data_from


page_html = '<html><body>%s</body></html>'


single_post_html = """<main id="main">
<article id="post-001">
    <header>
        <h1 class="entry-title">
            <a href="some-link">Some Post</a>
        </h1>
        <div class="post-thumbnail">
            <a href="http://www.someblog.net/2014/12/14/some-post/">
                <img src="http://someblog.net/test.jpg">
            </a>
        </div>
    </header>
    <div class="entry-content">
        <p>Some text.</p>
    </div>
</article>
</main>"""


single_post_data = Post(id='post-001', title='Some Post', subtitle='',
                        image_url='http://someblog.net/test.jpg',
                        content='<p>Some text.</p>')


single_blog_data = Blog(title='Some Blog', subtitle='',
                        url='http://someblog.net', posts=[single_post_data])


def mock_page_requester_wrapper(content):
    return (lambda url: page_html % content)


def null_requester(url):
    return ''


def assert_no_more_items(iterator):
    with pytest.raises(StopIteration):
        next(iterator)


def test_empty_blog_url_has_no_data():
    assert get_blog_data_from('', null_requester) == empty_blog


def test_invalid_url_raises():
    invalid_url = 'httasdf'
    with pytest.raises(BlogException) as ex_info:
        get_blog_data_from(invalid_url, null_requester)

    assert ex_info.value.message == 'Invalid blog url "%s"' % invalid_url


def test_returns_data():
    requester = mock_page_requester_wrapper(single_post_html)
    blog = get_blog_data_from('http://someblog.net', requester)
    assert blog == single_blog_data


def test_iterator_increments(blog_url='http://someblog.net'):
    def is_valid_page_url(url, page):
        return url.endswith('/page/%d' % page) and url.find('//page') == -1

    page_it = find_all_page_urls(blog_url)
    assert is_valid_page_url(next(page_it), 1)
    assert is_valid_page_url(next(page_it), 2)


def test_trailing_slash_works():
    test_iterator_increments(blog_url='http://someblog.net/')


def test_empty_html_has_no_posts():
    assert get_all_post_data_from('') == []


def test_single_post_in_page():
    assert get_all_post_data_from(single_post_html) == [single_post_data]


def test_no_posts_in_empty_parser():
    empty_parser = BeautifulSoup('')
    assert_no_more_items(find_all_posts(empty_parser))


def test_single_post_returns_only_one():
    requester = mock_page_requester_wrapper(single_post_html)
    single_post_parser = BeautifulSoup(requester('http://someblog.net'))
    post_it = find_all_posts(single_post_parser)
    next(post_it)
    assert_no_more_items(post_it)


def test_single_post_returns_data():
    requester = mock_page_requester_wrapper(single_post_html)
    single_post_parser = BeautifulSoup(requester('http://someblog.net'))
    assert next(find_all_posts(single_post_parser)) == single_post_data


def test_no_data_in_empty_post():
    empty_parser = BeautifulSoup('')
    assert get_post_data_from(empty_parser) == empty_post


def test_single_post_data():
    single_post_parser = BeautifulSoup(single_post_html)
    assert get_post_data_from(single_post_parser) == single_post_data
