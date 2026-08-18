"""Reproducible benchmark for the real placement eligibility engine.

This benchmark intentionally calls the application's existing
``run_eligibility_engine`` service. It does not reimplement the automated
eligibility logic for the automated measurement.

The benchmark uses a temporary SQLite database so it cannot modify the
application's development/production database. Student data is deterministic
and generated in memory, then loaded into that temporary database before each
measured run. Data loading is excluded from the timed engine interval.

The manual-style baseline is a computational simulation of spreadsheet-like
filtering over Python rows. It is NOT a measurement of a human placement
officer or of Microsoft Excel. It is included only as a reproducible
algorithmic baseline for the same eligibility rules.
"""

from __future__ import annotations

import argparse
import csv
import os
import statistics
import sys
import tempfile
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))


SIZES = (100, 500, 1_000, 5_000, 10_000)
REPEATS = 5

COMPANY_RULES = {
    "min_cgpa": "7.50",
    "max_backlogs": 1,
    "eligible_branches": "CSE,IT,AIDS,CSBS",
    "required_skills": "python,django",
    "eligible_year": 2026,
}

BRANCHES = ("CSE", "IT", "ECE", "EEE", "ME", "AIDS", "CSBS")
SKILL_SETS = (
    "Python, SQL",
    "Django, Python",
    "Java, SQL",
    "C#, SQL",
    "Python, Django, SQL",
    "Java, Spring",
)


def generate_rows(size: int) -> list[dict]:
    """Create deterministic student rows used by both benchmark paths."""
    rows = []
    for i in range(size):
        rows.append(
            {
                "name": f"Benchmark Student {i + 1}",
                "roll_number": f"BENCH{i + 1:06d}",
                "email": f"bench{i + 1:06d}@example.test",
                "cgpa": round(6.0 + ((i * 37) % 401) / 100, 2),
                "backlogs": (i * 7) % 4,
                "branch": BRANCHES[(i * 3) % len(BRANCHES)],
                "skills": SKILL_SETS[(i * 5) % len(SKILL_SETS)],
                "graduation_year": 2025 + (i % 2),
            }
        )
    return rows


def manual_style_filter(rows: list[dict]) -> int:
    """Simulate spreadsheet-style sequential filtering in Python.

    This is deliberately not described as a human/Excel timing. The timed
    operation represents row filtering plus constructing the resulting
    shortlist rows, using the same rules as the company configuration.
    """
    eligible_branches = {
        value.strip().upper()
        for value in COMPANY_RULES["eligible_branches"].split(",")
    }
    required_skills = {
        value.strip().lower()
        for value in COMPANY_RULES["required_skills"].split(",")
    }

    filtered = [row for row in rows if row["cgpa"] >= 7.50]
    filtered = [row for row in filtered if row["backlogs"] <= 1]
    filtered = [row for row in filtered if row["branch"] in eligible_branches]
    filtered = [
        row for row in filtered if row["graduation_year"] == COMPANY_RULES["eligible_year"]
    ]

    matched = []
    for row in filtered:
        student_skills = {
            skill.strip().lower() for skill in row["skills"].split(",") if skill.strip()
        }
        if required_skills.intersection(student_skills):
            matched.append(row)

    # Simulate producing the shortlist rows, rather than stopping at a count.
    shortlist_rows = [row["roll_number"] for row in matched]
    return len(shortlist_rows)


def setup_django(db_path: str):
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["DEBUG"] = "True"

    import django

    django.setup()

    from django.core.management import call_command

    call_command("migrate", run_syncdb=True, verbosity=0, interactive=False)


def load_dataset(rows: list[dict]):
    from placements.models import Student, Company

    Student.objects.all().delete()
    Company.objects.all().delete()

    students = [
        Student(
            name=row["name"],
            roll_number=row["roll_number"],
            email=row["email"],
            cgpa=row["cgpa"],
            backlogs=row["backlogs"],
            branch=row["branch"],
            skills=row["skills"],
            graduation_year=row["graduation_year"],
        )
        for row in rows
    ]
    Student.objects.bulk_create(students, batch_size=1000)

    company = Company.objects.create(
        name="Benchmark Company",
        min_cgpa=COMPANY_RULES["min_cgpa"],
        max_backlogs=COMPANY_RULES["max_backlogs"],
        eligible_branches=COMPANY_RULES["eligible_branches"],
        required_skills=COMPANY_RULES["required_skills"],
        eligible_year=COMPANY_RULES["eligible_year"],
    )
    return company


def benchmark_size(rows: list[dict], repeats: int) -> dict:
    from placements.models import Shortlist, SystemLog
    from placements.services.eligibility_engine import run_eligibility_engine

    company = load_dataset(rows)

    automated_times = []
    automated_counts = []
    manual_times = []
    manual_counts = []

    for _ in range(repeats):
        # Reset generated output so every timed automated run creates the same
        # kind of shortlist workload. Resetting is outside the timed interval.
        Shortlist.objects.all().delete()
        SystemLog.objects.all().delete()

        start = time.perf_counter()
        result = run_eligibility_engine(company=company, user=None)
        automated_times.append(time.perf_counter() - start)
        automated_counts.append(result["eligible_students"])

        start = time.perf_counter()
        manual_count = manual_style_filter(rows)
        manual_times.append(time.perf_counter() - start)
        manual_counts.append(manual_count)

    if len(set(automated_counts)) != 1 or len(set(manual_counts)) != 1:
        raise RuntimeError("Eligibility results changed between benchmark repetitions")
    if automated_counts[0] != manual_counts[0]:
        raise RuntimeError(
            f"Benchmark mismatch: automated={automated_counts[0]} manual={manual_counts[0]}"
        )

    automated = statistics.median(automated_times)
    manual = statistics.median(manual_times)
    saved = manual - automated
    improvement = (saved / manual * 100.0) if manual else 0.0

    return {
        "dataset_size": len(rows),
        "baseline_manual_style_seconds": manual,
        "automated_seconds": automated,
        "time_saved_seconds": saved,
        "percentage_improvement": improvement,
        "eligible_students": automated_counts[0],
        "repeats": repeats,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=REPEATS)
    parser.add_argument("--output", type=Path, default=ROOT / "benchmarks" / "results.csv")
    args = parser.parse_args()

    if args.repeats < 1:
        raise SystemExit("--repeats must be >= 1")

    with tempfile.TemporaryDirectory(prefix="placement-benchmark-") as tmp:
        db_path = str(Path(tmp) / "benchmark.sqlite3")
        setup_django(db_path)

        results = []
        for size in SIZES:
            print(f"Benchmarking {size:,} students ({args.repeats} repetitions)...", flush=True)
            results.append(benchmark_size(generate_rows(size), args.repeats))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print("\nRESULTS")
    print("dataset_size,baseline_manual_style_seconds,automated_seconds,time_saved_seconds,percentage_improvement,eligible_students,repeats")
    for row in results:
        print(
            f"{row['dataset_size']},{row['baseline_manual_style_seconds']:.6f},"
            f"{row['automated_seconds']:.6f},{row['time_saved_seconds']:.6f},"
            f"{row['percentage_improvement']:.2f},{row['eligible_students']},{row['repeats']}"
        )


if __name__ == "__main__":
    main()
