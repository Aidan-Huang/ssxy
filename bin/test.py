#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import shutil
import re
from io import StringIO
import yaml

class Relation :
    all = {}
    keys = []

    single_relation = True

    # @classmethod
    # def init(cls) :
    #     for family_id in os.listdir(u'../data/family/') :
    #         family_id = family_id.replace(u'.yaml', u'')
    #         yaml_file = u'../data/family/%s.yaml' % (family_id,)
    #         if family_id not in Node.all :
    #             _raise_err(u'Invalid family name: "%s"!', family_id)
    #
    #         yaml = _load_yaml(yaml_file)
    #         if yaml[u'relations']:
    #             for lst in yaml[u'relations'] :
    #                 relation = Relation(lst)
    #
    #                 find_equal_relation = False
    #                 # 判断是否仅添加单向关系
    #                 # 按起点关系在之前的关系列表中查终点关系，如果找到判断终点是否等于起点，如果也找到了，这条关系舍弃
    #                 if Relation.single_relation:
    #                     for pre_relation in Relation.all.keys():
    #                         if relation.is_equal_relation(Relation.all[pre_relation]):
    #                             find_equal_relation = True
    #
    #                 if find_equal_relation == False:
    #                     Relation.all[relation.name] = relation
    #                     Relation.keys.append(relation.name)
    #
    #                 print(u'Relation name: %s' % relation.name)
    #     print(u'Relation number: %d' % len(Relation.all))


    def __init__(self, lst) :
        self.node_from = lst[0]
        self.node_to = lst[1]
        self.desc = lst[2]
        self.name = self.node_from + u'->' + self.node_to

        if self.name in Relation.all :
            print(u'Relation name conflict:', self.name)
        # if self.node_from not in Node.all :
        #     _raise_err(u'Invalid relation "from" attr: "%s"!', self.node_from)
        # if self.node_to not in Node.all :
        #     _raise_err(u'Invalid relation "to" attr": "%s"!', self.node_to)

    def is_equal_relation(self, relation: Relation):

        if self.node_from == relation.node_to:
            if self.node_to == relation.node_from:
                return True

        return False

if '__main__' == __name__ :

    lst1 = ['王濛','王恭', '孙']
    lst2 = ['王恭','王濛1', '祖父']

    relation1 = Relation(lst1)
    Relation.all[relation1.name] = relation1
    Relation.keys.append(relation1.name)

    relation2 = Relation(lst2)
    Relation.all[relation2.name] = relation2
    Relation.keys.append(relation2.name)

    #
    is_equal_relation = relation1.is_equal_relation(relation2)
    #
    print("relaiton equal is:" + str(is_equal_relation))

    # name = 'graph'
    #
    # for i in range(5, 6):  # range()请看本章第五部分
    #     newname = name + str(i) + '.yaml'
    #     print(newname)

    # files = ['test1','test2']
    #
    # name = 'test2'
    #
    # if name in files:
    #     print(name)
    #
    # if len(files) != 0:
    #     for file in files:
    #         print(file)

