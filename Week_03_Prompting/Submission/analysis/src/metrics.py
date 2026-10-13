# Co-written by Claude Opus 5.5 and GPT-6.1 Sol
"""Result F1 per question and balanced result F1 over all questions.

F1 = 2*TP / (2*TP + FP + FN), as in
https://scikit-learn.org/stable/modules/generated/sklearn.metrics.f1_score.html
"""
from collections import Counter
from statistics import mean


def result_f1(expected, returned, error=False):
    """Compare the rows a query returned with the rows of the correct answer.

    TP: correct rows the query returned. FP: wrong rows the query returned.
    FN: correct rows the query missed. Repeated rows count each time.
    Both answers empty scores 1. An SQL error scores 0.
    """
    if error:
        return 0.0
    correct = Counter(tuple(row) for row in expected)
    got = Counter(tuple(row) for row in returned)
    tp = sum((correct & got).values())
    fp = sum(got.values()) - tp
    fn = sum(correct.values()) - tp
    if tp + fp + fn == 0:
        return 1.0
    return 2 * tp / (2 * tp + fp + fn)


def balanced_result_f1(records):
    """Mean of the average F1 over questions with an empty correct answer and over the rest."""
    empty = [r['f1'] for r in records if r['expected_count'] == 0]
    nonempty = [r['f1'] for r in records if r['expected_count'] > 0]
    return dict(balanced_f1=(mean(empty) + mean(nonempty)) / 2, empty_f1=mean(empty), nonempty_f1=mean(nonempty))
