'''
Version for comparino custom CoA and custom DeF for PaCor2021.

Metrics for automatic MT evaluation:
- BLEU score
- chrF3 (https://www.aclweb.org/anthology/W15-3049.pdf)
'''

from sacrebleu import sentence_bleu, corpus_bleu, corpus_chrf, sentence_chrf
import pandas as pd
import regex as re


test_set_path = r"C:\Users\anton\Documents\Documenti importanti\SSLMIT FORLI M.A. SPECIALIZED TRANSLATION 2019-2021\tesi\EXPERIMENTS\1 (first official experiment on gt mmt deepl baselines; test set 2000)\test-set_2000_1.txt"
reference_path = r"C:\Users\anton\Documents\Documenti importanti\SSLMIT FORLI M.A. SPECIALIZED TRANSLATION 2019-2021\tesi\EXPERIMENTS\1 (first official experiment on gt mmt deepl baselines; test set 2000)\reference_2000_1.txt"
MMT_baseline_path = r"C:\Users\anton\Documents\Documenti importanti\SSLMIT FORLI M.A. SPECIALIZED TRANSLATION 2019-2021\tesi\EXPERIMENTS\1 (first official experiment on gt mmt deepl baselines; test set 2000)\mmt_baseline_1.txt"
mmt_custom_path_CoA = r"C:\Users\anton\Documents\Documenti importanti\SSLMIT FORLI M.A. SPECIALIZED TRANSLATION 2019-2021\tesi\EXPERIMENTS\1 (first official experiment on gt mmt deepl baselines; test set 2000)\1_Trados\test-set_2000_1.txt_it-IT_de-DE.txt"
mmt_custom_path_DeF = r"C:\Users\anton\Documents\Documenti importanti\SSLMIT FORLI M.A. SPECIALIZED TRANSLATION 2019-2021\tesi\EXPERIMENTS\1 (first official experiment on gt mmt deepl baselines; test set 2000)\A_test-set_2000_DE_DeF (1).txt"

report_path_export = r"C:\Users\anton\Documents\Documenti importanti\SSLMIT FORLI M.A. SPECIALIZED TRANSLATION 2019-2021\tesi\EXPERIMENTS\1 (first official experiment on gt mmt deepl baselines; test set 2000)\report_experiment_CoA-DeF_15032021.txt"


with open(test_set_path, "r", encoding="utf-8") as test:
    source = test.read().splitlines()
with open(reference_path, "r", encoding="utf-8") as refe:
    ref = refe.read().splitlines()
with open(MMT_baseline_path, "r", encoding="utf-8") as mmt_base:
    base_MMT = mmt_base.read().splitlines()


with open(mmt_custom_path_CoA, "r", encoding="utf-8") as mmt_custom:
    mmt_c = mmt_custom.read().splitlines()

with open(mmt_custom_path_DeF, "r", encoding="utf-8") as mmt_custom_DeF:
    mmt_c_DeF = mmt_custom_DeF.read().splitlines()


# checking length of different sets
if len(source) != len(ref) != len(base_MMT) != len(mmt_c) != len(mmt_c_DeF):
    print("Error: sets have not same length.")
    print("Length source: ", len(source))
    print("Length reference: ", len(ref))
    print("Length baseline: ", len(base_MMT))
    print("Length mmt CoA: ", len(mmt_c))
    print("Length mmt DeF: ", len(mmt_c_DeF))


# BLEU and chrF3 on whole test set (custom)
print("BLEU custom MMT_CoA: ", corpus_bleu(mmt_c, [ref]).score)
print("chrF3 custom MMT_CoA: ", corpus_chrf(mmt_c, [ref], beta=3).score)
print("BLEU custom MMT_DeF: ", corpus_bleu(mmt_c_DeF, [ref]).score)
print("chrF3 custom MMT_DeF: ", corpus_chrf(mmt_c_DeF, [ref], beta=3).score)


# on custom
columns = ["source", "reference", "MMT (baseline)", "MMT (custom)_CoA", "MMT (custom)_DeF", "BLEU (baseline)",
           "BLEU (custom)_CoA", "BLEU (custom)_DeF", "BLEU (difference baseline/custom_CoA)",
           "BLEU (difference baseline/custom_DeF)", "BLEU (difference custom CoA/custom DeF)", "chrF3 (baseline)",
           "chrF3 (custom)_CoA", "chrF3 (custom)_DeF", "chrF3 (difference baseline/custom_CoA)",
           "chrF3 (difference baseline/custom_DeF)", "chrF3 (difference custom CoA/custom DeF)"]    # 17 columns
dataframe = pd.DataFrame(columns=columns)
for i in range(len(source)):
    BLEU_mmt_b = float("{:.3f}".format(sentence_bleu(base_MMT[i], [ref[i]], smooth_method='exp').score))
    BLEU_mmt_c_CoA = float("{:.3f}".format(sentence_bleu(mmt_c[i], [ref[i]], smooth_method='exp').score))
    BLEU_mmt_c_DeF = float("{:.3f}".format(sentence_bleu(mmt_c_DeF[i], [ref[i]], smooth_method='exp').score))
    diff_BLEU_CoA = float("{:.3f}".format(float(BLEU_mmt_c_CoA) - float(BLEU_mmt_b)))
    diff_BLEU_DeF = float("{:.3f}".format(float(BLEU_mmt_c_DeF) - float(BLEU_mmt_b)))
    diff_BLEU_CoA_DeF = float("{:.3f}".format(float(BLEU_mmt_c_DeF) - float(BLEU_mmt_c_CoA)))
    chrF3_mmt_b = float("{:.3f}".format(sentence_chrf(base_MMT[i], [ref[i]]).score))
    chrF3_mmt_c_CoA = float("{:.3f}".format(sentence_chrf(mmt_c[i], [ref[i]], beta=3).score))
    chrF3_mmt_c_DeF = float("{:.3f}".format(sentence_chrf(mmt_c_DeF[i], [ref[i]], beta=3).score))
    diff_chrF3_CoA = float("{:.3f}".format(chrF3_mmt_c_CoA - chrF3_mmt_b))
    diff_chrF3_DeF = float("{:.3f}".format(chrF3_mmt_c_DeF - chrF3_mmt_b))
    diff_chrF3_CoA_DeF = float("{:.3f}".format(chrF3_mmt_c_DeF - chrF3_mmt_c_CoA))
    dataframe.loc[i] = [source[i], ref[i], base_MMT[i], mmt_c[i], mmt_c_DeF[i], BLEU_mmt_b, BLEU_mmt_c_CoA,
                        BLEU_mmt_c_DeF, diff_BLEU_CoA, diff_BLEU_DeF, diff_BLEU_CoA_DeF, chrF3_mmt_b, chrF3_mmt_c_CoA,
                        chrF3_mmt_c_DeF, diff_chrF3_CoA, diff_chrF3_DeF, diff_chrF3_CoA_DeF]

dataframe.to_csv(report_path_export, sep="\t", header=True, index=False)         # export report file as .csv

with open(report_path_export, "r", encoding="utf-8") as report:
    report_ = report.read()

#  applying regex to localize float with dot  float with comma for Excel
pattern = re.compile(r'(?<=.+)(\t-?\d\d?\d?)\.(\d{1,3}(\t|\r\n|\n))')
sub = re.sub(pattern, r"\1,\2", report_)
sub2 = re.sub(pattern, r"\1,\2", sub)
with open(report_path_export, "w", encoding="utf-8") as report_out:
    report_out.write(sub2)
