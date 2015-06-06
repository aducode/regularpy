#!/usr/bin/python
# -*-  coding:utf-8 -*-
__author__ = 'aducode@126.com'
import types

operator_priority = {'|': 1, '.': 2, '*': 3, '?': 3, '+': 3, '(': -1,} # 运算符优先级
operations_num_map = {'|': 2, '.': 2, '*': 1, '?': 1, '+': 1}


class Node(object):
    """
    图的节点
    """
    id = 0

    def __init__(self, in_edges=None, out_edges=None, is_end=False, label=None):
        """
        图的节点
        :param in_edges:  进入节点的边列表
        :param out_edges:  出去节点的边列表
        :param is_end:    是否是接受状态
        :param label: 节点标签
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
        self.label = label

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
            #if not value or (out_edge.value == value or not out_edge.value):
            if not value or (out_edge.value == value):
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
        elif token == '[': # 支持[]操作
            j = i+1
            while pattern[j] != ']':
                j += 1
            subtoken = pattern[i:j+1]
            i = j+1
            # []内部没有嵌套,并且优先级等同于()属于最高，所以可以直接在这里生成一个子图压入值栈
            print subtoken
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



def closure(node, pre=set()):
    """
    获取node的闭包
    """
    ret=set()
    queue = list()
    queue.append(node)
    while queue:
        current = queue.pop(0)
        if current not in ret:
            ret.add(current)
            for next, edge in current.next():
                if edge.value is None:
                    queue.append(next)
    return ret




def nfa2dfa(start, end, edge_set):
    """
    nfa转换成dfa
    :param start: nfa 开始节点
    :param end:   nfa 结束节点（唯一)
    :param edge_set: nfa边的集合
    :return start, end, edge_set  dfa的开始节点，结束节点集合(多个),边集合
    """
    if not start or not end or not edge_set:
        return None, set(), set()
    # reset Node.id
    Node.id = 1
    #
    _edge_set = set()
    _end_nodes = set()
    # get alpha set
    alpha_set = set((edge.value for edge in edge_set if edge.value is not None))
    _start_nodes = closure(start)
    # DFA start node
    tmp = [str(node.id) for node in _start_nodes]
    tmp.sort()
    _start = Node(label=' '.join(tmp), is_end=(end in _start_nodes))
    _start.nodes = _start_nodes
    if end in _start_nodes:
        _end_nodes.add(_start)
    #DFA node cache
    visited = {_start.label:_start}
    queue = list()
    queue.append(_start)
    while queue:
        _current = queue.pop(0)
        for alpha in alpha_set:
            _next_nodes = set()
            is_end = False
            for _node in _current.nodes:
                for _next_node, _edge in _node.next(alpha):
                    _next_nodes |= closure(_next_node)
            if not _next_nodes:
                continue
            for tmp in _next_nodes:
                if tmp.is_end:
                    is_end=True
                    break
            key = [str(n.id) for n in _next_nodes]
            key.sort()
            key = ' '.join(key)
            if key not in visited:              
                _n = Node(label=key, is_end=is_end)
                _n.nodes = _next_nodes
                visited[key] = _n
                queue.append(_n)
            _next = visited[key]
            if _next.is_end:
                _end_nodes.add(_next)
            Edge(value=alpha, start_node=_current, end_node=_next, edge_set=_edge_set)
    return _start, _end_nodes, _edge_set


def write2dot(edge_set, dot):
    for edge in edge_set:
        dot.write('%s->%s%s;' % (edge.start_node.id, edge.end_node.id, '[label="%s"]' % edge.value if edge.value else ''))