import csv
import itertools
import re
from pathlib import Path
import io
from typing import Dict, Iterable, List, Optional, Tuple

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils.text import slugify as dj_slugify

from apps.profiles.models import (
    HardSkill, SoftSkill, JobRole, JobCategory,
    JobHardSkill, JobSoftSkill,
)


def read_csv_rows(path: Path, *, encoding: Optional[str] = None, header_row: int = 1) -> Iterable[Dict[str, str]]:
    encodings = [encoding] if encoding else ["utf-8-sig", "cp949", "utf-8"]
    last_err = None
    for enc in encodings:
        try:
            with path.open("r", encoding=enc, newline="") as f:
                lines = f.readlines()
                if header_row > 1:
                    lines = lines[header_row - 1 :]
                data_stream = io.StringIO("".join(lines))
                reader = csv.DictReader(data_stream)
                # Normalize headers: lower + strip
                reader.fieldnames = [
                    (h or "").strip().lower() for h in (reader.fieldnames or [])
                ]
                for row in reader:
                    yield {k: (v or "").strip() for k, v in row.items()}
            return
        except Exception as e:  # pragma: no cover - robust import on servers
            last_err = e
            continue
    raise CommandError(f"Failed to read CSV {path} with encodings {encodings}: {last_err}")


def slugify_code(name: str) -> str:
    base = dj_slugify(name) or re.sub(r"\W+", "-", name.strip()).strip("-").lower() or "skill"
    return base


def ensure_unique_code(base: str) -> str:
    code = base
    for i in itertools.count(2):
        if not HardSkill.objects.filter(code=code).exists():
            return code
        code = f"{base}-{i}"


class Command(BaseCommand):
    help = "Load Hard/Soft skills and optional job-role mappings from CSV files"

    def add_arguments(self, parser):
        parser.add_argument("--hard", type=str, help="Hard skill CSV path")
        parser.add_argument("--soft", type=str, help="Soft skill CSV path")
        parser.add_argument("--jobroles", type=str, help="JobRole CSV path (optional)")
        parser.add_argument("--map-hard", dest="map_hard", type=str, help="Job ↔ HardSkill mapping CSV path")
        parser.add_argument("--map-soft", dest="map_soft", type=str, help="Job ↔ SoftSkill mapping CSV path")
        parser.add_argument("--encoding", type=str, default=None, help="Force CSV encoding (e.g., utf-8-sig, cp949)")
        parser.add_argument("--create-missing-role", action="store_true", help="Create JobRole if not exists when mapping")
        parser.add_argument("--dry-run", action="store_true", help="Validate without writing to DB")
        # header rows (1-based). If provided, applies globally unless per-file is specified
        parser.add_argument("--header-row", type=int, default=1, help="Header row index (1-based) for all CSVs")
        parser.add_argument("--hard-header-row", type=int, default=None, help="Header row index for hard CSV")
        parser.add_argument("--soft-header-row", type=int, default=None, help="Header row index for soft CSV")
        parser.add_argument("--job-header-row", type=int, default=None, help="Header row index for jobroles CSV")

    def handle(self, *args, **opts):
        dry = opts.get("dry_run")
        enc = opts.get("encoding")

        created = {
            "hard": 0, "soft": 0, "jobrole": 0, "jobcat": 0,
            "map_hard": 0, "map_soft": 0,
        }

        with transaction.atomic():
            sid = transaction.savepoint()

            global_header = int(opts.get("header_row") or 1)
            hard_header = int(opts.get("hard_header_row") or global_header)
            soft_header = int(opts.get("soft_header_row") or global_header)
            job_header = int(opts.get("job_header_row") or global_header)

            # 1) HardSkill
            hard_path = opts.get("hard")
            if hard_path:
                self.stdout.write(self.style.NOTICE(f"Loading hard skills: {hard_path}"))
                for row in read_csv_rows(Path(hard_path), encoding=enc, header_row=hard_header):
                    # tolerate headers: name, hard_skill_name, hard_skill, etc.
                    name = row.get("name") or row.get("hard_skill_name") or row.get("hard_skill_") or row.get("hard_skill")
                    if not name:
                        continue
                    code = row.get("code") or row.get("hsc_code") or slugify_code(name)
                    if HardSkill.objects.filter(name=name).exists():
                        continue
                    code = ensure_unique_code(slugify_code(code))
                    HardSkill.objects.create(name=name, code=code)
                    created["hard"] += 1

            # 2) SoftSkill
            soft_path = opts.get("soft")
            if soft_path:
                self.stdout.write(self.style.NOTICE(f"Loading soft skills: {soft_path}"))
                for row in read_csv_rows(Path(soft_path), encoding=enc, header_row=soft_header):
                    name = row.get("name") or row.get("soft_skill_name") or row.get("soft_skill_") or row.get("soft_skill")
                    if not name:
                        continue
                    if SoftSkill.objects.filter(name=name).exists():
                        continue
                    SoftSkill.objects.create(name=name)
                    created["soft"] += 1

            # 3) JobRoles (optional)
            jobroles_path = opts.get("jobroles")
            if jobroles_path:
                self.stdout.write(self.style.NOTICE(f"Loading job roles: {jobroles_path}"))
                for row in read_csv_rows(Path(jobroles_path), encoding=enc, header_row=job_header):
                    name = row.get("name") or row.get("job_name") or row.get("role_name")
                    if not name:
                        continue
                    cat_name = row.get("category") or row.get("j_category") or None
                    cat_obj = None
                    if cat_name:
                        cat_obj, _new = JobCategory.objects.get_or_create(name=cat_name)
                        if _new:
                            created["jobcat"] += 1
                    if not JobRole.objects.filter(name=name).exists():
                        JobRole.objects.create(name=name, job_category=cat_obj)
                        created["jobrole"] += 1

            # 4) Job ↔ HardSkill mapping
            map_hard = opts.get("map_hard")
            if map_hard:
                self.stdout.write(self.style.NOTICE(f"Mapping job ↔ hard skills: {map_hard}"))
                for row in read_csv_rows(Path(map_hard), encoding=enc):
                    role_name = row.get("job_role") or row.get("role_name") or row.get("job_name")
                    hard_code = row.get("hard_code") or row.get("code")
                    hard_name = row.get("hard_name") or row.get("name")
                    if not role_name or not (hard_code or hard_name):
                        continue
                    role = JobRole.objects.filter(name=role_name).first()
                    if not role and opts.get("create_missing_role"):
                        role = JobRole.objects.create(name=role_name)
                        created["jobrole"] += 1
                    if not role:
                        continue
                    hs = None
                    if hard_code:
                        hs = HardSkill.objects.filter(code=hard_code).first()
                    if not hs and hard_name:
                        hs = HardSkill.objects.filter(name=hard_name).first()
                    if not hs:
                        # create on the fly using name/code if present
                        src = hard_name or hard_code
                        if not src:
                            continue
                        code = ensure_unique_code(slugify_code(hard_code or hard_name))
                        hs = HardSkill.objects.create(name=(hard_name or code), code=code)
                        created["hard"] += 1
                    JobHardSkill.objects.get_or_create(job_role=role, hard_skill=hs)
                    created["map_hard"] += 1

            # 5) Job ↔ SoftSkill mapping
            map_soft = opts.get("map_soft")
            if map_soft:
                self.stdout.write(self.style.NOTICE(f"Mapping job ↔ soft skills: {map_soft}"))
                for row in read_csv_rows(Path(map_soft), encoding=enc):
                    role_name = row.get("job_role") or row.get("role_name") or row.get("job_name")
                    soft_name = row.get("soft_name") or row.get("name") or row.get("soft_skill_name")
                    if not role_name or not soft_name:
                        continue
                    role = JobRole.objects.filter(name=role_name).first()
                    if not role and opts.get("create_missing_role"):
                        role = JobRole.objects.create(name=role_name)
                        created["jobrole"] += 1
                    if not role:
                        continue
                    ss, _ = SoftSkill.objects.get_or_create(name=soft_name)
                    if _:
                        created["soft"] += 1
                    JobSoftSkill.objects.get_or_create(job_role=role, soft_skill=ss)
                    created["map_soft"] += 1

            self.stdout.write(self.style.SUCCESS(
                f"Hard:{created['hard']} Soft:{created['soft']} JobRole:{created['jobrole']} "
                f"JobCat:{created['jobcat']} MapHard:{created['map_hard']} MapSoft:{created['map_soft']}"
            ))

            if dry:
                transaction.savepoint_rollback(sid)
                self.stdout.write(self.style.WARNING("Dry-run: rolled back all changes."))
            else:
                transaction.savepoint_commit(sid)
