#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
from graph import write2dot
from graph import compress_nfa
from graph import build_nfa

if __name__ == '__main__':
    i = 0
    if not os.path.exists('digraphs'):
        os.mkdir('digraphs')
    while True:
        pattern = raw_input('input pattern:\n')
        if pattern == '/quit' or pattern=='/q':
            break
        start, end, edge_set = build_nfa(pattern)
        start, end, edge_set = compress_nfa(start, end, edge_set)
        with open('digraphs/digraph%d.dot'%i, 'w') as dot:
            dot.write('digraph G{')
            dot.write('A[shape=box,label="%s"]' % pattern)
            write2dot(edge_set, dot)
            for _e in end:
                dot.write('%s[color=red,peripheries=2]' % _e.id)
            if start not in end:
                dot.write('%s[color=blue]' % start.id)
            else:
                dot.write('%s[color=blue,peripheries=2]' % start.id)
            dot.write('}')
        os.system('dot2png.bat %d'%i)
        i += 1