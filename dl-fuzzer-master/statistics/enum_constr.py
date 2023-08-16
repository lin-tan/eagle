from utils import *

constr_folder = '../doc_analysis/extract_constraint/tf/tf21_all/changed/'
#constr_folder = '../doc_analysis/extract_constraint/pytorch/pt15_all/'
#constr_folder = '../doc_analysis/extract_constraint/mxnet/mx16_all/'
doc_dtype = False
files = get_file_list(constr_folder)
# if doc_dtype:
#     csv = [['API', 'Arg', 'default', 'doc_dtype', 'enum_constr', 'descp']]
# else:
#     csv = [['API', 'Arg', 'default', 'enum_constr', 'descp']]
# for fname in files:
#     f = read_yaml(constr_folder+fname)
#     for arg in f['constraints']:
#         if 'enum' in f['constraints'][arg]:
#             if doc_dtype:
#                 csv.append([fname[:-5], arg, f['constraints'][arg].get('default', 'null'), 
#                 str(f['constraints'][arg].get('doc_dtype', 'null')),
#             str(f['constraints'][arg]['enum']), f['constraints'][arg]['descp']])
#             else:
#                 csv.append([fname[:-5], arg, f['constraints'][arg].get('default', 'null'), 
#             str(f['constraints'][arg]['enum']), f['constraints'][arg]['descp']])

# write_csv('./constr_analysis/mx_enum_constr.csv', csv)
            
csv = [['API', 'Arg', 'default', 'enum_constr', 'descp']]
frequencey = {}
for fname in files:
    f = read_yaml(constr_folder+fname)
    for arg in f['constraints']:
        if 'default' in f['constraints'][arg] and isinstance(f['constraints'][arg]['default'],str):
            default_val = f['constraints'][arg]['default']
            default_info = convert_default(default_val)
            if default_info['dtype'] == 'string':
                #if default_val != '' and default_val != ',':
                if default_val in frequencey:
                    frequencey[default_val] += 1
                else:
                    frequencey[default_val] = 1
# sort the dictionary by its value
print({k: v for k, v in sorted(frequencey.items(), key=lambda item: item[1], reverse=True)})
                #print(str(default_val) + '\t\t\t'+fname)
            

