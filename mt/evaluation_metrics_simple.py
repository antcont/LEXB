'''
Metrics for automatic MT evaluation:
- BLEU score
- chrF3 (https://www.aclweb.org/anthology/W15-3049.pdf)
- hLEPOR

BLEU and chrF3 are computed using SACREBLEU (Post 2018)

Corpus-level scores for one system's output.
'''

from sacrebleu import sentence_bleu, corpus_bleu, sentence_ter, corpus_ter, corpus_chrf, sentence_chrf
import pandas as pd
from hlepor import single_hlepor_score, hlepor_score



test_set_path = r""
reference_path = r""
MMT_custom_path = r""


with open(test_set_path, "r", encoding="utf-8") as test:
    source = test.read().splitlines()
with open(reference_path, "r", encoding="utf-8") as refe:
    ref = refe.read().splitlines()
with open(MMT_custom_path, "r", encoding="utf-8") as mmt_base:
    custom_MMT = mmt_base.read().splitlines()



# BLEU, chrF3, hLEPOR on the whole test set
print("BLEU custom MMT: ", corpus_bleu(custom_MMT, [ref]).score)
print("chrF3 custom MMT: ", corpus_chrf(custom_MMT, [ref], beta=3).score)
print("hLEPOR custom MMT_I: ", hlepor_score(ref, mmt_c_I))




