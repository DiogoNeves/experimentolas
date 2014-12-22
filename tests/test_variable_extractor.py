# !/usr/bin/env python
# -*- coding: utf-8 -*-

from types import StringTypes
from datetime import datetime
from random import random
import pytest
from experimentolas.variable_extractor import Variable, VariableExtractor, \
    count_words_in, WordCountExtractor
from experimentolas.blog_importer import Post, empty_post


sample_post = Post('post-001', 'test_title', datetime.now, (),
                   'this is a test. yes!')
sample_post_word_count = 5


def test_variable_extractor_returns_the_func_value():
    def random_extractor(post):
        random_extractor.value = int(random() * 10)
        return random_extractor.value

    extractor = VariableExtractor('test', random_extractor)
    assert extractor.extract(empty_post).value == random_extractor.value


def test_variable_extractor_keeps_name():
    def nothingness(post):
        return len(post)

    variable = VariableExtractor('test_name', nothingness).extract(empty_post)
    assert variable.name == 'test_name'


def test_none_extractor_func_asserts():
    with pytest.raises(AssertionError):
        VariableExtractor('none', None)


def test_empty_post_returns_0_words():
    assert count_words_in(empty_post) == 0


def test_it_returns_right_word_count():
    assert count_words_in(sample_post) == sample_post_word_count


def test_variable_extractor_returns_value():
    variable = WordCountExtractor.extract(sample_post)
    assert_valid_variable(variable)
    assert variable.value == sample_post_word_count


def assert_valid_variable(variable):
    assert isinstance(variable, Variable)
    assert isinstance(variable.name, StringTypes)
