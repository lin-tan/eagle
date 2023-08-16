import numpy as np
from map_bug_id_to_input_id import mapper

bug_results = {
    'tensorflow': 'unique_bugs_tf.tsv',
    'pytorch': 'unique_bugs_pt.tsv',
    'mxnet': 'unique_bugs_mx.tsv'
}
TOTAL_INPUT = 1000

ok_ratio = np.arange(0, 101, 10)
excpt_ratio = 100 - ok_ratio
ratios = zip(ok_ratio, excpt_ratio)

target_libs = ['tensorflow', 'pytorch', 'mxnet']


class BugResult:
    def __init__(self, lib, total, caught, uncaught, eo_caught, ee_caught):
        self.lib = lib
        self.total = total
        self.caught = caught
        self.uncaught = uncaught
        self.eo_caught = eo_caught
        self.ee_caught = ee_caught

    def uncaught_bug_ids(self):
        return ';'.join([b.id for b in self.uncaught])


with open('ratio_analysis_result.csv', 'w') as f:
    for i, r in enumerate(ratios):
        print('+++ trying ok:except = %d%%:%d%% +++' % r)
        assert len(r) == 2
        ok_ratio = r[0]/100
        excpt_ratio = r[1]/100

        all_lib_result = {}
        for lib in target_libs:
            total_bugs, caught_bugs, uncaught_bugs, eo_caught, ee_caught = mapper(bug_results[lib], lib, ok_ratio, excpt_ratio, TOTAL_INPUT)
            res = BugResult(lib, total_bugs, caught_bugs, uncaught_bugs, eo_caught, ee_caught)
            all_lib_result[lib] = res

        text = '%s vs. %s' % (r[0], r[1])
        text_rest = ''
        for lib in target_libs:
            res = all_lib_result[lib]
            res_line = '%s,%s,%s,%s,%s' % (res.total, res.caught, res.uncaught_bug_ids(), len(res.eo_caught), len(res.ee_caught))
            text_rest = ','.join([text_rest, res_line])
        line = text + text_rest
        f.write(line + '\n')
