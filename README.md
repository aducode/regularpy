# regular
自己动手实现一个简单的正则表达式引擎

目前进度：

1.直接生成DFA
	* 根据正则表达式构建出抽象语法树
	* 计算节点的nullable firstpos
	* 计算节点lastpost followpos
	* 进行match group运算，但是group只支持最小匹配
	* 生成的DFA只支持 | * CAT ? +基本正则语法
2.生成NFA转换DFA
	* 构造NFA，支持[A-Z], {m,n}正则语法
	* NFA支持group
	* NFA转换成DFA(group捕获信息未转换)

