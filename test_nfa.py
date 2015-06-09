#!/usr/bin/python
# -*- coding:utf-8 -*-
import os
from nfa.graph import write2dot
from nfa.graph import nfa2dfa
from nfa.graph import build_nfa
from nfa.reg import compile

if __name__ == '__main__':
    i = 0
    while True:
        pattern = raw_input('input pattern:\n')
        if pattern == '/quit' or pattern=='/q':
            break
        start, end, edge_set = build_nfa(pattern)
        #if not os.path.exists('digraphs'):
        #    os.mkdir('digraphs')
        #with open('digraphs/nfa%d.dot'%i, 'w') as dot:
        #    dot.write('digraph G{')
        #    dot.write('A[shape=box, label="%s"]' % pattern)
        #    write2dot(edge_set, dot)
        #    dot.write('%s[color=blue]' % start.id)
        #    dot.write('%s[color=red, peripheries=2]' % end.id)
        #    dot.write('}')
        #os.system('dot2png.bat %d %s'% (i,'nfa'))
        #start, end, edge_set = nfa2dfa(start, end, edge_set)
        p = compile(pattern)
        if not p:
            print 'Empyt pattern'
            continue
        #with open('digraphs/dfa%d.dot'%i, 'w') as dot:
        #    dot.write('digraph G{')
        #    dot.write('A[shape=box,label="%s"]' % pattern)
        #    write2dot(p.edges, dot)
        #    for _e in p.ends:
        #        dot.write('%s[color=red,peripheries=2]' % _e.id)
        #    if p.start not in p.ends:
        #        dot.write('%s[color=blue]' % p.start.id)
        #    else:
        #        dot.write('%s[color=blue,peripheries=2]' % p.start.id)
        #    dot.write('}')
        #os.system('dot2png.bat %d %s'% (i,'dfa'))
        i += 1
        while True:
            text = raw_input('input text:\n# ')
            if text == '/q' or text == '/quit':
                break
            for m in p.search(text):
                if m:
                    print '>', m.group()