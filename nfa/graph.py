#!/usr/bin/python
# -*-  coding:utf-8 -*-
__author__ = 'aducode@126.com'
import types
import os

operator_priority = {'|': 1, '.': 2, '*': 3, '?': 3, '+': 3, '(': -1, } # 运算符优先级
operations_num_map = {'|': 2, '.': 2, '*': 1, '?': 1, '+': 1}


class Node(object):
    """
    图的节点
    """
    id = 0

    def __init__(self, in_edges=None, out_edges=None, is_end=False):
        """
        图的节点
        :param in_edges:  进入节点的边列表
        :param out_edges:  出去节点的边列表
        :param is_end:    是否是接受状态
        :return:
        """
        self.id = self.__class__.id
        self.__class__.id += 1
        if isinstance(in_edges, types.ListType):
            self.in_edges = in_edges
        elif isinstance(in_edges, Edge):
            self.in_edges = [in_edges]
        else:
            self.in_edges = []
        if isinstance(out_edges, types.ListType):
            self.out_edges = out_edges
        elif isinstance(out_edges, Edge):
            self.out_edges = [out_edges]
        else:
            self.out_edges = []
        self.is_end = is_end

    def add_in_edge(self, edge):
        assert isinstance(edge, Edge)
        edge.end_node = self
        self.in_edges.append(edge)

    def add_out_edge(self, edge):
        assert isinstance(edge, Edge)
        edge.start_node = self
        self.out_edges.append(edge)

    def next(self, value=None):
        """
        下一批节点
        """
        for out_edge in self.out_edges:
            if not value or (out_edge.value == value or not out_edge.value):
                yield out_edge.end_node, out_edge

    def merge(self, node):
        """
        该节点与node合并
        """
        ret = None
        for out_edge in self.out_edges:
            if out_edge.end_node == node:
                ret = out_edge
                self.out_edges.remove(out_edge)
                break
        self.is_end = node.is_end
        for in_edge in self.in_edges:
            node.add_in_edge(in_edge)
        for out_edge in self.out_edges:
            node.add_out_edge(out_edge)
        return ret

    # def pop_in_edge(self, node):
    #     ret = None
    #     for edge in self.in_edges:
    #         if edge.start_node == node:
    #             ret = edge
    #             break
    #     if ret:
    #         self.in_edges.remove(ret)
    #         node.out_edges.remove(ret)
    #         ret.start_node = None
    #         ret.end_node = None
    #     return ret
    #
    # def pop_out_edge(self, node):
    #     ret = None
    #     for edge in self.out_edges:
    #         if edge.end_node == node:
    #             ret = edge
    #             break
    #     if ret:
    #         self.out_edges.remove(ret)
    #         node.in_edges.remove(ret)
    #         ret.start_node = None
    #         ret.end_node = None
    #     return ret

class Edge(object):
    """
    图的边
    """
    def __init__(self, value=None, start_node=None, end_node=None):
        """
        图的边
        :param value:  边上的值
        :param start_node: 边的开始节点
        :param end_node: 边的结束节点
        :return:
        """
        self.value = value
        self.start_node = start_node
        if isinstance(self.start_node, Node):
            self.start_node.add_out_edge(self)
        self.end_node = end_node
        if isinstance(self.end_node, Node):
            self.end_node.add_in_edge(self)

def clone_graph(start, end, visited=set()):
    """
    复制图
    :param start: 开始节点
    :param end:  结束节点
    """
    pass


def make_graph(op, value_stack, edge_set):
    if op == '.':
        assert len(value_stack) >= 2
        start2, end2 = value_stack.pop()
        start1, end1 = value_stack.pop()
        old_edge = end1.merge(start2)
        if old_edge and old_edge in edge_set:
            edge_set.remove(old_edge)
        value_stack.append((start1, end2))
    elif op == '|':
        assert len(value_stack) >= 2
        start2, end2 = value_stack.pop()
        start1, end1 = value_stack.pop()
        end1.is_end = False
        end2.is_end = False
        start = Node()
        end = Node(is_end=True)
        edge_set.add(Edge(start_node=start, end_node=start1))
        edge_set.add(Edge(start_node=start, end_node=start2))
        edge_set.add(Edge(start_node=end1, end_node=end))
        edge_set.add(Edge(start_node=end2, end_node=end))
        value_stack.append((start, end))
    elif op == '*':
        assert len(value_stack) >= 1
        _start, _end = value_stack.pop()
        _end.is_end = False
        edge_set.add(Edge(start_node=_end, end_node=_start))
        start = Node()
        end = Node(is_end=True)
        edge_set.add(Edge(start_node=start, end_node=_start))
        edge_set.add(Edge(start_node=_end, end_node=end))
        edge_set.add(Edge(start_node=start, end_node=end))
        value_stack.append((start, end))
    elif op == '?':
        assert len(value_stack) >= 1
        _start, _end = value_stack.pop()
        _end.is_end = False
        start = Node()
        end = Node(is_end=True)
        edge_set.add(Edge(start_node=start, end_node=_start))
        edge_set.add(Edge(start_node=_end, end_node=end))
        edge_set.add(Edge(start_node=start, end_node=end))
        value_stack.append((start, end))
    elif op == '+':
        assert len(value_stack) >= 1
        _start, _end = value_stack.pop()
        _end.is_end = False
        edge_set.add(Edge(start_node=_end, end_node=_start))
        start = Node()
        end = Node(is_end=True)
        edge_set.add(Edge(start_node=start, end_node=_start))
        edge_set.add(Edge(start_node=_end, end_node=end))
        value_stack.append((start, end))


def build_nfa(pattern):
    """
    根据正则表达式构造nfa
    :param pattern: 正则表达式
    :return (start_node, end_node, edge_set):
    """
    if not pattern:
        return
    edge_set = set()
    value_stack = []
    op_stack = []
    i = 0
    next_is_cat = True
    is_op = False
    is_first = True
    while i < len(pattern):
        token = pattern[i]
        if token == '|':
            # 操作符
            next_is_cat = False
            is_op = True
        elif token == '*':
            is_op = True
        elif token == '?':
            is_op = True
        elif token == '+':
            is_op =True
        elif token == '(':
            op_stack.append(token)
            next_is_cat = False
            i += 1
            continue
        elif token == ')':
            while op_stack[-1] != '(':
                _op = op_stack.pop()
                make_graph(_op, value_stack, edge_set)
            next_is_cat = True
            i += 1
            continue
        # elif token == '?':
        #     is_op = True
        #     continue
        # elif token == '+':
        #     is_op = True
        #     continue
        # elif token == '[' or token == ']':
        #     is_op = True
        #     continue
        # elif token == '{' or token == '}':
        #     is_op = True
        elif token == '\\':
            # skip 1
            i += 1
            token = pattern[i]
        if is_op:
            # 符号
            op = token
            while op_stack and operator_priority[op_stack[-1]] >= operator_priority[op]:
                _op = op_stack.pop()
                make_graph(_op, value_stack, edge_set)
            op_stack.append(op)
            is_op = False
        else:
            # 字符串
            if not is_first and next_is_cat:
                # 需要插入cat运算符
                op = '.'
                while op_stack and operator_priority[op_stack[-1]] >= operator_priority[op]:
                    _op = op_stack.pop()
                    make_graph(_op, value_stack, edge_set)
                op_stack.append(op)
            start_node = Node()
            end_node = Node(is_end=True)
            edge_set.add(Edge(token, start_node=start_node, end_node=end_node))
            value_stack.append((start_node, end_node))
            next_is_cat = True
        is_first = False
        i += 1
    while op_stack:
        _op = op_stack.pop()
        make_graph(_op, value_stack, edge_set)
    if not value_stack:
        return None, None, set()
    start, end = value_stack[0]
    Node.id = 0
    return start, end, edge_set


def visit_nfa(start, edge_count, dot, visited=set()):
    """
    遍历图
    :param start:
    :param end:
    :return:
    """
    if len(visited) == edge_count:
        return
    for node, edge in start.next():
        if edge not in visited:
            visited.add(edge)
            dot.write('%s->%s%s;' % (start.id, node.id, '[label="%s"]' % edge.value if edge.value else ''))
            visit_nfa(node, edge_count, dot, visited)


if __name__ == '__main__':
    i = 0
    if not os.path.exists('digraphs'):
        os.mkdir('digraphs')
    while True:
        pattern = raw_input('input pattern:\n')
        if pattern == '/quit':
            break
        start, end, edge_set = build_nfa(pattern)
        with open('digraphs/digraph%d.dot'%i, 'w') as dot:
            dot.write('digraph G{')
            dot.write('A[shape=box,label="%s"]' % pattern)
            visit_nfa(start, len(edge_set), dot, visited=set())
            dot.write('%s[color=red,peripheries=2]' % end.id)
            dot.write('%s[color=blue]' % start.id)
            dot.write('}')
        os.system('dot2png.bat %d'%i)
        i += 1