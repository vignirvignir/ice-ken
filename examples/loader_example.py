"""
Example: parse and validate the provided synthetic XML dataset.

Run from the repo root after installing the package in editable mode:

    python examples/loader_example.py

This mirrors the CLI behavior of `python -m ice_ken.loaders` but lets you
work with the Python API directly.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

from ice_ken.loaders import parse_einstaklingar_xml, validate_records


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    xml_path = repo_root / "data" / "Thjordska-Gervigogn-VartolulausarKennitolur.xml"

    if not xml_path.exists():
        print(f"XML file not found at {xml_path}")
        print("Please ensure you are running from the project root.")
        return

    print(f"Reading sample XML: {xml_path}")
    records: List[Dict[str, Any]] = parse_einstaklingar_xml(xml_path)
    print(f"Parsed {len(records)} raw records")

    validated = validate_records(records)
    print(f"Validated {len(validated)} records. Showing first 3:\n")

    for rec in validated[:3]:
        kt = rec.get("Kennitala")
        name = rec.get("Nafn") or rec.get("FulltNafn") or rec.get("NafnFullt") or "<name unknown>"
        v = rec.get("validation", {})
        print(f"- {name} :: {kt}")
        print(
            f"  relaxed={v.get('relaxed')} strict={v.get('strict')} is_dataset={v.get('is_dataset')} entity={v.get('entity_type')} birth_date={v.get('birth_date')}"
        )

    print("\nTip: You can also use the CLI directly:")
    print("  python -m ice_ken.loaders data/Thjordska-Gervigogn-VartolulausarKennitolur.xml --out validated.json")


if __name__ == "__main__":
    main()
