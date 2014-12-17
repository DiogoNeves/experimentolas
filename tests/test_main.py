# !/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest
from bs4 import BeautifulSoup
from experimentolas.blog_extractor import Post, Blog, BlogException, \
    empty_blog, empty_post
from experimentolas.blog_extractor import get_blog_data_from, \
    find_all_page_urls, get_all_post_data_from, find_all_posts, \
    try_get_post_data_from


page_html = '<html><body><h1 class="site-title">Some Blog</h1>%s</body></html>'


single_post_html = """<article id="post-001">
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
    <div class="entry-content"><p>Some text.</p></div>
</article>
"""


single_post_page_html = '<main>%s</main>' % single_post_html


single_post_data = Post(id='post-001', title='Some Post', subtitle='',
                        image_url='http://someblog.net/test.jpg',
                        content='<p>Some text.</p>')


single_blog_data = Blog(title='Some Blog', subtitle='',
                        url='http://someblog.net', posts=[single_post_data])


empty_parser = BeautifulSoup('')


def mock_page_requester_wrapper(content):
    return (lambda url: page_html % content)


def null_requester(url):
    return ''


def assert_no_more_items(iterator):
    with pytest.raises(StopIteration):
        next(iterator)


def test_empty_blog_url_has_no_data():
    assert get_blog_data_from('', null_requester, 10) == empty_blog


def test_invalid_url_raises():
    invalid_url = 'httasdf'
    with pytest.raises(BlogException) as ex_info:
        get_blog_data_from(invalid_url, null_requester, 10)

    assert ex_info.value.message == 'Invalid blog url "%s"' % invalid_url


def test_returns_data():
    requester = mock_page_requester_wrapper(single_post_page_html)
    blog = get_blog_data_from('http://someblog.net', requester, 1)
    assert blog == single_blog_data


def test_iterator_increments(blog_url='http://someblog.net'):
    def is_valid_page_url(url, page):
        return url.endswith('/page/%d' % page) and url.find('//page') == -1

    page_it = find_all_page_urls(blog_url, 10)
    assert is_valid_page_url(next(page_it), 1)
    assert is_valid_page_url(next(page_it), 2)


def test_trailing_slash_works():
    test_iterator_increments(blog_url='http://someblog.net/')


def test_iterator_stops():
    page_it = find_all_page_urls('http://someblog.net', 1)
    next(page_it)
    assert_no_more_items(page_it)


def test_iterator_asserts_less_than_one():
    with pytest.raises(AssertionError):
        find_all_page_urls(base_url='http://someblog.net', page_limit=0)


def test_empty_html_has_no_posts():
    assert get_all_post_data_from(empty_parser) == []


def test_single_post_in_page():
    requester = mock_page_requester_wrapper(single_post_page_html)
    page_parser = BeautifulSoup(requester('http://someblog.net'))
    assert get_all_post_data_from(page_parser) == [single_post_data]


def test_no_posts_in_empty_parser():
    assert_no_more_items(find_all_posts(empty_parser))


def test_single_post_returns_only_one():
    single_post_parser = BeautifulSoup(single_post_page_html)
    post_it = find_all_posts(single_post_parser)
    next(post_it)
    assert_no_more_items(post_it)


def test_single_post_is_found():
    single_post_parser = BeautifulSoup(single_post_page_html)
    assert next(find_all_posts(single_post_parser)) == \
        BeautifulSoup(single_post_html).find('article')


def test_no_data_in_empty_post():
    empty_parser = BeautifulSoup('')
    assert try_get_post_data_from(empty_parser) == empty_post


def test_single_post_data():
    single_post_parser = BeautifulSoup(single_post_html)
    post = single_post_parser.find('article')
    assert try_get_post_data_from(post) == single_post_data
