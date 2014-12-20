# !/usr/bin/env python
# -*- coding: utf-8 -*-
import itertools
import pytest
from datetime import datetime
from dateutil.tz import tzlocal
from bs4 import BeautifulSoup
from experimentolas.blog_importer import Post, Blog, BlogException, \
    empty_blog, empty_post, empty_parser, null_date
from experimentolas.blog_importer import get_blog_data_from, \
    iterate_pages, get_all_post_data_from, iterate_all_posts, \
    try_get_post_data_from, get_parser, page_requester, try_parse_date, \
    valid_url


page_html = '<html><body>%s</body></html>'


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
        <span class="entry-date published" time="2014-12-15T22:29:25+00:00">
            15 de Dezembro de 2014
        </span>
    </header>
    <div class="entry-content"><p>Some text.</p></div>
</article>
"""

no_date_post_html = """<article id="post-001">
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


single_post_data = Post(id='post-001', title='Some Post',
                        date=try_parse_date('2014-12-15T22:29:25+00:00'),
                        images=('http://someblog.net/test.jpg',),
                        content='<p>Some text.</p>')

no_date_post_data = Post(id='post-001', title='Some Post',
                         date=null_date,
                         images=('http://someblog.net/test.jpg',),
                         content='<p>Some text.</p>')


single_blog_data = Blog(title='Some Blog', url='http://someblog.net',
                        posts=(single_post_data,))


def get_title(attribute, title_class):
    assert attribute == 'class' or attribute == 'id'
    return '<h1 %s="%s">Some Blog</h1>' % (attribute, title_class)


def get_site_title(attribute='class'):
    return get_title(attribute, 'site-title')


def get_blog_title(attribute='class'):
    return get_title(attribute, 'blog-title')


def get_page_html(title, content):
    return page_html % (title + content)


def mock_page_requester_wrapper(html, max_requests=10):
    def _page_requester(url):
        if _page_requester.times_requested < max_requests:
            _page_requester.times_requested += 1
            return get_parser(html)
        else:
            return empty_parser

    _page_requester.times_requested = 0
    return _page_requester


def null_requester(url):
    return ''


def default_requester(url):
    return get_parser(get_page_html(get_site_title(), single_post_page_html))


def assert_no_more_items(iterator):
    with pytest.raises(StopIteration):
        next(iterator)


def test_empty_returns_null_date():
    assert try_parse_date('') == null_date


def test_invalid_returns_null_date():
    assert try_parse_date('invalid') == null_date


def test_no_timezone_returns_localtz():
    # pylint: disable=E1103
    assert try_parse_date('0001-01-01T00:00:00').tzinfo == tzlocal()


def test_different_locales_match():
    assert try_parse_date('0001-01-01T00:00:00+00:00') == \
        try_parse_date('0001-01-01T01:00:00+01:00')


def test_empty_url_is_not_valid():
    assert not valid_url('')


def test_invalid_is_invalid():
    assert not valid_url('invalid')


def test_relative_is_invalid():
    assert not valid_url('/relative')


def test_valid_is_valid():
    assert valid_url('http://linguas.pt')
    assert valid_url('http://linguas.pt/')


def test_query_params_is_valid():
    assert valid_url('http://linguas.pt/test?param=1')


def test_empty_blog_url_has_no_data():
    assert get_blog_data_from('', null_requester, 10) == empty_blog


def test_invalid_url_raises():
    invalid_url = 'httasdf'
    with pytest.raises(BlogException) as ex_info:
        get_blog_data_from(invalid_url, null_requester, 10)

    assert ex_info.value.message == 'Invalid blog url "%s"' % invalid_url


def assert_title_matches(title):
    content_html = get_page_html(title, single_post_page_html)
    requester = mock_page_requester_wrapper(content_html)
    blog = get_blog_data_from('http://someblog.net', requester, 1)

    expected = 'Some Blog' if title else ''
    assert blog.title == expected
    assert len(blog.posts) == 1


def test_no_title_returns_data():
    assert_title_matches('')


def test_site_title_matches():
    assert_title_matches(get_site_title('class'))
    assert_title_matches(get_site_title('id'))


def test_blog_title_matches():
    assert_title_matches(get_blog_title('class'))
    assert_title_matches(get_blog_title('id'))


def test_returns_data():
    blog = get_blog_data_from('http://someblog.net', default_requester, 1)
    assert blog == single_blog_data


def test_iterator_increments(blog_url='http://someblog.net'):
    def is_valid_page(page_parser):
        return isinstance(page_parser, BeautifulSoup)

    page_it = iterate_pages(blog_url, default_requester, 2)
    assert is_valid_page(next(page_it))
    assert is_valid_page(next(page_it))


def test_trailing_slash_works():
    test_iterator_increments(blog_url='http://someblog.net/')


def test_iterator_stops():
    page_it = iterate_pages('http://someblog.net', default_requester, 1)
    next(page_it)
    assert_no_more_items(page_it)


def test_blog_stops_on_empty_page():
    content_html = get_page_html(get_site_title(), single_post_page_html)
    requester = mock_page_requester_wrapper(content_html, 1)
    page_it = iterate_pages('http://someblog.net', requester, 2)
    next(page_it)
    assert_no_more_items(page_it)


def test_empty_html_has_no_posts():
    assert get_all_post_data_from(empty_parser) == ()


def test_single_post_in_page():
    page_parser = default_requester('http://someblog.net')
    assert get_all_post_data_from(page_parser) == (single_post_data,)


def test_no_posts_in_empty_parser():
    assert_no_more_items(iterate_all_posts(empty_parser))


def test_single_post_returns_only_one():
    single_post_parser = get_parser(single_post_page_html)
    post_it = iterate_all_posts(single_post_parser)
    next(post_it)
    assert_no_more_items(post_it)


def test_single_post_is_found():
    single_post_parser = get_parser(single_post_page_html)
    assert next(iterate_all_posts(single_post_parser)) == \
        get_parser(single_post_html).find('article')


def test_no_data_in_empty_post():
    assert try_get_post_data_from(empty_parser) == empty_post


def test_single_post_data():
    single_post_parser = get_parser(single_post_html)
    post = single_post_parser.find('article')
    assert try_get_post_data_from(post) == single_post_data


def test_no_date_post_data():
    no_date_post_parser = get_parser(no_date_post_html)
    post = no_date_post_parser.find('article')
    assert try_get_post_data_from(post) == no_date_post_data


@pytest.fixture(scope='module', params=[
    'http://whyevolutionistrue.wordpress.com/', 'http://www.linguas.pt/'])
def real_blog_data(request):
    return get_blog_data_from(request.param, page_requester, max_pages=1)


@pytest.mark.integration_test
def test_real_blog(real_blog_data):
    assert real_blog_data.title
    assert valid_url(real_blog_data.url)
    assert len(real_blog_data.posts) > 1
    assert_valid_post(real_blog_data.posts[0])


def assert_valid_post(post):
    assert post.id.startswith('post-')
    assert post.title
    assert isinstance(post.date, datetime) and post.date != null_date
    assert isinstance(post.images, tuple)
    assert post.content
