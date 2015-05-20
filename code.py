__author__ = 'Administrator'
from ast.tree import build_ast
from ast.dfa import build_dfa


def match(dfa, text):
    start_state = dfa[0]
    end_states = dfa[1]
    trans = dfa[3]
    current_state = start_state
    for t in text:
        current_state = trans[current_state].get(t, None)
        if not current_state:
            current_state = start_state
        elif current_state in end_states:
            return True
    return False

def group(dfa, text):
    start_state = dfa[0]
    end_states = dfa[1]
    trans = dfa[3]
    current_state = start_state
    start = end = 0
    for i in xrange(len(text)):
        t = text[i]
        current_state = trans[current_state].get(t, None)
        if not current_state:
            current_state = start_state
            start = i+1
        elif current_state in end_states:
            end = i+1
            yield text[start:end]
            current_state = start_state
            start = i+1

if __name__ == '__main__':
    re = raw_input("please input regular text:(input /quit to quit)\n")
    while re != '/quit':
        if re.startswith('/'):
            re = raw_input("can't contain '/', input another regular text:\n")
            continue
        tree = build_ast(re)
        # visit_ast(root)
        dfa = build_dfa(tree)
        # print 'start state:', dfa[0]
        # print 'end states:', dfa[1]
        # print 'states:', dfa[2]
        # print 'trans:', dfa[3]
        text = raw_input('please input text:(input /pattern for a new pattern)\n')
        while text != '/pattern':
            print '-' * 20
            # print 'is match?\t', 'yes' if match(dfa, text) else 'no'
            for t in group(dfa, text):
                print t
            text = raw_input('please input text:(input /pattern for a new pattern)\n')
        re = raw_input("please input regular text:(input /quit to quit)\n")
    print 'Bye~~'
