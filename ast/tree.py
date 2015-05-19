#!/usr/bin/python
# -*- coding:utf-8 -*-
import types
__author__ = 'aducode@126.com'


class Node(object):
    """
    AST节点
    """
    operator_priority = {'|': 1, '.': 2, '*': 3, '(': -1, } # 运算符优先级
    operations_num_map = {'|': 2, '.': 2, '*': 1, }

    def __init__(self, value=None, children=None):
        self.value = value
        self.children = children
        self.followpos = set()

    def __str__(self):
        return '%s:%s' % (self.value, self.children)

    @classmethod
    def new(cls, op, stack):
        children = []
        for i in xrange(cls.operations_num(op)):
            children.append(stack.pop())
        if op == '*':
            return StarNode(op, children)
        elif op == '|':
            return OrNode(op, children)
        elif op == '.':
            return CatNode(op, children)

    @staticmethod
    def leaf(value):
        return Leaf(value)

    @classmethod
    def priority(cls, op):
        return cls.operator_priority.get(op, -1)

    @classmethod
    def operations_num(cls, op):
        return cls.operations_num_map.get(op, 0)


class CatNode(Node):
    """
    Cat 操作符节点
    """
    def __init__(self, op, children):
        super(CatNode, self).__init__(op, children)
        assert len(children) == 2
        self.nullable = self.children[0].nullable and self.children[1].nullable
        if self.left.nullable:
            self.firstpos = self.left.firstpos | self.right.firstpos
        else:
            self.firstpos = self.left.firstpos
        if self.right.nullable:
            self.lastpos = self.left.lastpos | self.right.lastpos
        else:
            self.lastpos = self.right.lastpos

        for n in self.left.lastpos:
            n.followpos.update(self.right.firstpos)

    @property
    def left(self):
        """
        左节点
        """
        return self.children[1]

    @property
    def right(self):
        """
        右节点
        """
        return self.children[0]


class OrNode(Node):
    """
    Or 操作符节点
    """
    def __init__(self, op, children):
        super(OrNode, self).__init__(op, children)
        assert len(children) == 2
        self.nullable = self.left.nullable or self.right.nullable
        self.firstpos = self.left.firstpos | self.right.firstpos
        self.lastpos = self.left.lastpos | self.right.lastpos

    @property
    def left(self):
        """
        左节点
        """
        return self.children[1]

    @property
    def right(self):
        """
        右节点
        """
        return self.children[0]

class StarNode(Node):
    """
    Start 操作节点
    """
    def __init__(self, op, children):
        super(StarNode, self).__init__(op, children)
        self.nullable = True
        self.firstpos = self.child.firstpos
        self.lastpos = self.child.lastpos
        for n in self.child.lastpos:
            n.followpos.update(self.child.firstpos)

    @property
    def child(self):
        """
        子节点
        """
        return self.children[0]

class Leaf(Node):
    """
    叶子节点，保存NFA的节点
    """
    def __init__(self, value):
        super(Leaf, self).__init__(value)
        self.nullable = False
        self.firstpos = set([self])
        self.lastpos = set([self])

    def __str__(self):
        return self.value


class EmptyNode(Node):
    """
    空节点
    """
    def __init__(self):
        super(EmptyNode, self).__init__()
        self.nullable = True
        self.firstpos = set()
        self.lastpos = set()


def build_ast(token):
    """
    根据输入的正则表达式构建抽象语法树
    :param token:  正则表达式
    :return:       AST root
    """
    if not isinstance(token, types.StringTypes):
        return
    try:
        value_stack = []  # 字符栈
        operator_stack = [] # 操作符栈
        is_operator = False
        first = True
        for t in token:
            if t == '|' or t == '*':
                # 操作符
                op = t
                if op != '*':
                    is_operator = True
                else:
                    is_operator = False
                while operator_stack and Node.priority(operator_stack[-1]) >= Node.priority(op):
                    # 操作符栈栈顶优先级高于当前操作符
                    # 需要先计算
                    _op = operator_stack.pop()
                    value_stack.append(Node.new(_op, value_stack))
                operator_stack.append(op)
            elif t == '(':
                # 左括号
                if not is_operator and not first:
                    operator_stack.append('.')
                operator_stack.append('(')
                first = True
            elif t == ')':
                # 右括号
                while operator_stack[-1] != '(':
                    op = operator_stack.pop()
                    value_stack.append(Node.new(op, value_stack))
                if operator_stack[-1] == '(':
                    operator_stack.pop()
            else:
                # 字符
                if not is_operator and not first:
                    # 说明前一个t也是一个字符串，两个字符串之间是cat操作(用 . 代替)
                    op = '.'
                    while operator_stack and Node.priority(operator_stack[-1]) >= Node.priority(op):
                        _op = operator_stack.pop()
                        value_stack.append(Node.new(_op, value_stack))
                    operator_stack.append(op)
                    is_operator = True
                # 说明前一个是一个操作符
                value = t
                is_operator = False
                value_stack.append(Node.leaf(value))  # 压站
                first = False
        while operator_stack:
            op = operator_stack.pop()
            value_stack.append(Node.new(op, value_stack))
        return value_stack[0]
    except (IndexError, KeyError, ):
        raise RuntimeError("Parse [%s] fail!" % token)


def visit_ast(node, indent=0):
    print '\t'*indent, node, '--->', node.value, ':nullable:', node.nullable, ':firstpos:', node.firstpos, ':lastpos', node.lastpos, ':followpos:', node.followpos
    if node.children:
        for child in node.children:
            visit_ast(child, indent+1)


if __name__ == '__main__':
    re = raw_input("please input regular text:\n")
    while re != '/quit':
        if re.startswith('/'):
            re = raw_input("can't contain '/', input another regular text:\n")
            continue
        root = build_ast(re)
        print '-' * 20
        visit_ast(root)
        re = raw_input("please input regular text:\n")
    print 'Bye~~'


