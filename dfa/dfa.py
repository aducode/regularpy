#!/usr/bin/python
# -*- coding:utf-8 -*-
__author__ = 'aducode@126.com'

def build_dfa(tree):
    """
    根据抽象语法树构建DFA
    :param (root, alpha_set): 抽象语法树
    :param alpha_set: 输入字符集合
    :return: (startState, endStates, States, Trans)  (初始状态, 接收状态, 状态集, 转换函数)
    """
    root = tree[0]
    alpha_set = tree[1]
    queue = [root.firstpos]
    start_state = tuple(root.firstpos)
    end_states = set()
    states = set()
    trans = {}
    while queue:
        s = tuple(queue.pop(0))
        states.add(s)
        is_end_state = False
        for n in s:
            if n.value == '\0':
                is_end_state = True
                break
        if is_end_state:
            end_states.add(s)
        for alpha in alpha_set:
            u = set()
            for node in s:
                if node.value == alpha:
                    u = u | node.followpos
            if u:
                u = tuple(u)
                if s not in trans:
                    trans[s] = {}
                trans[s][alpha] = u
                if u not in states:
                    queue.append(u)
    return start_state, end_states, states, trans
