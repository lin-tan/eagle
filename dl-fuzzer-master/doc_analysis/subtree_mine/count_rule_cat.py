from util import *


def count(rule_path):
    group = {
        'dtype': ['dtype'],
        'structure': ['tensor_t', 'structure'],
        'shape': ['shape', 'ndim'],
        'validvalue': ['enum', 'range']
}
    target = []

    rule_cat_cnt = {}
    for g in group:
        rule_cat_cnt[g] = 0

    rule = read_yaml(rule_path)
    for subtree in rule:
        for g in group:
            for subcat in group[g]:
                if subcat in rule[subtree]:
                    rule_cat_cnt[g]+=1
                    break

    print(rule_cat_cnt)


# count('./mining_data/tf/subtree_rule.yaml')
# {'dtype': 401, 'structure': 231, 'shape': 298, 'validvalue': 91}


# count('./mining_data/pt/subtree_rule.yaml')
# {'dtype': 114, 'structure': 151, 'shape': 282, 'validvalue': 22}


count('./mining_data/mx/subtree_rule.yaml')
{'dtype': 196, 'structure': 78, 'shape': 173, 'validvalue': 11}
