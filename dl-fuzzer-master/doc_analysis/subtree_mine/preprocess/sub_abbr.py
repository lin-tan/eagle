# Deprecated

import sys
sys.path.insert(0,'..')

from util import * 
import argparse

abbrs_expand = {"don't": "do not", "Don't": "do not", "doesn't": "does not", "Doesn't": "does not",
        "didn't": "did not",
        "couldn't": "could not", "Couldn't": "could not", "can't": "can not", "Can't": "can not",
        "ca n't": "can not", "Ca n't": "can not",
        "shouldn't": "should not", "Shouldn't": "should not", "should've": "should have",
        "mightn't": "might not", "mustn't": "must not", "Mustn't": "must not", "needn't": "need not",
        "haven't": "have not", "hadn't": "had not", "hasn't": "has not",
        "you'd": "you should", "You'd": "you should", "you're": "you are", "You're": "you're",
        "it's": "it is", "It's": "it is", "won't": "will not", "wo n't": "will not",
        "isn't": "is not", "Isn't": "is not", "aren't": "are not", "Aren't": "are not"
        }


abbrs = {" n't": " not", "'s": "", "'d": ""}
normalize = {r'\ban\b': 'a'}
remove = [r'\(optional\)', r'\(default\)' ]

def sub_abbr(src_text):
    normalized_text = src_text
    for abbr in abbrs_expand:
        if re.search(abbr, normalized_text):
            normalized_text = re.sub(abbr, abbrs_expand[abbr], normalized_text, flags=re.IGNORECASE)
    # to check if needed
    
    for abbr in abbrs:
        normalized_text = re.sub(abbr, abbrs[abbr], normalized_text, flags=re.IGNORECASE)

    for norm in normalize:
        normalized_text = re.sub(norm, normalize[norm], normalized_text, flags=re.IGNORECASE)

    for rem in remove:
        normalized_text = re.sub(rem, ' ', normalized_text, flags=re.IGNORECASE)
    return remove_extra_space(normalized_text)
def test():
    test_case = {
        "An `int`. The length of the dimension `axis`.": "a `int`. The length of the dimension `axis`.",
        'For N=1 it can be either "NWC" (default) or "NCW", for N=2 it can be either "NHWC" (default) or "NCHW" and for N=3 either "NDHWC" (default) or "NCDHW".':\
        'For N=1 it can be either "NWC" or "NCW", for N=2 it can be either "NHWC" or "NCHW" and for N=3 either "NDHWC" or "NCDHW".'
    }
    for s in test_case:
        normalized = sub_abbr(s)
        if normalized==test_case[s]:
            print('PASS')
        else:
            print('FAIL')
            print('Original text: %s'% s)
            print('Normalized text: %s'% normalized)


if __name__ == '__main__':
    test()