'''
Metrics for automatic MT quality evaluation:
- BLEU score
- chrF3 (https://www.aclweb.org/anthology/W15-3049.pdf)
- hLEPOR

BLEU and chrF3 are computed using SACREBLEU (Post 2018)

Comparing output of baseline + 2 different adapted systems (I and II)

Scores are computed at the corpus level and at the segment level.
A CSV report file is created for further analyses at the segment level.
'''

from sacrebleu import sentence_bleu, corpus_bleu, corpus_chrf, sentence_chrf
import pandas as pd
import regex as re
from hlepor import single_hlepor_score, hlepor_score


test_set_path = r""
reference_path = r""
MMT_baseline_path = r""
mmt_custom_path_I = r""
mmt_custom_path_II = r""

report_path_export = r""


with open(test_set_path, "r", encoding="utf-8") as test:
    source = test.read().splitlines()
with open(reference_path, "r", encoding="utf-8") as refe:
    ref = refe.read().splitlines()
with open(MMT_baseline_path, "r", encoding="utf-8") as mmt_base:
    base_MMT = mmt_base.read().splitlines()
with open(mmt_custom_path_I, "r", encoding="utf-8") as mmt_custom:
    mmt_c_I = mmt_custom.read().splitlines()
with open(mmt_custom_path_II, "r", encoding="utf-8") as mmt_custom_II:
    mmt_c_II = mmt_custom_II.read().splitlines()


# checking length of different sets
if len(source) != len(ref) != len(base_MMT) != len(mmt_c_I) != len(mmt_c_II):
    print("Error: sets have not same length.")
    print("Length source: ", len(source))
    print("Length reference: ", len(ref))
    print("Length baseline: ", len(base_MMT))
    print("Length MMT I: ", len(mmt_c_I))
    print("Length MMT II: ", len(mmt_c_II))


# Metrics on whole test set (custom)

print("BLEU custom MMT_I: ", corpus_bleu(mmt_c_I, [ref]).score)
print("chrF3 custom MMT_I: ", corpus_chrf(mmt_c_I, [ref], beta=3).score)
print("hLEPOR custom MMT_I: ", hlepor_score(ref, mmt_c_I))

print("BLEU custom MMT_II: ", corpus_bleu(mmt_c_II, [ref]).score)
print("chrF3 custom MMT_II: ", corpus_chrf(mmt_c_II, [ref], beta=3).score)
print("hLEPOR custom MMT_II: ", hlepor_score(ref, mmt_c_II))



columns = ["source", "reference", "MMT (baseline)", "MMT (custom)_I", "MMT (custom)_II", "BLEU (baseline)",
           "BLEU (custom)_I", "BLEU (custom)_II", "BLEU (difference baseline/custom_I)",
           "BLEU (difference baseline/custom_II)", "BLEU (difference custom I/custom II)", "chrF3 (baseline)",
           "chrF3 (custom)_I", "chrF3 (custom)_II", "chrF3 (difference baseline/custom_I)",
           "chrF3 (difference baseline/custom_II)", "chrF3 (difference custom I/custom II)", "hLEPOR (baseline)",
           "hLEPOR (custom)_I", "hLEPOR (custom)_II", "hLEPOR (difference baseline/custom I)",
           "hLEPOR (difference baseline/custom II)", "hLEPOR (difference custom I/II)"]    # 23 columns

dataframe = pd.DataFrame(columns=columns)
for i in range(len(source)):
    BLEU_mmt_b = float("{:.3f}".format(sentence_bleu(base_MMT[i], [ref[i]], smooth_method='exp').score))
    BLEU_mmt_c_I = float("{:.3f}".format(sentence_bleu(mmt_c_I[i], [ref[i]], smooth_method='exp').score))
    BLEU_mmt_c_II = float("{:.3f}".format(sentence_bleu(mmt_c_II[i], [ref[i]], smooth_method='exp').score))
    diff_BLEU_I = float("{:.3f}".format(float(BLEU_mmt_c_I) - float(BLEU_mmt_b)))
    diff_BLEU_II = float("{:.3f}".format(float(BLEU_mmt_c_II) - float(BLEU_mmt_b)))
    diff_BLEU_I_II = float("{:.3f}".format(float(BLEU_mmt_c_II) - float(BLEU_mmt_c_I)))
    chrF3_mmt_b = float("{:.3f}".format(sentence_chrf(base_MMT[i], [ref[i]]).score))
    chrF3_mmt_c_I = float("{:.3f}".format(sentence_chrf(mmt_c_I[i], [ref[i]], beta=3).score))
    chrF3_mmt_c_II = float("{:.3f}".format(sentence_chrf(mmt_c_II[i], [ref[i]], beta=3).score))
    diff_chrF3_I = float("{:.3f}".format(chrF3_mmt_c_I - chrF3_mmt_b))
    diff_chrF3_II = float("{:.3f}".format(chrF3_mmt_c_II - chrF3_mmt_b))
    diff_chrF3_I_II = float("{:.3f}".format(chrF3_mmt_c_II - chrF3_mmt_c_I))
    hlepor_mmt_b = float("{:.3f}".format(single_hlepor_score(ref[i], base_MMT[i])))
    hlepor_mmt_c_I = float("{:.3f}".format(single_hlepor_score(ref[i], mmt_c_I[i])))
    hlepor_mmt_c_II = float("{:.3f}".format(single_hlepor_score(ref[i], mmt_c_II[i])))
    diff_hlepor_I = float("{:.3f}".format(hlepor_mmt_c_I - hlepor_mmt_b))
    diff_hlepor_II = float("{:.3f}".format(hlepor_mmt_c_II - hlepor_mmt_b))
    diff_hlepor_I_II = float("{:.3f}".format(hlepor_mmt_c_II - hlepor_mmt_c_I))
    dataframe.loc[i] = [source[i], ref[i], base_MMT[i], mmt_c_I[i], mmt_c_II[i], BLEU_mmt_b, BLEU_mmt_c_I,
                        BLEU_mmt_c_II, diff_BLEU_I, diff_BLEU_II, diff_BLEU_I_II, chrF3_mmt_b, chrF3_mmt_c_I,
                        chrF3_mmt_c_II, diff_chrF3_I, diff_chrF3_II, diff_chrF3_I_II, hlepor_mmt_b, hlepor_mmt_c_I,
                        hlepor_mmt_c_II, diff_hlepor_I, diff_hlepor_II, diff_hlepor_I_II]

dataframe.to_csv(report_path_export, sep="\t", header=True, index=False)         # export report file as .csv

with open(report_path_export, "r", encoding="utf-8") as report:
    report_ = report.read()

#  applying regex to localize float with dot  float with comma for Excel
pattern = re.compile(r'(?<=.+)(\t-?\d\d?\d?)\.(\d{1,3}(\t|\r\n|\n))')
sub = re.sub(pattern, r"\1,\2", report_)
sub2 = re.sub(pattern, r"\1,\2", sub)
with open(report_path_export, "w", encoding="utf-8") as report_out:
    report_out.write(sub2)
