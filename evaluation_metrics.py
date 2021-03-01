'''
Metrics for automatic MT evaluation:
- BLEU score
- chrF3 (https://www.aclweb.org/anthology/W15-3049.pdf)
'''

from sacrebleu import sentence_bleu, corpus_bleu, sentence_ter, corpus_ter, corpus_chrf, sentence_chrf
import pandas as pd


test_set_path = r"C:\Users\anton\Dropbox\Eurac_tesi\custom_MT\experiments\1 (first official experiment on gt mmt deepl baselines; test set 2000)\test-set_2000_1.txt"
reference_path = r"C:\Users\anton\Dropbox\Eurac_tesi\custom_MT\experiments\1 (first official experiment on gt mmt deepl baselines; test set 2000)\reference_2000_1.txt"
MMT_baseline_path = r"C:\Users\anton\Dropbox\Eurac_tesi\custom_MT\experiments\1 (first official experiment on gt mmt deepl baselines; test set 2000)\mmt_baseline_1.txt"
mmt_custom_path = r"C:\Users\anton\Dropbox\Eurac_tesi\custom_MT\experiments\1_Trados\test-set_2000_1.txt_it-IT_de-DE.txt"
deepl_baseline_path = r"C:\Users\anton\Dropbox\Eurac_tesi\custom_MT\experiments\deepl_baseline_1.txt"
gt_baseline_path = r"C:\Users\anton\Dropbox\Eurac_tesi\custom_MT\experiments\gt_baseline_1.txt"
report_path_export = r"C:\Users\anton\Dropbox\Eurac_tesi\custom_MT\experiments\report_experiment_1_custom_24022021.txt"


''' if test set in tab-separated format
with open(test_set_path, "r", encoding="utf-8") as test:
    testset = test.read().splitlines()
    source = []
    reference = []
    for tu in testset:
        source_s, target = tu.split("\t")
        source.append(source_s)
        reference.append(target)
'''
with open(test_set_path, "r", encoding="utf-8") as test:
    source = test.read().splitlines()
with open(reference_path, "r", encoding="utf-8") as refe:
    ref = refe.read().splitlines()
with open(MMT_baseline_path, "r", encoding="utf-8") as mmt_base:
    base_MMT = mmt_base.read().splitlines()
'''
with open(deepl_baseline_path, "r", encoding="utf-8") as deepl_base:
    base_deepl = deepl_base.read().splitlines()
with open(gt_baseline_path, "r", encoding="utf-8") as gt_base:
    base_gt = gt_base.read().splitlines()
'''

with open(mmt_custom_path, "r", encoding="utf-8") as mmt_custom:
    mmt_c = mmt_custom.read().splitlines()


# checking length of different sets
if len(source) != len(reference) != len(baseline) != len(mmt):
    print("Error: sets have not same length.")
    print("Length source: ", len(source))
    print("Length reference: ", len(reference))
    print("Length baseline: ", len(baseline))
    print("Length mmt: ", len(mmt))



# BLEU on the whole test set (baseline)
#print("BLEU MMT: ", corpus_bleu(base_MMT, [ref]).score)
#print("BLEU Google Translate: ", corpus_bleu(base_gt, [ref]).score)
#print("BLEU DeepL: ", corpus_bleu(base_deepl, [ref]).score)

# BLEU and chrF3 on whole test set (custom)
print("BLEU custom MMT: ", corpus_bleu(mmt_c, [ref]).score)
print("chrF3 custom MMT: ", corpus_chrf(mmt_c, [ref], beta=3).score)


# chrF3 on the whole test set (baseline)
#print("chrF3 MMT: ", corpus_chrf(base_MMT, [ref], beta=3).score)
#print("chrF3 Google Translate: ", corpus_chrf(base_gt, [ref], beta=3).score)
#print("chrF3 DeepL: ", corpus_chrf(base_deepl, [ref], beta=3).score)

# computing metrics on single segments
''' on baselines
columns = ["source", "reference", "mmt (baseline)", "gt (baseline)", "deepl (baseline)", "BLEU (mmt)", "chrF3 (mmt)", "BLEU (gt)", "chrF3 (gt)", "BLEU (deepl)", "chrF3 (deepl)"]
dataframe = pd.DataFrame(columns=columns)
for i in range(len(source)):
    BLEU_mmt_b = "{:.3f}".format(sentence_bleu(base_MMT[i], [ref[i]], smooth_method='exp').score)
    chrF3_mmt_b = sentence_chrf(base_MMT[i], [ref[i]]).score
    BLEU_gt = "{:.3f}".format(sentence_bleu(base_gt[i], [ref[i]], smooth_method='exp').score)
    chrF3_gt = sentence_chrf(base_gt[i], [ref[i]]).score
    BLEU_deepl = "{:.3f}".format(sentence_bleu(base_deepl[i], [ref[i]], smooth_method='exp').score)
    chrF3_deepl = sentence_chrf(base_deepl[i], [ref[i]]).score
    dataframe.loc[i] = [source[i], ref[i], base_MMT[i], base_gt[i], base_deepl[i], BLEU_mmt_b, chrF3_mmt_b, BLEU_gt, chrF3_gt, BLEU_deepl, chrF3_deepl]
'''

# on custom
columns = ["source", "reference", "MMT (baseline)", "MMT (custom)", "BLEU (baseline)", "BLEU (custom)", "BLEU (difference)", "chrF3 (baseline)", "chrF3 (custom)", "chrF3 (difference)"]
dataframe = pd.DataFrame(columns=columns)
for i in range(len(source)):
    BLEU_mmt_c = float("{:.3f}".format(sentence_bleu(mmt_c[i], [ref[i]], smooth_method='exp').score))
    BLEU_mmt_b = float("{:.3f}".format(sentence_bleu(base_MMT[i], [ref[i]], smooth_method='exp').score))
    chrF3_mmt_c = float("{:.3f}".format(sentence_chrf(mmt_c[i], [ref[i]], beta=3).score))
    chrF3_mmt_b = float("{:.3f}".format(sentence_chrf(base_MMT[i], [ref[i]]).score))
    diff_BLEU = float("{:.3f}".format(float(BLEU_mmt_c) - float(BLEU_mmt_b)))
    diff_chrF3 = float("{:.3f}".format(chrF3_mmt_c - chrF3_mmt_b))
    dataframe.loc[i] = [source[i], ref[i], base_MMT[i], mmt_c[i], BLEU_mmt_b, BLEU_mmt_c, diff_BLEU, chrF3_mmt_b, chrF3_mmt_c, diff_chrF3]

dataframe.to_csv(report_path_export, sep="\t", header=True, index=False)         # export report file as .csv

