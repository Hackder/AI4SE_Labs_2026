# Co-written by Claude Opus 5.5 and GPT-6.1 Sol
"""Score every checked attempt and compare the three prompts; the report reads the JSON output."""
import csv
import importlib.util
import itertools
import json
import math
import random
from pathlib import Path
from statistics import mean

from metrics import result_f1, balanced_result_f1

BASE = Path(__file__).resolve().parents[2]
RESULTS = BASE / 'analysis/results'
NAMES = ('rtf', 'icio', 'co_star')


def load_evaluator():
    path = BASE.parent / 'Assignments/Task_2/data/evaluate_retrieval_predictions.py'
    spec = importlib.util.spec_from_file_location('evaluator', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def evaluate(path, labels, db, evaluator):
    with path.open(newline='') as f:
        rows = list(csv.DictReader(f))
    records = []
    for row, label in zip(rows, labels):
        expected = json.loads(label['result'])
        try:
            actual, error = db.execute(row['predicted_sql']).fetchall(), None
        except Exception as exc:
            actual, error = [], str(exc)
        records.append(dict(
            id=int(row['id']), question=row['question'], sql=row['predicted_sql'],
            correct=error is None and evaluator.row_multiset(expected) == evaluator.row_multiset(actual),
            error=error, expected_count=len(expected), actual_count=len(actual),
            f1=result_f1(expected, actual, error is not None)))
    return records


def summarize(records):
    return dict(correct=sum(r['correct'] for r in records), accuracy=mean(r['correct'] for r in records),
                **balanced_result_f1(records), failed_ids=[r['id'] for r in records if not r['correct']])


def mcnemar(a, b):
    """Exact McNemar test: two-sided binomial test on questions where only one prompt is correct."""
    a_only = sum(x['correct'] and not y['correct'] for x, y in zip(a, b))
    b_only = sum(y['correct'] and not x['correct'] for x, y in zip(a, b))
    n = a_only + b_only
    p = min(1., 2 * sum(math.comb(n, k) for k in range(min(a_only, b_only) + 1)) / 2**n) if n else 1.
    return dict(a_only=a_only, b_only=b_only, p=p)


def permutation(a, b, draws=20000, seed=20261013):
    """Paired permutation test on balanced F1: randomly swap which prompt got each question's score."""
    sizes = {True: sum(r['expected_count'] == 0 for r in a), False: sum(r['expected_count'] > 0 for r in a)}
    diffs = [(x['f1'] - y['f1']) / (2 * sizes[x['expected_count'] == 0]) for x, y in zip(a, b)]
    observed = abs(sum(diffs))
    rng = random.Random(seed)
    hits = sum(abs(sum(d if rng.random() < .5 else -d for d in diffs)) >= observed - 1e-12 for _ in range(draws))
    return dict(difference=sum(diffs), p=(hits + 1) / (draws + 1))


def holm(tests):
    last = 0
    for rank, t in enumerate(sorted(tests, key=lambda t: t['p'])):
        last = max(last, min(1., (len(tests) - rank) * t['p']))
        t['p_holm'] = last


def main():
    csv.field_size_limit(10**9)
    evaluator = load_evaluator()
    with evaluator.LABELS_PATH.open(newline='') as f:
        labels = list(csv.DictReader(f))
    db = evaluator.load_database()

    summary, first, final = [], {}, {}
    for name in NAMES:
        attempts = sorted((BASE / 'agents' / name / 'attempts').glob('*.csv'))
        for path in attempts:
            records = evaluate(path, labels, db, evaluator)
            summary.append(dict(prompt=name, attempt=int(path.stem), **summarize(records)))
            first.setdefault(name, records)
        final[name] = evaluate(BASE / 'agents' / name / 'predictions.csv', labels, db, evaluator)
        run = json.loads((BASE / 'agents' / name / 'run/metadata.json').read_text())
        summary.append(dict(prompt=name, attempt='final', model=run['model_requested'],
                            reasoning=run['reasoning_effort_requested'], wall_seconds=run['wall_seconds'],
                            tokens=run['token_usage'], **summarize(final[name])))
        with (RESULTS / f'{name}.per_question.csv').open('w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=list(final[name][0]))
            writer.writeheader()
            writer.writerows(final[name])

    stats = {}
    for phase, records in (('first', first), ('final', final)):
        pairs = list(itertools.combinations(NAMES, 2))
        exact = [dict(a=a, b=b, **mcnemar(records[a], records[b])) for a, b in pairs]
        f1 = [dict(a=a, b=b, **permutation(records[a], records[b])) for a, b in pairs]
        holm(exact)
        holm(f1)
        stats[phase] = dict(mcnemar=exact, balanced_f1_permutation=f1)

    (RESULTS / 'summary.json').write_text(json.dumps(summary, indent=2))
    (RESULTS / 'statistics.json').write_text(json.dumps(stats, indent=2))
    print(json.dumps(stats, indent=2))


if __name__ == '__main__':
    main()
