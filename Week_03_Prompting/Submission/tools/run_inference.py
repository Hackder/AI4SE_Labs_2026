# Co-written by Claude Opus 5.5 and GPT-6.1 Sol
"""Run each prompt in a fresh CLI agent session and record the session time."""
import datetime
import hashlib
import json
import pathlib
import subprocess
import time

BASE = pathlib.Path(__file__).resolve().parents[1]
ROOT = BASE.parents[2]
MODEL = 'gpt-5.6-luna'


def main():
    for name in ('rtf', 'icio', 'co_star'):
        (BASE / 'agents' / name / 'run').mkdir(parents=True, exist_ok=True)
        prompt = (BASE / 'agents' / name / 'prompt.txt').read_text()
        command = ['codex', 'exec', '--ephemeral', '--skip-git-repo-check', '-C', str(ROOT), '-s', 'workspace-write', '-m', MODEL, '-c', 'model_reasoning_effort="low"', '--json', '-o', str(BASE / 'agents' / name / 'run' / 'final.txt'), '-']
        started = datetime.datetime.now(datetime.timezone.utc).isoformat()
        tick = time.perf_counter()
        print(f'Starting {name}: {MODEL}, low', flush=True)
        with (BASE / 'agents' / name / 'run' / 'events.jsonl').open('w') as stdout, (BASE / 'agents' / name / 'run' / 'stderr.txt').open('w') as stderr:
            result = subprocess.run(command, input=prompt, text=True, stdout=stdout, stderr=stderr)
        elapsed = time.perf_counter() - tick
        metadata = dict(prompt_id=name, prompt_sha256=hashlib.sha256(prompt.encode()).hexdigest(), started_utc=started, ended_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(), wall_seconds=elapsed, returncode=result.returncode, command=[part.replace(str(ROOT), '.') for part in command], model_requested=MODEL, reasoning_effort_requested='low')
        (BASE / 'agents' / name / 'run' / 'metadata.json').write_text(json.dumps(metadata, indent=2))
        print(f'Finished {name}: returncode={result.returncode}, seconds={elapsed:.3f}', flush=True)
        if result.returncode:
            print((BASE / 'agents' / name / 'run' / 'stderr.txt').read_text()[-2000:], flush=True)
            break


if __name__ == '__main__':
    main()
