from pathlib import Path

from ice_ken.loaders import parse_einstaklingar_xml, validate_records


def test_parse_and_validate_sample_xml():
    repo_root = Path(__file__).resolve().parents[1]
    xml_path = repo_root / "data" / "Thjordska-Gervigogn-VartolulausarKennitolur.xml"

    records = parse_einstaklingar_xml(xml_path)
    # Expect 6 records per the sample file
    assert isinstance(records, list)
    assert len(records) == 6

    validated = validate_records(records)
    assert len(validated) == 6

    for rec in validated:
        kt = rec.get("Kennitala")
        val = rec.get("validation", {})
        assert val.get("relaxed") is True
        # In this sample file, kennitalas are without checksum; strict should be False
        assert val.get("strict") is False
        # dataset marker (14/15 in positions 7–8) not used in this file
        assert val.get("is_dataset") is False
        # birth_date parsed from kennitala should be present
        assert val.get("birth_date") is not None
