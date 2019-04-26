#!/usr/bin/python
# -*- coding: UTF-8 -*-


class UnionFind:
    """
    并查集
    """
    def __init__(self, groups):
        self.groups = groups
        self.items = []
        for g in groups:
            self.items += list(g)
        self.items = set(self.items)
        self.parent = {}
        self.rootdict = {}  # 记住每个root下节点的数量
        for item in self.items:
            self.rootdict[item] = 1
            self.parent[item] = item

    def union(self, r1, r2):
        """
        合并2个子树
        :param r1:
        :param r2:
        :return:
        """
        rr1 = self.findroot(r1)
        rr2 = self.findroot(r2)
        cr1 = self.rootdict[rr1]
        cr2 = self.rootdict[rr2]
        if cr1 >= cr2:  # 将节点数量较小的树归并给节点数更大的树
            self.parent[rr2] = rr1
            self.rootdict.pop(rr2)
            self.rootdict[rr1] = cr1 + cr2
        else:
            self.parent[rr1] = rr2
            self.rootdict.pop(rr1)
            self.rootdict[rr2] = cr1 + cr2

    def findroot(self, r):  # 递归查找节点所在的子树的根节点
        """
        可以通过压缩路径来优化算法,即遍历路径上的每个节点直接指向根节点
        """

        # if r == self.parent[r]:
        #     return r
        if r in self.rootdict.keys():
            return r
        else:
            return self.findroot(self.parent[r])

    def create_tree(self):
        for g in self.groups:
            if len(g) < 2:
                continue
            else:
                for i in range(0, len(g) - 1):
                    if self.findroot(g[i]) != self.findroot(g[i + 1]):  # 如果处于同一个集合的节点有不同的根节点，归并之
                        self.union(g[i], g[i + 1])

    def get_tree(self):
        rs = {}
        for item in self.items:
            root = self.findroot(item)
            rs.setdefault(root, [])
            rs[root] += [item]

        ret = []
        for key in rs.keys():
            ret.append(rs[key])
        return ret


if __name__ == '__main__':
    u = UnionFind([('a', 'b', 'c'), ('b', 'd'), ('e', 'f'), ('g'), ('d', 'h')])
    # u = UnionFind([[1, 0], [0, 1], [2]])
    u.create_tree()
    print u.get_tree()
