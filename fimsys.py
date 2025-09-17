import os
import json
import time
import hashlib
import logging
from logging import Logger
from datetime import datetime
from typing import Dict, List
import fnmatch

CHUNK_SIZE = 65536  # 64KB
DEFAULT_INTERVAL = 10  # seconds between scans


def setup_logger(log_file: str = None) -> Logger:
    logger = logging.getLogger("FIM")
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Clear old handlers to avoid duplicates
    if logger.hasHandlers():
        logger.handlers.clear()

    # console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    # file handler (optional)
    if log_file:
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger


def compute_sha256(file_path: str) -> str:
    h = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while True:
                chunk = f.read(CHUNK_SIZE)
                if not chunk:
                    break
                h.update(chunk)
    except (PermissionError, FileNotFoundError) as e:
        return f"<ERROR:{type(e).__name__}>"
    return h.hexdigest()


def get_file_metadata(path: str) -> Dict:
    try:
        st = os.stat(path)
        return {
            'size': st.st_size,
            'mtime': st.st_mtime
        }
    except Exception:
        return {'size': None, 'mtime': None}


def normalize_path(path: str) -> str:
    return os.path.normpath(os.path.abspath(path))


def should_exclude(path: str, exclude_patterns: List[str]) -> bool:
    for pat in exclude_patterns:
        if fnmatch.fnmatch(path, pat) or fnmatch.fnmatch(os.path.basename(path), pat):
            return True
    return False


def build_baseline(target_dir: str, baseline_file: str, exclude_patterns: List[str]) -> Dict:
    target_dir = normalize_path(target_dir)
    baseline = {
        'meta': {
            'generated_at': datetime.utcnow().isoformat() + 'Z',
            'root': target_dir
        },
        'files': {}
    }

    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), exclude_patterns)]
        for f in files:
            full = os.path.join(root, f)
            if should_exclude(full, exclude_patterns):
                continue
            rel = os.path.relpath(full, target_dir)
            h = compute_sha256(full)
            md = get_file_metadata(full)
            baseline['files'][rel] = {
                'hash': h,
                'size': md.get('size'),
                'mtime': md.get('mtime')
            }
    with open(baseline_file, 'w', encoding='utf-8') as bf:
        json.dump(baseline, bf, indent=2)
    return baseline


def load_baseline(baseline_file: str) -> Dict:
    try:
        with open(baseline_file, 'r', encoding='utf-8') as bf:
            return json.load(bf)
    except FileNotFoundError:
        return None


def scan_current_state(target_dir: str, exclude_patterns: List[str]) -> Dict:
    target_dir = normalize_path(target_dir)
    cur = {}
    for root, dirs, files in os.walk(target_dir):
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), exclude_patterns)]
        for f in files:
            full = os.path.join(root, f)
            if should_exclude(full, exclude_patterns):
                continue
            rel = os.path.relpath(full, target_dir)
            h = compute_sha256(full)
            md = get_file_metadata(full)
            cur[rel] = {
                'hash': h,
                'size': md.get('size'),
                'mtime': md.get('mtime')
            }
    return cur


def compare_baseline_and_current(baseline: Dict, current: Dict) -> Dict:
    added, deleted, modified = [], [], []
    base_files = baseline.get('files', {}) if baseline else {}
    base_keys, cur_keys = set(base_files.keys()), set(current.keys())

    added_keys = cur_keys - base_keys
    deleted_keys = base_keys - cur_keys
    common_keys = base_keys & cur_keys

    for k in added_keys:
        added.append({'path': k, 'current': current[k]})
    for k in deleted_keys:
        deleted.append({'path': k, 'baseline': base_files[k]})
    for k in common_keys:
        if base_files[k].get('hash') != current[k].get('hash'):
            modified.append({'path': k, 'baseline': base_files[k], 'current': current[k]})

    return {'added': added, 'deleted': deleted, 'modified': modified}


def print_and_log_diffs(diffs: Dict, logger: Logger):
    changes = 0
    if diffs['added']:
        logger.info('=== Added Files ===')
        for a in diffs['added']:
            logger.info(f"ADDED: {a['path']} | hash={a['current'].get('hash')}")
            changes += 1
    if diffs['deleted']:
        logger.info('=== Deleted Files ===')
        for d in diffs['deleted']:
            logger.info(f"DELETED: {d['path']} | old_hash={d['baseline'].get('hash')}")
            changes += 1
    if diffs['modified']:
        logger.info('=== Modified Files ===')
        for m in diffs['modified']:
            logger.info(f"MODIFIED: {m['path']} | old_hash={m['baseline'].get('hash')} | new_hash={m['current'].get('hash')}")
            changes += 1
    if changes == 0:
        logger.debug("No changes detected.")
    return changes


def monitor_loop(target_dir: str, baseline_file: str, interval: int, log_file: str, update_baseline: bool, exclude_patterns: List[str]):
    logger = setup_logger(log_file)
    logger.info(f"Monitoring {target_dir} every {interval}s...")
    baseline = load_baseline(baseline_file)
    if baseline is None:
        logger.error("Baseline not found. Run baseline first.")
        return

    try:
        while True:
            current = scan_current_state(target_dir, exclude_patterns)
            diffs = compare_baseline_and_current(baseline, current)
            changes = print_and_log_diffs(diffs, logger)

            # ✅ Auto-update baseline after changes
            if changes > 0 and update_baseline:
                baseline = {
                    'meta': {'generated_at': datetime.utcnow().isoformat() + 'Z', 'root': normalize_path(target_dir)},
                    'files': current
                }
                with open(baseline_file, 'w', encoding='utf-8') as bf:
                    json.dump(baseline, bf, indent=2)
                logger.info("Baseline auto-updated after change.")

            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Monitoring stopped.")


def run_scan_once(target_dir: str, baseline_file: str, log_file: str, exclude_patterns: List[str]) -> int:
    logger = setup_logger(log_file)
    baseline = load_baseline(baseline_file)
    if baseline is None:
        logger.error("Baseline not found. Run baseline first.")
        return 2
    current = scan_current_state(target_dir, exclude_patterns)
    diffs = compare_baseline_and_current(baseline, current)
    changes = print_and_log_diffs(diffs, logger)
    return 0 if changes == 0 else 1
