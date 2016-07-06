#!/usr/bin/python
# -*- coding:utf-8 -*-
from graph import build_nfa
from graph import nfa2dfa

class Match(object):
    def __init__(self, text, start, end):
        self.text = text
        self.start = start
        self.end = end

    def start(self, group=0):
        return self.start

    def end(self, group=0):
        return self.end

    def group(self, group=0):
        return self.text[self.start:self.end]


class Pattern(object):
    def __init__(self, pattern):
        self.start, self.ends, self.edges = nfa2dfa(*build_nfa(pattern))
        #self.nfa_start, nfa_end, self.nfa_edges = build_nfa(pattern)
        #self.dfa_start, self.dfa_ends, self.dfa_edges = nfa2dfa(self.nfa_start, nfa_end, self.nfa_edges)
        #self.nfa_ends = set([nfa_end])
        #self.start, self.ends, self.edges = self.dfa_start, self.dfa_ends, self.dfa_edges
        #self.start, self.ends, self.edges = self.nfa_start, self.nfa_ends, self.nfa_edges

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
                            yield Match(text, start, end)
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
                yield Match(text, start, end)

def compile(pattern):
    pattern = Pattern(pattern)
    return pattern if pattern.start and pattern.ends and pattern.edges else None
