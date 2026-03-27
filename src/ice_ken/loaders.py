from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path
from typing import Any
import xml.etree.ElementTree as ET

try:
    from defusedxml.ElementTree import fromstring as _xml_fromstring
except ImportError:
    # Python's C-accelerated XMLParser (default since 3.x) does not resolve
    # external entities, so ET.fromstring is safe for untrusted input in
    # practice.  Install defusedxml for additional protections (e.g. entity
    # expansion limits).
    _xml_fromstring = ET.fromstring

from .kennitala import is_valid, is_company, is_personal, is_dataset_id, parse


def _read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sanitize_known_issues(xml_text: str) -> str:
    # Fix duplicated self-closing tag pattern observed in sample
    xml_text = re.sub(r"(<SidastaIslLogh[^>]*/>)\s*/>", r"\1", xml_text)
    return xml_text


def _is_nil(elem: ET.Element) -> bool:
    for k, v in elem.attrib.items():
        if k.endswith("nil") and v.lower() == "true":
            return True
    return False


def _text_or_none(elem: ET.Element) -> str | None:
    if _is_nil(elem):
        return None
    txt = (elem.text or "").strip()
    return txt if txt != "" else None


def parse_einstaklingar_xml(path: str | Path) -> list[dict[str, Any]]:
    path = Path(path)
    xml_text = _read_text(path)
    xml_text = _sanitize_known_issues(xml_text)
    root = _xml_fromstring(xml_text)
    if root.tag != "Einstaklingar":
        raise ValueError("Unexpected root element; expected 'Einstaklingar'")
    records: list[dict[str, Any]] = []
    for child in root.findall("Einstaklingur"):
        rec: dict[str, Any] = {}
        for field in list(child):
            # Strip namespace if any
            tag = field.tag.split("}")[-1] if "}" in field.tag else field.tag
            rec[tag] = _text_or_none(field)
        records.append(rec)
    return records


def _to_iso_date(d: date) -> str:
    return d.isoformat()


def validate_records(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for rec in records:
        kt = (rec.get("Kennitala") or "").strip()
        v_relaxed = is_valid(kt, enforce_checksum=False)
        v_strict = is_valid(kt, enforce_checksum=True)
        ds = is_dataset_id(kt)
        entity = (
            "company" if is_company(kt) else ("individual" if is_personal(kt) else None)
        )
        birth_iso: str | None = None
        if v_relaxed:
            try:
                info = parse(kt, enforce_checksum=False)
                birth_iso = _to_iso_date(info.birth_date)
            except Exception:
                birth_iso = None
        rec_out = dict(rec)
        rec_out["validation"] = {
            "relaxed": v_relaxed,
            "strict": v_strict,
            "is_dataset": ds,
            "entity_type": entity,
            "birth_date": birth_iso,
        }
        out.append(rec_out)
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(
        description="Parse and validate gervigögn Einstaklingar XML"
    )
    p.add_argument("xml", type=str, help="Path to Einstaklingar XML file")
    p.add_argument(
        "--out", type=str, default=None, help="Write validated JSON to this path"
    )
    args = p.parse_args(argv)

    records = parse_einstaklingar_xml(args.xml)
    validated = validate_records(records)
    if args.out:
        out_path = Path(args.out)
        out_path.write_text(
            json.dumps({"Einstaklingar": validated}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        print(f"Wrote {out_path}")
    else:
        print(json.dumps({"Einstaklingar": validated}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
