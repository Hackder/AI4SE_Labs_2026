# Co-written by Claude Opus 5.5 and GPT-6.1 Sol
"""Evaluate and archive every attempt using the assignment's exact row-multiset metric.

The checker reports failing IDs, execution errors, and row counts, never label rows.
Every invocation preserves the CSV and feedback for later analysis.
"""
import argparse
import csv
import hashlib
import importlib.util
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('predictions', type=Path)
    args = parser.parse_args()
    source = args.predictions.resolve()
    original = BASE.parent / 'Assignments/Task_2/data/evaluate_retrieval_predictions.py'
    spec = importlib.util.spec_from_file_location('assignment_evaluator', original)
    evaluator = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(evaluator)
    csv.field_size_limit(10**9)
    labels = list(csv.DictReader(evaluator.LABELS_PATH.open(encoding='utf-8', newline='')))
    questions = list(csv.DictReader((BASE / 'inputs/questions.csv').open(encoding='utf-8', newline='')))
    with source.open(encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        if not {'id', 'question', 'predicted_sql'} <= set(reader.fieldnames or []):
            raise ValueError('Required columns: id,question,predicted_sql')
        predictions = list(reader)
    by_id = {}
    for row in predictions:
        ident = int(row['id'])
        if ident in by_id:
            raise ValueError(f'Duplicate ID {ident}')
        by_id[ident] = row
    if set(by_id) != set(range(len(labels))):
        raise ValueError('IDs must cover 0..154 exactly once')
    for i, q in enumerate(questions):
        if by_id[i]['question'] != q['question'] or q['question'] != labels[i]['question']:
            raise ValueError(f'Question text mismatch at ID {i}')
    connection = evaluator.load_database()
    connection.execute('PRAGMA query_only=ON')
    outcomes = []
    for i, label in enumerate(labels):
        sql = by_id[i]['predicted_sql']
        expected = json.loads(label['result'])
        error = None
        rows = []
        # Bound runaway queries without inspecting or repairing the prediction.
        budget = [0]
        def progress():
            budget[0] += 1
            return budget[0] > 20000
        connection.set_progress_handler(progress, 1000)
        try:
            if not sql.lstrip().lower().startswith(('select', 'with')):
                raise sqlite3.OperationalError('Only read-only SELECT queries allowed')
            rows = connection.execute(sql).fetchall()
            correct = evaluator.row_multiset(rows) == evaluator.row_multiset(expected)
        except sqlite3.Error as exc:
            error = str(exc)
            correct = False
        outcomes.append(dict(id=i, correct=correct, expected_count=len(expected), actual_count=len(rows), error=error))
    connection.close()
    count = sum(r['correct'] for r in outcomes)
    history = source.parent / 'attempts'
    history.mkdir(parents=True, exist_ok=True)
    attempt = 1 + max([int(p.stem) for p in history.glob('*.csv')], default=0)
    content = source.read_bytes()
    (history / f'{attempt:03}.csv').write_bytes(content)
    feedback = dict(attempt=attempt, checked_utc=datetime.now(timezone.utc).isoformat(), sha256=hashlib.sha256(content).hexdigest(), correct=count, total=len(labels), accuracy=count/len(labels), outcomes=outcomes)
    (history / f'{attempt:03}.json').write_text(json.dumps(feedback, indent=2))
    print(f'Accuracy: {count / len(labels):.4f} ({count / len(labels):.2%})\nCorrect: {count}/{len(labels)}\nAttempt: {attempt}')
    for r in outcomes:
        if not r['correct']:
            print(f"FAIL id={r['id']} expected_count={r['expected_count']} actual_count={r['actual_count']} error={r['error']}")


if __name__ == '__main__':
    main()
