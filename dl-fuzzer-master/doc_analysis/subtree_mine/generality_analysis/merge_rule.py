
import sys
sys.path.insert(0,'../')
from util import *


# def main(rule_path1, rule_pa
# th2, save_to):
#     def merge_rules(r1, r2):
#         ret = r1.copy()
#         for cat in r2:
#             if cat in r1:
#                 ret[cat] = list(set(r1[cat]+r2[cat]))
#             else:
#                 ret[cat] = r2[cat]
#         return ret
    
#     rule1 = read_yaml(rule_path1)
#     rule2 = read_yaml(rule_path2)
#     all_rule = rule1.copy()
#     for subtree in rule2:
#         if subtree in rule1:
#             all_rule[subtree] = merge_rules(rule1[subtree], rule2[subtree])
#         else:
#             all_rule[subtree] = rule2[subtree]

#     print('combine {} and {} to form {} rules'.format(len(list(rule1.keys())), len(list(rule2.keys())), len(list(all_rule.keys()))))
#     save_yaml(save_to, all_rule)

# # main('./mining_data/tf/subtree_rule.yaml', './mining_data/pt/subtree_rule.yaml', './mining_data/general/tf_pt_rule.yaml')
# # main('./mining_data/tf/subtree_rule.yaml', './mining_data/mx/subtree_rule.yaml', './mining_data/general/tf_mx_rule.yaml')
# main('./mining_data/pt/subtree_rule.yaml', './mining_data/mx/subtree_rule.yaml', './mining_data/general/pt_mx_rule.yaml')






def main(rule_path1, rule_path2, rule_path3, save_to):
    def merge_rules(r1, r2):
        ret = r1.copy()
        for cat in r2:
            if cat in r1:
                ret[cat] = list(set(r1[cat]+r2[cat]))
            else:
                ret[cat] = r2[cat]
        return ret
    
    rule1 = read_yaml(rule_path1)
    rule2 = read_yaml(rule_path2)
    rule3 = read_yaml(rule_path3)
    all_rule = rule1.copy()
    for subtree in rule2:
        if subtree in rule1:
            all_rule[subtree] = merge_rules(rule1[subtree], rule2[subtree])
        else:
            all_rule[subtree] = rule2[subtree]

    for subtree in rule3:
        if subtree in all_rule:
            all_rule[subtree] = merge_rules(all_rule[subtree], rule3[subtree])
        else:
            all_rule[subtree] = rule3[subtree]

    print('combine {}, {} and {} to form {} rules'.format(len(list(rule1.keys())), len(list(rule2.keys())), len(list(rule3.keys())), len(list(all_rule.keys()))))
    save_yaml(save_to, all_rule)

# main('./mining_data/tf/subtree_rule.yaml', './mining_data/pt/subtree_rule.yaml', './mining_data/general/tf_pt_rule.yaml')
# main('./mining_data/tf/subtree_rule.yaml', './mining_data/mx/subtree_rule.yaml', './mining_data/general/tf_mx_rule.yaml')
main('../mining_data/pt/subtree_rule.yaml', '../mining_data/mx/subtree_rule.yaml', '../mining_data/tf/subtree_rule.yaml', '../mining_data/general/all_rule.yaml')

# combine 398, 275 and 659 to form 1262 rules
