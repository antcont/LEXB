'''
Statistical significance test using Paired bootstrap resampling (Koehn 2004)  http://www.aclweb.org/anthology/W04-3250

based on: https://github.com/neubig/util-scripts/blob/master/paired-bootstrap.py by Graham Neubig and Mathias Müller
'''

import numpy as np
from sacrebleu import sentence_bleu, corpus_bleu, sentence_ter, corpus_ter, corpus_chrf, sentence_chrf
from hlepor import single_hlepor_score, hlepor_score


EVAL_TYPE_BLEU = "bleu"
EVAL_TYPE_HLEPOR = "hlepor"
EVAL_TYPE_CHRF3 = "chrF3"


EVAL_TYPES = [EVAL_TYPE_BLEU,
              EVAL_TYPE_HLEPOR,
              EVAL_TYPE_CHRF3]




def eval_measure(gold, sys, eval_type='bleu'):
    ''' Evaluation measure

    This takes in gold labels and system outputs and evaluates their
    accuracy. It currently supports:
    * Accuracy (acc), percentage of labels that match
    * Pearson's correlation coefficient (pearson)
    * BLEU score (bleu)
    * BLEU_detok, on detokenized references and translations, with internal tokenization
    :param gold: the correct labels (reference)
    :param sys: the system outputs (hypothesis)
    :param eval_type: The type of evaluation to do (bleu, chrf3, hlepor)
    '''
    if eval_type == EVAL_TYPE_BLEU:
        # make sure score is 0-based instead of 100-based
        return corpus_bleu(sys, [gold]).score / 100.
    elif eval_type == EVAL_TYPE_CHRF3:
        return corpus_chrf(sys, [gold], beta=3).score
    elif eval_type == EVAL_TYPE_HLEPOR:
        return hlepor_score(sys, gold)
    else:
        raise NotImplementedError('Unknown eval type in eval_measure: %s' % eval_type)


def eval_with_paired_bootstrap(gold, sys1, sys2,
                               num_samples=1000, sample_ratio=0.5,
                               eval_type='acc'):
    ''' Evaluate with paired boostrap
    This compares two systems, performing a significance tests with
    paired bootstrap resampling to compare the accuracy of the two systems.

    :param gold: The correct labels (reference)
    :param sys1: The output of system 1 (baseline hypothesis)
    :param sys2: The output of system 2 (MMT adapted hypothesis)
    :param num_samples: The number of bootstrap samples to take
    :param sample_ratio: The ratio of samples to take every time
    :param eval_type: The type of evaluation to do (bleu, chrF3, hlepor)
    '''
    assert (len(gold) == len(sys1))
    assert (len(gold) == len(sys2))

    '''# Preprocess the data appropriately for they type of eval
    gold = [eval_preproc(x, eval_type) for x in gold]
    sys1 = [eval_preproc(x, eval_type) for x in sys1]
    sys2 = [eval_preproc(x, eval_type) for x in sys2]'''


    sys1_scores = []
    sys2_scores = []
    wins = [0, 0, 0]
    n = len(gold)
    ids = list(range(n))

    counter = 0

    for _ in range(num_samples):
        counter += 1
        # Subsample the gold and system outputs
        reduced_ids = np.random.choice(ids, int(len(ids) * sample_ratio), replace=True)
        reduced_gold = [gold[i] for i in reduced_ids]
        reduced_sys1 = [sys1[i] for i in reduced_ids]
        reduced_sys2 = [sys2[i] for i in reduced_ids]
        # Calculate accuracy on the reduced sample and save stats
        sys1_score = eval_measure(reduced_gold, reduced_sys1, eval_type=eval_type)
        sys2_score = eval_measure(reduced_gold, reduced_sys2, eval_type=eval_type)
        if sys1_score > sys2_score:
            wins[0] += 1
        elif sys1_score < sys2_score:
            wins[1] += 1
        else:
            wins[2] += 1
        sys1_scores.append(sys1_score)
        sys2_scores.append(sys2_score)

        print("\r", "%s out of %s bootsrap resamples." % (counter, num_samples), end="")

    # Print win stats
    wins = [x / float(num_samples) for x in wins]
    print('Win ratio: sys1=%.3f, sys2=%.3f, tie=%.3f' % (wins[0], wins[1], wins[2]))
    if wins[0] > wins[1]:
        print('(sys1 is superior with p value p=%.3f)\n' % (1 - wins[0]))
    elif wins[1] > wins[0]:
        print('(sys2 is superior with p value p=%.3f)\n' % (1 - wins[1]))

    # Print system stats
    sys1_scores.sort()
    sys2_scores.sort()
    print('sys1 mean=%.3f, median=%.3f, 95%% confidence interval=[%.3f, %.3f]' %
          (np.mean(sys1_scores), np.median(sys1_scores), sys1_scores[int(num_samples * 0.025)],
           sys1_scores[int(num_samples * 0.975)]))
    print('sys2 mean=%.3f, median=%.3f, 95%% confidence interval=[%.3f, %.3f]' %
          (np.mean(sys2_scores), np.median(sys2_scores), sys2_scores[int(num_samples * 0.025)],
           sys2_scores[int(num_samples * 0.975)]))


if __name__ == "__main__":
    # execute only if run as a script
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('gold', help='File of reference set')
    parser.add_argument('sys1', help='File of baseline hypothesis set')
    parser.add_argument('sys2', help='File of adapted hypothesis set')
    parser.add_argument('--eval_type', help='The evaluation type (bleu, chrF3, hlepor)', type=str,
                        default='bleu', choices=EVAL_TYPES)
    parser.add_argument('--num_samples', help='Number of samples to use', type=int, default=10000)
    args = parser.parse_args()

    with open(args.gold, 'r', encoding="utf-8") as f:
        gold = f.readlines()
    with open(args.sys1, 'r', encoding="utf-8") as f:
        sys1 = f.readlines()
    with open(args.sys2, 'r', encoding="utf-8") as f:
        sys2 = f.readlines()
    eval_with_paired_bootstrap(gold, sys1, sys2, eval_type=args.eval_type, num_samples=args.num_samples)