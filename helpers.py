# -*- coding: utf-8 -*-

import re

class StringEnum(object):
    """
    A simple object, constructed with a strings list and which defines one
    attribute for each string. Each attribute's value is its own name, except
    those with special chars.
    """

    def __init__(self, names):
        self.names = names
        for name in self.names:
            setattr(self, self.fix_name(name), name)

    def fix_name(self, name):
            return re.sub(r"[^a-zA-Z]", "_", name)

    def get_member(self, name):
        return getattr(self, self.fix_name(name))

    def get_names(self):
        return self.names[:]
