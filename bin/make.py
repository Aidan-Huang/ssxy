#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import shutil
import re
from io import StringIO
import yaml

def _raise_err(format, *args) :
    raise ValueError(format % args)


def _load_yaml(yaml_file) :
    # print(u'load: ' + yaml_file)
    with open(yaml_file, u'rb') as f :
        return yaml.load(f.read(), Loader=yaml.FullLoader)



class Node :
    all = {}
    keys = []

    @classmethod
    def init(cls) :
        Node.all = {}
        Node.keys = []

        for node_type in [u'person', u'company'] :
            for node_id in os.listdir(u'../data/' + node_type) :
                yaml_file = u'../data/%s/%s/brief.yaml' % (node_type, node_id)
                node = Node(_load_yaml(yaml_file), node_id, node_type)
                if node_id in Node.all :
                    _raise_err(u'Node id conflict: "%s"!', node_id)

                Node.all[node_id] = node
                Node.keys.append(node_id)
        print(u'Node number: %d' % len(Node.all))


    def __init__(self, yaml, node_id, type) :
        self.id = node_id
        self.type = type
        self.name = yaml[u'name']
        if u'other_names' in yaml :  # person
            self.other_names = yaml[u'other_names']
        if u'sex' in yaml :  # person
            self.sex = yaml[u'sex']
        if u'full_name' in yaml :  # company
            self.full_name = yaml[u'full_name']
        self.birth = yaml[u'birth']
        self.death = yaml[u'death']
        self.desc = yaml[u'desc']
        if u'cause_of_death' in yaml:
            self.cause_of_death = yaml[u'cause_of_death']
        else:
            self.cause_of_death = None
        self.links = yaml[u'links']



class Relation :
    all = {}
    keys = []

    single_relation = True

    @classmethod
    def init(cls) :
        for family_id in os.listdir(u'../data/family/') :
            family_id = family_id.replace(u'.yaml', u'')
            yaml_file = u'../data/family/%s.yaml' % (family_id,)
            if family_id not in Node.all :
                _raise_err(u'Invalid family name: "%s"!', family_id)

            yaml = _load_yaml(yaml_file)
            if yaml[u'relations']:
                for lst in yaml[u'relations'] :
                    relation = Relation(lst)

                    Relation.all[relation.name] = relation
                    Relation.keys.append(relation.name)
                    # print(u'Relation name: %s' % relation.name)

        print(u'Relation number: %d' % len(Relation.all))


    def __init__(self, lst) :
        self.node_from = lst[0]
        self.node_to = lst[1]
        self.desc = lst[2]
        self.name = self.node_from + u'->' + self.node_to
        self.equal = False

        if self.name in Relation.all :
            _raise_err(u'Relation name conflict: "%s"!', self.name)
        if self.node_from not in Node.all :
            _raise_err(u'Invalid relation "from" attr: "%s"!', self.node_from)
        if self.node_to not in Node.all :
            _raise_err(u'Invalid relation "to" attr": "%s"!', self.node_to)

        if Relation.single_relation:
            if self.node_to + u'->' + self.node_from in Relation.all:
                self.equal = True


    # def is_equal_relation(self, relation: Relation) :
    #
    #     if self.node_from == relation.node_to:
    #         if self.node_to == relation.node_from:
    #             return True
    #
    #     return False

class Family :
    all = {}
    keys = []

    @classmethod
    def init(cls) :
        for family_id in os.listdir(u'../data/family/') :
            family_id = family_id.replace(u'.yaml', u'')
            yaml_file = u'../data/family/%s.yaml' % (family_id,)
            if family_id not in Node.all :
                _raise_err(u'Invalid family name: "%s"!', family_id)

            family = Family(_load_yaml(yaml_file))
            Family.all[family_id] = family
            Family.keys.append(family_id)
        print(u'Family number: %d' % len(Family.all))


    def __init__(self, yaml) :
        self.name = yaml[u'name']
        self.inner = yaml[u'inner']
        self.inner.reverse()
        self.outer = yaml[u'outer']
        self.outer.reverse()
        self.members = [self.name] + self.inner + self.outer

        for name in self.members :
            if name not in Node.all :
                _raise_err(u'Invalid family members: "%s"!', name)



class Graph :
    def __init__(self, yaml) :
        self._name = yaml[u'name']
        self._families = yaml[u'families']
        self._families.reverse()
        self._nodes = []
        self._relations = {}
        self._relations_keys = []

        for f in self._families :
            family = Family.all[f]
            for n in family.members :
                if n not in self._nodes :
                    self._nodes.append(n)
            for r in Relation.keys :
                relation = Relation.all[r]
                if relation.node_from in family.members \
                    and relation.node_to in family.members \
                    and r not in self._relations :
                    # self._relations.append(r)
                    self._relations[relation.name] = relation
                    self._relations_keys.append(relation.name)

            if Relation.single_relation:
                for n in self._nodes:
                    for r in self._relations_keys:
                        relation = self._relations[r]
                        equal_name = relation.node_to + u'->' + relation.node_from
                        if relation.node_from == n:
                            if equal_name in self._relations_keys:
                                self._relations_keys.remove(equal_name)
                                del self._relations[equal_name]




    def dump(self) :
        output = StringIO()

        for n in self._nodes :
            output.write(self._dot_node(n))
        output.write(u'\n')

        for r in self._relations :
            output.write(self._dot_relation(r))
        output.write(u'\n')

        if len(self._families) > 1 :
            for f in self._families :
                output.write(self._dot_sub_graph(f))

        template = u'''
digraph
{
\trankdir = "LR";
\tranksep = 0.5;
\tlabel = "%s";
\tlabelloc = "t";
\tfontsize = "24";
\tfontname = "SimHei";

\tgraph [style="filled", color="lightgrey"];
\tnode [fontname="SimSun"];
\tedge [fontname="SimSun"];

%s
}
'''
        return template % (self._name, output.getvalue())


    def _node_color(self, node) :
        if u'company' == node.type :
            return u'gray'
        elif re.match(u'.*(帝|谥).*', str(node.other_names)):
            return (u'red' if u'M'==node.sex else u'darkorange')
        else :
            return (u'blue' if u'M'==node.sex else u'darkgreen')

    def _other_names(self, node) :
        other_names = ''
        if u'person'==node.type and node.other_names :
            other_names = u', '.join([u'%s:%s' % (k,v) for k,v in node.other_names.items()])
        elif u'company'==node.type and node.full_name :
            other_names = node.full_name
        return u'<tr><td>(%s)</td></tr>' % (other_names,) if other_names else ''

    def _dot_node(self, node_id) :
        node = Node.all[node_id]
        template = u'\t%s [shape="%s", color="%s", ' \
                    u'label=<<table border="0" cellborder="0">' \
                    u'<tr><td>%s%s</td></tr>' \
                    u'%s' \
                    u'<tr><td>%s</td></tr>' \
                    u'<tr><td>%s</td></tr></table>>];\n'

        # print("node_id=" + node_id)
        portrait = u'../data/person/%s/portrait.png' % (node_id,)
        # print("portrait=" + portrait)
        portrait = u'<img src="%s"/>' % (portrait,) if os.path.exists(portrait) else ''


        # 出生日期，年龄
        # 出生日期是公元前，出生日期的“前”去掉，数值取反
        # 死亡日期是公元前，死亡日期的“前”去掉，数值取反
        # 年龄等于死亡日期减去出生日期

        birth_age = u''

        try:
            if node.birth != u'N/A':
                iBirth = 0
                iDeath = 0
                age = 0
                birth = str(node.birth)
                death = str(node.death)

                birth_age = u'[' + str(node.birth)

                if(birth.startswith('前')):
                    iBirth = 0 - int(birth.strip("前"))
                else:
                    iBirth = int(birth)

                # print("iBirth=" + str(iBirth))

                if (death != u'N/A'):
                    if (death.startswith('前')):
                        iDeath = 0 - int(death.strip("前"))
                    else:
                        iDeath = int(death)

                    age = iDeath - iBirth

                # print("iDeath=" + str(iDeath))

                # print("age=" + str(age))

                if age != 0:
                    birth_age = birth_age + u'生,' + str(age) + u'岁]'
                else:
                    birth_age = birth_age + u'生]'
        except Exception as err:
            print(u'error!\n%s' % err)

        # print("node.birth=" + str(node.birth))
        # print("node.death=" + str(node.death))
        # print("birth_age=" + birth_age)

        desc = node.desc.replace(u'\n', u'<br/>')
        if node.cause_of_death != None and node.cause_of_death != '':
            # print(node.cause_of_death)
            desc = desc + "<font color = 'red'>" + node.cause_of_death.replace(u'\n', u'<br/>') + "</font>"
            # print(desc)

        return template % (node.id,
                           u'box' if u'person'==node.type else u'ellipse',
                           self._node_color(node),
                           node.name,
                           # (u'' if node.birth == u'N/A' else u' [%s'% node.birth + (u']' if node.death == u'N/A' else u',%s]'% str(int(node.death) - int(node.birth)))),
                           birth_age,
                           self._other_names(node),
                           portrait,
                           desc)


    def _dot_relation(self, name) :
        relation = Relation.all[name]
        template = u'''\t%s -> %s [label="%s", style=%s, color="%s"];\n'''

        if re.match(u'^夫|妻$', relation.desc) :
            style = u'bold'
        elif re.match(u'^父|母$', relation.desc) :
            style = u'solid'
        elif re.match(u'^(独|长|次|幼|三|四|五|六|七|八|九)?(子|女)$', relation.desc) :
            style = u'solid'
        elif re.match(u'^.*?(兄|弟|姐|妹)$', relation.desc) :
            style = u'dashed'
        else :
            style = u'dotted'

        return template % (relation.node_from, relation.node_to,
                           relation.desc, style,
                           self._node_color(Node.all[relation.node_to]))


    def _dot_sub_graph(self, name) :
        node = Node.all[name]
        if node.type == u'company' :
            return self._dot_node(name)

        family = Family.all[name]
        template = u'''
\tsubgraph "cluster_%s"
\t{
\t\tfontsize="18";
\t\tlabel="%s家族";
\t\t%s;
\t}
'''
        return template % (family.name, family.name,
                           u';'.join([name]+family.inner))



class Builder :

    output_dir = u'/download'

    def __init__(self) :
        Node.init()
        Relation.init()
        Family.init()

    def _mkdir(self, name) :
        if os.path.exists(name) :
            shutil.rmtree(name)
        os.mkdir(name)

    def _exec(self, cmd) :
        print(cmd)
        return os.system(cmd.encode(u'utf-8'))

    def output(self, name, graph, file_type):

        dot_file = u'..' + self.output_dir + '/dot/%s.dot' % (name,)
        output_file = u'..' + self.output_dir + '/%s/%s.%s' % (file_type, name, file_type)

        with open(dot_file, u'wb') as f:
            f.write(Graph(graph).dump().encode(u'utf-8'))

        cmd = u'dot "%s" -T %s -o "%s"' % (dot_file, file_type, output_file)
        # print('cmd: ' + cmd)
        if os.system(cmd) != 0:
            _raise_err(u'Make "%s" failed!', dot_file)

    def do(self, file_type, files, graph_range) :
        os.chdir(u'..' + self.output_dir + '/')
        self._mkdir(u'dot')
        self._mkdir(file_type)

        for i in graph_range:
            filename = u'../data/graph' + str(i) + '.yaml'

            if len(files) > 0:
                for graph in _load_yaml(filename):
                    name = u'%s' % (graph[u'name'])
                    if name in files:
                        self.output(name, graph, file_type)
            else:
                for graph in _load_yaml(filename):
                    name = u'%s' % (graph[u'name'])
                    self.output(name, graph, file_type)
        return 0


if '__main__' == __name__ :
    try :
        if len(sys.argv) != 2 :
            print(u'''Usage:\n%s file_type
(file_type is pdf or jpg or png or gif or tiff or svg or ps)''' % sys.argv[0])
            sys.exit(0)

        Relation.single_relation = True
        Builder.output_dir = u'/tmp'
        graph_range = range(2, 3)

        files = []
        # files = ['01德行031','01德行032','01德行033','01德行034','01德行035']
        # files = ['04文学104']

        sys.exit(Builder().do(sys.argv[1],files,graph_range))

    except Exception as err :
        print(u'Make abort!\n%s' % err)
        sys.exit(1)
