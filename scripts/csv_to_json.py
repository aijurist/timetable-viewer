"""Install scheduler CSV exports as static timetable-viewer data.

The viewer intentionally consumes JSON so it can be hosted without FastAPI. The
source CSV files are retained beside the JSON for auditability.
"""

from __future__ import annotations

import argparse
import json
import shutil
from pathlib import Path

import pandas as pd


REQUIRED_THEORY_COLUMNS = {
    "day",
    "time_slot",
    "slot_index",
    "course_instance_id",
    "course_code",
    "teacher_id",
    "room_number",
    "schedule_type",
    "department",
    "semester",
}
REQUIRED_LAB_COLUMNS = {
    "day",
    "session_name",
    "time_range",
    "course_instance_id",
    "course_code",
    "teacher_id",
    "room_number",
    "schedule_type",
    "department",
    "semester",
}


def _load_csv(path: Path, required_columns: set[str]) -> pd.DataFrame:
    if not path.is_file():
        raise FileNotFoundError(path)
    frame = pd.read_csv(path)
    missing = sorted(required_columns - set(frame.columns))
    if missing:
        raise ValueError(f"{path.name} is missing required columns: {missing}")
    return frame


def _write_json(frame: pd.DataFrame, path: Path) -> None:
    # Pandas' JSON encoder converts NaN to standards-compliant null values while
    # preserving inferred booleans and numeric section/slot fields.
    records = json.loads(frame.to_json(orient="records", force_ascii=False))
    path.write_text(
        json.dumps(records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _copy_if_needed(source: Path, destination: Path) -> None:
    """Copy an export into the viewer unless it is already the canonical file."""
    if source.resolve() != destination.resolve():
        shutil.copy2(source, destination)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "theory_csv",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data/theory_schedule_second_year.csv",
    )
    parser.add_argument(
        "lab_csv",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data/lab_schedule_second_year.csv",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "data",
    )
    args = parser.parse_args()

    theory = _load_csv(args.theory_csv, REQUIRED_THEORY_COLUMNS)
    lab = _load_csv(args.lab_csv, REQUIRED_LAB_COLUMNS)
    args.output_dir.mkdir(parents=True, exist_ok=True)

    theory_json = args.output_dir / "theory_schedule.json"
    lab_json = args.output_dir / "lab_schedule.json"
    _write_json(theory, theory_json)
    _write_json(lab, lab_json)

    theory_csv_copy = args.output_dir / "theory_schedule_second_year.csv"
    lab_csv_copy = args.output_dir / "lab_schedule_second_year.csv"
    _copy_if_needed(args.theory_csv, theory_csv_copy)
    _copy_if_needed(args.lab_csv, lab_csv_copy)

    print(f"Theory schedule: {len(theory)} records -> {theory_json}")
    print(f"Lab schedule: {len(lab)} records -> {lab_json}")
    print(f"Source CSV copies: {theory_csv_copy}, {lab_csv_copy}")


if __name__ == "__main__":
    main()
