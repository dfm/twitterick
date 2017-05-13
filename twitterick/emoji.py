# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

__all__ = ["replace_unicode_emoji"]

from ._unicode_characters import UNICODE_ALIAS

_unicode_modifiers = ("\ufe0e", "\ufe0f")


def _name_for(character):
    for modifier in _unicode_modifiers:
        character = character.replace(modifier, '')
    return UNICODE_ALIAS.get(character, False)


def _image_string(name):
    return "<img class=\"emoji\" src=\"/static/emoji/{0}.png\">".format(name)


def replace_unicode_emoji(self, text):
    output = []
    for i, character in enumerate(text):
        if character in _unicode_modifiers:
            continue
        name = _name_for(character)
        if name:
            character = _image_string(name)
        output.append(character)
    return "".join(output)
