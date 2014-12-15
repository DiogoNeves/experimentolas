# !/usr/bin/env python
# -*- coding: utf-8 -*-


import pytest
from experimentolas.blog_extractor import *


page_html = '<html><body>%s</body></html>'


single_post_html = """<main id="main">
<article id="post-001">
    <header>
        <h1 class="entry-title">
            <a href="http://www.someblog.net/2014/12/14/some-post/">Some Post</a>
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


def test_empty_blog_url_has_no_data():
    assert get_blog_data_from('', null_requester) == {}


def test_invalid_url_raises():
    invalid_url = 'httasdf'
    with pytest.raises(BlogException) as ex:
        get_blog_data_from(invalid_url, null_requester)

    assert ex.message == 'Invalid blog url "%s"' % invalid_url


def test_returns_data():
    requester = mock_page_requester_wrapper(single_post_html)
    blog = get_blog_data_from('http://someblog.net', requester)
    assert blog == single_blog_data


def test_empty_blog_url_has_no_pages():
    with pytest.raises(StopIteration):
        find_all_pages('')


def test_iterator_increments(blog_url='http://someblog.net'):
    page_it = find_all_pages(blog_url)
    assert next(page_it) == blog_url + '/page/1'
    assert next(page_it) == blog_url + '/page/2'


def test_trailing_slash_works():
    test_iterator_increments(blog_url='http://someblog.net/')


def test_empty_html_has_no_posts():
    assert get_all_post_data_from('') == []


def test_single_post_in_page():
    assert get_all_post_data_from(single_post_html) == [single_post_data]


def test_no_posts_in_empty_parser():
    pass


def test_single_post():
    pass


def test_no_data_in_empty_post():
    pass


def test_single_post_data():
    pass
