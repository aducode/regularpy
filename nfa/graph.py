#!/usr/bin/python
# -*-  coding:utf-8 -*-
__author__ = 'aducode@126.com'
import types

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


class Edge(object):
    """
    图的边
    """
    def __init__(self, value=None, start_node=None, end_node=None, edge_set=None):
        """
        图的边
        :param value:  边上的值
        :param start_node: 边的开始节点
        :param end_node: 边的结束节点
        :return:
        """
        if edge_set:
            for edge in edge_set:
                if edge.start_node == start_node and edge.end_node == end_node and edge.value==value:
                    return
        self.value = value
        self.start_node = start_node
        if isinstance(self.start_node, Node):
            self.start_node.add_out_edge(self)
        self.end_node = end_node
        if isinstance(self.end_node, Node):
            self.end_node.add_in_edge(self)
        if isinstance(edge_set, set):
            edge_set.add(self)


def make_graph(op, value_stack):
    """
    构造子图
    :param op: 操作符
    :param value_stack: 数值栈
    :param edge_set: 边集合
    """
    if op == '.':
        assert len(value_stack) >= 2
        start2, end2, edge_set2 = value_stack.pop()
        start1, end1, edge_set1 = value_stack.pop()
        edge_set = edge_set1 | edge_set2
        old_edge = end1.merge(start2)
        if old_edge and old_edge in edge_set:
            edge_set.remove(old_edge)
        value_stack.append((start1, end2, edge_set))
    elif op == '|':
        assert len(value_stack) >= 2
        start2, end2, edge_set2 = value_stack.pop()
        start1, end1, edge_set1 = value_stack.pop()
        end1.is_end = False
        end2.is_end = False
        edge_set = edge_set1 | edge_set2
        start = Node()
        end = Node(is_end=True)
        Edge(start_node=start, end_node=start1, edge_set=edge_set)
        Edge(start_node=start, end_node=start2, edge_set=edge_set)
        Edge(start_node=end1, end_node=end, edge_set=edge_set)
        Edge(start_node=end2, end_node=end, edge_set=edge_set)
        value_stack.append((start, end, edge_set))
    elif op == '*':
        assert len(value_stack) >= 1
        _start, _end, edge_set = value_stack.pop()
        Edge(start_node=_end, end_node=_start, edge_set=edge_set)
        Edge(start_node=_start, end_node=_end, edge_set=edge_set)
        value_stack.append((_start, _end, edge_set))
    elif op == '?':
        assert len(value_stack) >= 1
        _start, _end, edge_set = value_stack.pop()
        Edge(start_node=_start, end_node=_end, edge_set=edge_set)
        value_stack.append((_start, _end, edge_set))
    elif op == '+':
        assert len(value_stack) >= 1
        _start, _end, edge_set = value_stack.pop()
        Edge(start_node=_end, end_node=_start, edge_set=edge_set)
        value_stack.append((_start, _end, edge_set))
    elif (op.startswith('{') and op.endswith('}')):
        # 重复
        op = op[1:-1]
        if op.count(',') == 0:
            min_repeat = max_repeat = int(op)
        elif op.count(',') == 1:
            min_max = op.split(',')
            min_repeat = int(min_max[0]) if min_max[0] else 0
            max_repeat = int(min_max[1]) if min_max[1] else None
        if min_repeat>=0 and (max_repeat is None or max_repeat >= min_repeat):
            if min_repeat == 0 and max_repeat is None:
                return make_graph('*', value_stack)
            if min_repeat == 1 and max_repeat is None:
                return make_graph('+', value_stack)
            if min_repeat == 0 and max_repeat == 1:
                return make_graph('?', value_stack)
            _start, _end, _edge_set = value_stack.pop()
            if max_repeat is not None and max_repeat > 1:
                graph_list = list()
                tmp_nodes = list()
                for repeat in xrange(max_repeat-1):
                    graph_list.append(clone_nfa(_start, _end, _edge_set))
                for idx in xrange(len(graph_list)):
                    s, e, eset = graph_list[idx]
                    if idx >= min_repeat-1:
                        tmp_nodes.append(s)
                    _end.merge(s)
                    _edge_set = _edge_set | eset
                    _end = e
                if min_repeat == 0:
                    tmp_nodes.append(_start)
                for t in tmp_nodes:
                    Edge(start_node=t, end_node=_end, edge_set=_edge_set)
            elif max_repeat is None:
                graph_list = list()
                for repeat in xrange(min_repeat):
                    graph_list.append(clone_nfa(_start, _end, _edge_set))
                tmp_node = None
                for idx in xrange(len(graph_list)):
                    s, e, eset = graph_list[idx]
                    if idx == len(graph_list)-1:
                        tmp_node = s
                    _end.merge(s)
                    _edge_set = _edge_set | eset
                    _end = e
                Edge(start_node=tmp_node, end_node=_end, edge_set=_edge_set)
                Edge(start_node=_end, end_node=tmp_node, edge_set=_edge_set)
            value_stack.append((_start, _end, _edge_set))


def clone_nfa(start, end, edge_set):
    """
    复制
    :param start: 开始节点
    :param end: 结束节点
    :param edge_set: 边集合
    """
    edge_set_clone=set()
    start_clone=None
    end_clone=None
    visited_node=dict()
    for edge in edge_set:
        start_node=edge.start_node
        end_node=edge.end_node
        if start_node not in visited_node:
            visited_node[start_node]=Node(is_end=start_node.is_end)
        if end_node not in visited_node:
            visited_node[end_node] = Node(is_end=end_node.is_end)
        if not start_clone:
            if start_node == start:
                start_clone = visited_node[start_node]
            if end_node == start:
                start_clone = visited_node[end_node]
        if not end_clone:
            if start_node == end:
                end_clone = visited_node[start_node]
            if end_node == end:
                end_clone = visited_node[end_node]
        Edge(value=edge.value, start_node=visited_node[start_node], end_node=visited_node[end_node], edge_set=edge_set_clone)
    return start_clone, end_clone, edge_set_clone
    

def build_nfa(pattern):
    """
    根据正则表达式构造nfa
    :param pattern: 正则表达式
    :return (start_node, end_node, edge_set):
    """
    if not pattern:
        return
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
            if not is_first and next_is_cat:
                # 需要插入cat运算符
                op = '.'
                while op_stack and operator_priority[op_stack[-1]] >= operator_priority[op]:
                    _op = op_stack.pop()
                    make_graph(_op, value_stack)
                op_stack.append(op)
            op_stack.append(token)     
            next_is_cat = False
            i += 1
            continue
        elif token == ')':
            while op_stack[-1] != '(':
                _op = op_stack.pop()
                make_graph(_op, value_stack)
            op_stack.pop()
            next_is_cat = True
            i += 1
            continue
        elif token == '{':
            j = i+1
            while pattern[j] != '}':
                j += 1
            op = pattern[i:j+1]
            i = j + 1
            while op_stack and operator_priority[op_stack[-1]] >= operator_priority['*']:
                _op = op_stack.pop()
                make_graph(_op, value_stack)
            op_stack.append(op)
            continue
        elif token == '\\':
            # skip 1
            i += 1
            token = pattern[i]
        if is_op:
            # 符号
            op = token
            while op_stack and operator_priority[op_stack[-1]] >= operator_priority[op]:
                _op = op_stack.pop()
                make_graph(_op, value_stack)
            op_stack.append(op)
            is_op = False
        else:
            # 字符串
            if not is_first and next_is_cat:
                # 需要插入cat运算符
                op = '.'
                while op_stack and operator_priority[op_stack[-1]] >= operator_priority[op]:
                    _op = op_stack.pop()
                    make_graph(_op, value_stack)
                op_stack.append(op)
            edge_set=set()
            start_node = Node()
            end_node = Node(is_end=True)
            Edge(token, start_node=start_node, end_node=end_node, edge_set=edge_set)
            value_stack.append((start_node, end_node, edge_set))
            next_is_cat = True
        is_first = False
        i += 1
    while op_stack:
        _op = op_stack.pop()
        make_graph(_op, value_stack)
    Node.id = 0
    if not value_stack:
        return None, None, set()
    return value_stack.pop()

def write2dot(edge_set, dot):
    for edge in edge_set:
        dot.write('%s->%s%s;' % (edge.start_node.id, edge.end_node.id, '[label="%s"]' % edge.value if edge.value else ''))

if __name__ == '__main__':
    i = 0
    if not os.path.exists('digraphs'):
        os.mkdir('digraphs')
    while True:
        pattern = raw_input('input pattern:\n')
        if pattern == '/quit' or pattern=='/q':
            break
        start, end, edge_set = build_nfa(pattern)
        with open('digraphs/digraph%d.dot'%i, 'w') as dot:
            dot.write('digraph G{')
            dot.write('A[shape=box,label="%s"]' % pattern)
            write2dot(edge_set, dot)
            dot.write('%s[color=red,peripheries=2]' % end.id)
            dot.write('%s[color=blue]' % start.id)
            dot.write('}')
        os.system('dot2png.bat %d'%i)
        i += 1