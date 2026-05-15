#!/usr/bin/env python3
from __future__ import annotations

import argparse
import email
import json
import os
import stat
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DEFAULT_OUT_DIR = ROOT / "third_party_licenses"
DEFAULT_VENV_DIR = ROOT / "kdv" / ".venv"
DEFAULT_GO_DIR = ROOT / "kdv_parser"

LICENSE_PATTERNS = (
    "LICENSE",
    "LICENSE.*",
    "LICENCE",
    "LICENCE.*",
    "COPYING",
    "COPYING.*",
    "NOTICE",
    "NOTICE.*",
    "COPYRIGHT",
    "COPYRIGHT.*",
    "AUTHORS",
    "AUTHORS.*",
)


def find_site_packages(venv_dir: Path) -> Path | None:
    candidates = [venv_dir / "Lib" / "site-packages"]
    candidates.extend((venv_dir / "lib").glob("python*/site-packages"))
    for path in candidates:
        if path.exists():
            return path
    return None


def normalize_name(name: str) -> str:
    return name.replace("/", "_")


def copy_license_files(src_dir: Path, dest_dir: Path) -> bool:
    found = False
    dest_dir.mkdir(parents=True, exist_ok=True)
    for pattern in LICENSE_PATTERNS:
        for path in src_dir.glob(pattern):
            if not path.is_file():
                continue
            shutil.copy2(path, dest_dir / path.name)
            found = True
    return found


def read_metadata_name_version(metadata_file: Path) -> tuple[str, str]:
    msg = email.message_from_string(metadata_file.read_text(errors="ignore"))
    name = msg.get("Name", metadata_file.parent.name.replace(".dist-info", ""))
    version = msg.get("Version", "")
    return name, version


def _remove_readonly(func, path, _exc_info):
    try:
        os.chmod(path, stat.S_IWRITE | stat.S_IREAD)
        func(path)
    except FileNotFoundError:
        pass


def prepare_output_dir(out_dir: Path) -> None:
    # Always clear previous output first to avoid overwrite/permission errors.
    if out_dir.exists():
        shutil.rmtree(out_dir, onerror=_remove_readonly)
    out_dir.mkdir(parents=True, exist_ok=True)


def collect_python(venv_dir: Path, out_dir: Path) -> int:
    site_packages = find_site_packages(venv_dir)
    if site_packages is None:
        print(f"[python] site-packages not found under: {venv_dir}")
        return 1

    dist_infos = sorted(site_packages.glob("*.dist-info"))
    if not dist_infos:
        print(f"[python] no .dist-info found: {site_packages}")
        return 1

    print(f"[python] scanning: {site_packages}")
    py_out = out_dir / "python"
    py_out.mkdir(parents=True, exist_ok=True)

    failures = 0
    for dist in dist_infos:
        metadata_file = dist / "METADATA"
        if not metadata_file.exists():
            continue

        name, version = read_metadata_name_version(metadata_file)
        target = py_out / normalize_name(name)
        target.mkdir(parents=True, exist_ok=True)

        found = copy_license_files(dist, target)
        found = copy_license_files(site_packages, target) or found
        shutil.copy2(metadata_file, target / "METADATA")

        status = "OK" if found else "METADATA ONLY"
        if not found:
            failures += 1
        print(f"  - {name}=={version}: {status}")

    return 0 if failures == 0 else 2


def parse_go_list_output(text: str):
    decoder = json.JSONDecoder()
    i = 0
    n = len(text)
    while i < n:
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break
        obj, idx = decoder.raw_decode(text, i)
        i = idx
        yield obj


def collect_go(go_dir: Path, out_dir: Path) -> int:
    if not go_dir.exists():
        print(f"[go] directory not found: {go_dir}")
        return 1

    try:
        output = subprocess.check_output(
            ["go", "list", "-m", "-json", "all"],
            cwd=go_dir,
            text=True,
            stderr=subprocess.STDOUT,
        )
    except FileNotFoundError:
        print("[go] go command not found, skipping")
        return 2
    except subprocess.CalledProcessError as exc:
        print("[go] go list failed")
        print(exc.output)
        return 2

    go_out = out_dir / "go"
    go_out.mkdir(parents=True, exist_ok=True)
    failures = 0

    for mod in parse_go_list_output(output):
        if mod.get("Main"):
            continue
        path = mod.get("Path")
        version = mod.get("Version")
        mod_dir = mod.get("Dir")
        if not (path and version and mod_dir):
            continue

        src = Path(mod_dir)
        dst = go_out / f"{normalize_name(path)}@{version}"
        dst.mkdir(parents=True, exist_ok=True)

        found = copy_license_files(src, dst)
        if found:
            print(f"  - {path}@{version}: OK")
        else:
            failures += 1
            print(f"  - {path}@{version}: LICENSE NOT FOUND")

    return 0 if failures == 0 else 2


def write_third_party_notice(out_dir: Path) -> None:
    notice = ROOT / "THIRD_PARTY_NOTICES.txt"
    notice.write_text(
        "Third-Party Notices\n"
        "===================\n"
        "\n"
        "This distribution includes third-party software components.\n"
        "\n"
        "License texts are bundled in:\n"
        f"- {out_dir.relative_to(ROOT).as_posix()}/\n",
        encoding="utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Collect Python/Go dependency licenses")
    parser.add_argument("--venv-dir", type=Path, default=DEFAULT_VENV_DIR)
    parser.add_argument("--go-dir", type=Path, default=DEFAULT_GO_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Delete output directory before collecting",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with non-zero status if any dependency license file is missing",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    out_dir = args.out_dir.resolve()
    prepare_output_dir(out_dir)

    print(f"output: {out_dir}")
    py_rc = collect_python(args.venv_dir.resolve(), out_dir)
    go_rc = collect_go(args.go_dir.resolve(), out_dir)
    write_third_party_notice(out_dir)
    print("done")
    if py_rc == 1 or go_rc == 1:
        return 1
    if args.strict and (py_rc != 0 or go_rc != 0):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
