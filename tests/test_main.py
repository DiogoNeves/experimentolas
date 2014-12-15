# !/usr/bin/env python
# -*- coding: utf-8 -*-


import pytest
from experimentolas import *


def test_empty_url_has_no_data():
    assert get_blog_data_from('') == {}


def test_invalid_url_raises():
    invalid_url = 'httasdf'
    with pytest.raises(BlogException) as ex:
        get_blog_data_from(invalid_url)

    assert ex.message == 'Invalid blog url "%s"' % invalid_url
