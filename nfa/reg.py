#!/usr/bin/python
# -*- coding:utf-8 -*-
from graph import build_nfa
from graph import nfa2dfa

class Pattern(object):
    def __init__(self, pattern):
        self.start, self.ends, self.edges = nfa2dfa(*build_nfa(pattern))

    def search(self, text, pos=0, endpos=None):
        """
        search
        :param text: text
        :param pos: text start pos
        :param endpos: text end pos
        :return
        """
        text = text[pos:endpos if endpos is not None else  len(text)] if text else None
        if text:
            start = 0
            end = -1 if self.start not in self.ends else 0 # -1 not find
            i = 0
            current = self.start
            while i<len(text):
                alpha = text[i]
                try:
                    next, _ = current.next(alpha).next()
                except StopIteration:
                    if end != -1:
                        if start<end:
                            yield text[start:end]
                        i = start = end
                        end = -1
                    else:
                        i += 1
                        start = i
                    current = self.start
                else:
                    i += 1
                    current = next
                    if current in self.ends:
                        end = i
            if start<end:
                yield text[start:end]

def compile(pattern):
    pattern = Pattern(pattern)
    return pattern if pattern.start and pattern.ends and pattern.edges else None