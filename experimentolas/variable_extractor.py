# !/usr/bin/env python
# -*- coding: utf-8 -*-

from collections import namedtuple
from types import StringTypes


Variable = namedtuple('Variable', ['name', 'value'])


class VariableExtractor(object):
    def __init__(self, name, extract_func):
        assert isinstance(name, StringTypes)
        assert callable(extract_func)

        self._name = name
        self._extract_func = extract_func

    def extract(self, post):
        assert post is not None
        value = self._extract_func(post)
        return Variable(self._name, value)


def count_words_in(post):
    if post.content:
        return len(post.content.split(' '))
    else:
        return 0


WordCountExtractor = VariableExtractor('word_count', count_words_in)
