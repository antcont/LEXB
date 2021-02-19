'''
Metrics for automatic MT evaluation:
- BLEU score
- chrF3 (https://www.aclweb.org/anthology/W15-3049.pdf)

'''

from sacrebleu import sentence_bleu, corpus_bleu, sentence_ter, corpus_ter, corpus_chrf, sentence_chrf
import pandas as pd

'''
source = "I presenti criteri disciplinano, ai sensi dell’articolo 54, commi 1 e 2, della legge provinciale 18 giugno 2002, n. 8, e successive modifiche, di seguito denominata legge, la concessione di contributi in conto capitale per:".split()
ref = "Diese Richtlinien regeln im Sinne von Artikel 54 Absätze 1 und 2 des Landesgesetzes vom 18. Juni 2002, Nr. 8, in geltender Fassung, in der Folge als Gesetz bezeichnet, die Gewährung von Beiträgen für Investitionsausgaben für:".split()
hyp_MMT = 'Diese Kriterien regeln gemäß Artikel 54 Absätze 1 und 2 des Provinzgesetzes Nr. 8 vom 18. Juni 2002 und späterer Änderungen, im Folgenden "Gesetz" genannt, die Gewährung von Kapitalzuschüssen für:'.split()
hyp_DeepL = 'Die vorliegenden Kriterien regeln gemäß Artikel 54 Absätze 1 und 2 der Norma Foral Nr. 8 vom 18. Juni 2002 mit späteren Änderungen, im Folgenden "Gesetz" genannt, die Gewährung von Kapitalzuschüssen für:'.split()
hyp_GT = "Diese Kriterien regeln gemäß Artikel 54 Absätze 1 und 2 des Landesgesetzes vom 18. Juni 2002 Nr. 8 und nachfolgende Änderungen, im Folgenden als Gesetz bezeichnet, die Gewährung von Kapitalzuschüssen für:".split()

#with nltk's BLEU
print("MMT: ", sentence_bleu([ref], hyp_MMT))
print("Google Translate: ", sentence_bleu([ref], hyp_GT))
print("DeepL: ", sentence_bleu([ref], hyp_DeepL))
'''

test_set_path = r"C:\Users\anton\Dropbox\Eurac_tesi\custom_MT\test-set_2000_1.txt"
reference_path = r"C:\Users\anton\Dropbox\Eurac_tesi\custom_MT\reference_2000_1.txt"
MMT_baseline_path = r"C:\Users\anton\Dropbox\Eurac_tesi\custom_MT\experiments\mmt_baseline_1.txt"
deepl_baseline_path = r"C:\Users\anton\Dropbox\Eurac_tesi\custom_MT\experiments\deepl_baseline_1.txt"
gt_baseline_path = r"C:\Users\anton\Dropbox\Eurac_tesi\custom_MT\experiments\gt_baseline_1.txt"
report_path_export = r"C:\Users\anton\Dropbox\Eurac_tesi\custom_MT\experiments\report_experiment1_baseline.txt"


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
    hyp_MMT = mmt_base.read().splitlines()
with open(deepl_baseline_path, "r", encoding="utf-8") as deepl_base:
    hyp_deepl = deepl_base.read().splitlines()
with open(gt_baseline_path, "r", encoding="utf-8") as gt_base:
    hyp_gt = gt_base.read().splitlines()

'''
with open(MMT_experiment_path, "r", encoding="utf-8") as exp:
    mmt = exp.read().splitlines()
'''
'''
if len(source) != len(reference) != len(baseline) != len(mmt):
    print("Error: sets have not same length.")
    print("Length source: ", len(source))
    print("Length reference: ", len(reference))
    print("Length baseline: ", len(baseline))
    print("Length mmt: ", len(mmt))
'''
'''
source = "I presenti criteri disciplinano, ai sensi dell’articolo 54, commi 1 e 2, della legge provinciale 18 giugno 2002, n. 8, e successive modifiche, di seguito denominata legge, la concessione di contributi in conto capitale per:"
ref = "Diese Richtlinien regeln im Sinne von Artikel 54 Absätze 1 und 2 des Landesgesetzes vom 18. Juni 2002, Nr. 8, in geltender Fassung, in der Folge als Gesetz bezeichnet, die Gewährung von Beiträgen für Investitionsausgaben für:"
hyp_MMT = 'Diese Kriterien regeln gemäß Artikel 54 Absätze 1 und 2 des Provinzgesetzes Nr. 8 vom 18. Juni 2002 und späterer Änderungen, im Folgenden "Gesetz" genannt, die Gewährung von Kapitalzuschüssen für:'
hyp_DeepL = 'Die vorliegenden Kriterien regeln gemäß Artikel 54 Absätze 1 und 2 der Norma Foral Nr. 8 vom 18. Juni 2002 mit späteren Änderungen, im Folgenden "Gesetz" genannt, die Gewährung von Kapitalzuschüssen für:'
hyp_GT = "Diese Kriterien regeln gemäß Artikel 54 Absätze 1 und 2 des Landesgesetzes vom 18. Juni 2002 Nr. 8 und nachfolgende Änderungen, im Folgenden als Gesetz bezeichnet, die Gewährung von Kapitalzuschüssen für:"
'''

# BLEU on the whole test set
print("BLEU MMT: ", corpus_bleu(hyp_MMT, [ref]).score)
print("BLEU Google Translate: ", corpus_bleu(hyp_gt, [ref]).score)
print("BLEU DeepL: ", corpus_bleu(hyp_deepl, [ref]).score)

'''
# TER on the whole test set
print("TER MMT: ", corpus_ter(hyp_MMT, ref).score)
print("TER Google Translate: ", corpus_ter(hyp_GT, ref).score)
print("TER DeepL: ", corpus_ter(hyp_DeepL, ref).score)
'''

# chrF3 on the whole test set
print("chrF3 MMT: ", corpus_chrf(hyp_MMT, [ref], beta=3).score)
print("chrF3 Google Translate: ", corpus_chrf(hyp_gt, [ref], beta=3).score)
print("chrF3 DeepL: ", corpus_chrf(hyp_deepl, [ref], beta=3).score)

# computing metrics on single segments
#columns = ["source", "reference", "MMT (baseline)", "MMT (custom)", "BLEU (baseline)", "BLEU (custom)", "TER (baseline)", "TER (custom)", "chrF (baseline)", "chrF (custom)"]
columns = ["source", "reference", "mmt (baseline)", "gt (baseline)", "deepl (baseline)", "BLEU (mmt)", "chrF3 (mmt)", "BLEU (gt)", "chrF3 (gt)", "BLEU (deepl)", "chrF3 (deepl)"]
dataframe = pd.DataFrame(columns=columns)
for i in range(len(source)):
    BLEU_mmt = "{:.3f}".format(sentence_bleu(hyp_MMT[i], [ref[i]], smooth_method='exp').score)
    chrF3_mmt = sentence_chrf(hyp_MMT[i], [ref[i]]).score
    BLEU_gt = "{:.3f}".format(sentence_bleu(hyp_gt[i], [ref[i]], smooth_method='exp').score)
    chrF3_gt = sentence_chrf(hyp_gt[i], [ref[i]]).score
    BLEU_deepl = "{:.3f}".format(sentence_bleu(hyp_deepl[i], [ref[i]], smooth_method='exp').score)
    chrF3_deepl = sentence_chrf(hyp_deepl[i], [ref[i]]).score
    dataframe.loc[i] = [source[i], ref[i], hyp_MMT[i], hyp_gt[i], hyp_deepl[i], BLEU_mmt, chrF3_mmt, BLEU_gt, chrF3_gt, BLEU_deepl, chrF3_deepl]
    '''
    BLEU_baseline = sentence_bleu(baseline[i], reference[i])
    BLEU_custom = sentence_bleu(mmt[i], reference[i])
    TER_baseline = sentence_ter(baseline[i], reference[i])
    TER_custom = sentence_ter(mmt[i], reference[i])
    chrF3_baseline = sentence_chrf(baseline[i], reference[i], beta=3)
    chrF3_custom = sentence_chrf(mmt[i], reference[i], beta=3)
    dataframe.loc[i] = [source[i], reference[i], baseline[i], mmt[i], BLEU_baseline, BLEU_custom, TER_baseline, TER_custom, chrF3_baseline, chrF3_custom]
    '''

dataframe.to_csv(report_path_export, sep="\t", header=True, index=False)         # export report file as .csv

