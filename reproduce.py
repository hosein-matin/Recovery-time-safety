#!/usr/bin/env python3
"""Reproduce one release component in an isolated copy; run --help for commands."""
from __future__ import annotations
import argparse
import csv
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent
ACTIONS = ('verify', 'hjb', 'continuous', 'continuous-benchmark', 'fixed-periods',
           'fixed-benchmark', 'sampled', 'sampled-benchmark', 'certificates', 'render-only')


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def verify(source):
    """Read-only checksum and release-count audit; no optional packages needed."""
    errors = []
    manifest = source / 'SHA256SUMS.txt'
    checked = 0
    if not manifest.exists():
        errors.append('SHA256SUMS.txt is absent; release integrity cannot be verified.')
    else:
        for line in manifest.read_text().splitlines():
            if not line.strip():
                continue
            try:
                expected, name = line.split(maxsplit=1)
                name = name.lstrip('*')
                path = (source / name).resolve()
                path.relative_to(source.resolve())
                if not path.is_file():
                    errors.append('Missing manifest file: ' + name)
                elif digest(path) != expected:
                    errors.append('SHA256 mismatch: ' + name)
                checked += 1
            except (ValueError, OSError) as exc:
                errors.append(f'Invalid/unreadable manifest entry {line!r}: {exc}')
    counts = {}
    for relative, expected in [('numerics_v6/data/episodes.csv', 936),
                               ('numerics_v6/data/refinement.csv', 504),
                               ('numerics_v7/data/episodes.csv', 360),
                               ('fixed_period_experiments/data/episodes.csv', 192)]:
        path = source / relative
        if not path.exists():
            errors.append('Missing release dataset: ' + relative)
            continue
        with path.open(newline='') as f:
            rows = list(csv.DictReader(f))
        counts[relative] = len(rows)
        if len(rows) != expected:
            errors.append(f'{relative}: expected {expected} rows, found {len(rows)}')
        if relative.startswith('numerics_v7/'):
            holds = sum(int(float(row.get('holds') or 0)) for row in rows)
            counts['historical_sampled_holds'] = holds
            if holds != 64067:
                errors.append(f'Historical sampled holds: expected 64067, found {holds}')
    policies = list((source / 'manuscript/numerics/policies').glob('*medium.npz'))
    counts['frozen_hjb_policies'] = len(policies)
    if len(policies) != 6:
        errors.append(f'Expected six supplied HJB policies, found {len(policies)}')
    report = {'status': 'passed' if not errors else 'failed', 'manifest_files_checked': checked,
              'counts': counts, 'errors': errors}
    print(json.dumps(report, indent=2))
    return 0 if not errors else 1


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='Examples:\n  python3 reproduce.py --verify\n  python3 reproduce.py --render-only\n'
               '  python3 reproduce.py --fixed-periods --fresh --workers 3\n'
               '  python3 reproduce.py --sampled --fresh --workers 4\n'
               'Fresh simulations are the default. --reuse explicitly permits supplied caches.\n'
               'Every execution except --verify creates output/reproduced/<UTC timestamp>-<action>/.\n'
               'The supplied release data are never overwritten. See README.md for scope and costs.')
    group = parser.add_mutually_exclusive_group(required=True)
    for action in ACTIONS:
        group.add_argument('--' + action, action='store_const', dest='action', const=action)
    freshness = parser.add_mutually_exclusive_group()
    freshness.add_argument('--fresh', dest='fresh', action='store_true', help='Recompute simulation records (default).')
    freshness.add_argument('--reuse', dest='fresh', action='store_false', help='Explicitly allow existing simulation caches.')
    parser.set_defaults(fresh=True)
    parser.add_argument('--workers', type=int, help='Production workers: default 3 for fixed periods, 4 otherwise.')
    parser.add_argument('--output-root', type=Path, default=ROOT / 'output/reproduced')
    parser.add_argument('--from-run', type=Path, help='Copy a previous isolated run as input for a subsequent action.')
    parser.add_argument('--plan', action='store_true', help='Print the planned commands without copying or executing.')
    args = parser.parse_args()
    if args.workers is not None and args.workers < 1:
        parser.error('--workers must be a positive integer')
    source = (args.from_run or ROOT).resolve()
    if not (source / 'manuscript/main.tex').exists():
        parser.error('--from-run must name a complete isolated package directory')
    if args.action == 'verify':
        return verify(source)
    workers = args.workers or (3 if args.action == 'fixed-periods' else 4)
    python = sys.executable
    commands = []
    def add(folder, *command):
        commands.append((folder, list(command)))
    action = args.action
    if action == 'hjb':
        add('.', python, 'scripts/reproduce_hjb_policies.py', '--out', 'reproduced/hjb')
    elif action == 'continuous':
        add('.', python, 'numerics_v6/run_v6.py', '--all', '--workers', str(workers),
            '--legacy', 'manuscript/numerics', *(['--resume'] if not args.fresh else []))
        add('.', python, 'manuscript/make_v6_paper_assets.py')
    elif action == 'continuous-benchmark':
        add('.', python, 'numerics_v6/benchmark_v6.py', '--legacy', 'manuscript/numerics')
    elif action in ('fixed-periods', 'fixed-benchmark'):
        add('fixed_period_experiments', 'bash', 'build_outward.sh')
        if action == 'fixed-periods':
            add('fixed_period_experiments', python, 'prepare_certificates.py')
            add('fixed_period_experiments', python, 'run_matrix.py', '--workers', str(workers))
            add('fixed_period_experiments', python, 'audit_results.py')
        else:
            add('fixed_period_experiments', python, 'benchmark_serial.py')
        add('fixed_period_experiments', python, 'analyze_results.py')
        add('.', python, 'scripts/refresh_manuscript_assets.py', '--fixed-periods')
    elif action in ('sampled', 'sampled-benchmark'):
        add('numerics_v7', 'bash', 'build_outward.sh')
        if action == 'sampled':
            add('numerics_v7', python, 'run_matrix.py', '--workers', str(workers),
                *(['--fresh'] if args.fresh else []))
        else:
            add('numerics_v7', python, 'benchmark_v7.py')
        add('numerics_v7', python, 'analyze_v7.py')
        add('.', python, 'manuscript/make_v7_full_tables.py')
        add('.', python, 'scripts/refresh_manuscript_assets.py', '--sampled')
    elif action == 'certificates':
        add('sampling_certificate', python, 'ovm_analytic_constants.py')
        add('sampling_certificate', python, 'certify_balanced.py', '--delta', '.025',
            '--out', 'certified_results_0025.json')
        add('sampling_certificate', python, 'make_certificate_summary.py')
        add('.', python, 'scripts/refresh_manuscript_assets.py', '--certificates')
    elif action == 'render-only':
        add('manuscript', 'bash', 'build.sh', 'all')
    if args.plan:
        print(json.dumps({'action': action, 'source': str(source), 'fresh': args.fresh,
                          'commands': [{'cwd': c, 'argv': a} for c, a in commands]}, indent=2))
        return 0
    output_root = args.output_root.resolve()
    stamp = dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%S.%fZ')
    work = output_root / f'{stamp}-{action}'
    def ignore(directory, names):
        rejected = []
        for name in names:
            candidate = Path(directory) / name
            if (name in {'output', 'reproduced', '.git', '.venv', 'venv', '__pycache__', '.pytest_cache'}
                    or candidate.suffix in {'.pyc', '.so'}
                    or candidate.resolve() in {output_root, work}):
                rejected.append(name)
        return rejected
    print(f'Copying release inputs to {work}', flush=True)
    shutil.copytree(source, work, ignore=ignore)
    if action == 'fixed-periods' and args.fresh:
        # This runner has no --fresh option; remove only the isolated copy's cache.
        shutil.rmtree(work / 'fixed_period_experiments/data/cases', ignore_errors=True)
        (work / 'fixed_period_experiments/data/cases').mkdir(parents=True)
    env = os.environ.copy()
    env.update({'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1', 'OMP_NUM_THREADS': '1',
                'MPLBACKEND': 'Agg', 'MPLCONFIGDIR': str(work / 'output/matplotlib')})
    manifest = {'action': action, 'started_utc': stamp, 'source': str(source), 'work': str(work),
                'fresh': args.fresh, 'workers': workers, 'status': 'running', 'commands': [],
                'scope': 'Only the selected component is recomputed; all other inputs retain their supplied provenance.',
                'root_manifest_sha256': digest(source / 'SHA256SUMS.txt') if (source / 'SHA256SUMS.txt').exists() else None}
    record = work / 'reproduction_run.json'
    def save():
        record.write_text(json.dumps(manifest, indent=2) + '\n')
    save()
    try:
        for folder, command in commands:
            print(f'[{folder}] ' + ' '.join(command), flush=True)
            started = time.perf_counter()
            result = subprocess.run(command, cwd=work / folder, env=env)
            manifest['commands'].append({'cwd': folder, 'argv': command,
                                          'returncode': result.returncode, 'seconds': time.perf_counter() - started})
            save()
            if result.returncode:
                raise RuntimeError(f'Command failed with exit code {result.returncode}')
        if action == 'hjb':
            check = json.loads((work / 'reproduced/hjb/regeneration_check.json').read_text())
            if len(check['cases']) != 6 or not check['all_exact']:
                raise RuntimeError('HJB regeneration did not reproduce all six supplied array sets exactly; see report.')
        if action == 'render-only':
            (work / 'pdf').mkdir(exist_ok=True)
            for filename in ('ECC_revision_v11_2026-11-08.pdf', 'ECC_revision_v11_technical_notes_2026-11-08.pdf'):
                shutil.copyfile(work / 'manuscript' / filename, work / 'pdf' / filename)
        manifest['status'] = 'complete'
        save()
        print(f'Completed {action}. Outputs and command record: {work}', flush=True)
        return 0
    except (OSError, RuntimeError) as exc:
        manifest.update(status='failed', error=str(exc))
        save()
        print(f'{exc}\nPartial outputs retained at {work}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
