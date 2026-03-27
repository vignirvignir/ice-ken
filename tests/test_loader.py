from pathlib import Path

import pytest

from ice_ken.loaders import parse_einstaklingar_xml, validate_records, main


REPO_ROOT = Path(__file__).resolve().parents[1]
SAMPLE_XML = REPO_ROOT / "data" / "Thjordska-Gervigogn-VartolulausarKennitolur.xml"


def test_parse_and_validate_sample_xml():
    records = parse_einstaklingar_xml(SAMPLE_XML)
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


def test_wrong_root_element(tmp_path):
    xml_file = tmp_path / "wrong_root.xml"
    xml_file.write_text("<People><Person/></People>", encoding="utf-8")
    with pytest.raises(ValueError, match="Unexpected root element"):
        parse_einstaklingar_xml(xml_file)


def test_empty_einstaklingar(tmp_path):
    xml_file = tmp_path / "empty.xml"
    xml_file.write_text("<Einstaklingar/>", encoding="utf-8")
    records = parse_einstaklingar_xml(xml_file)
    assert records == []


def test_missing_fields_yield_none(tmp_path):
    xml_file = tmp_path / "missing.xml"
    xml_file.write_text(
        "<Einstaklingar>"
        "  <Einstaklingur>"
        "    <Kennitala>1234567890</Kennitala>"
        "    <Nafn></Nafn>"
        "  </Einstaklingur>"
        "</Einstaklingar>",
        encoding="utf-8",
    )
    records = parse_einstaklingar_xml(xml_file)
    assert len(records) == 1
    assert records[0]["Kennitala"] == "1234567890"
    assert records[0]["Nafn"] is None  # empty element → None


def test_nil_attribute_yields_none(tmp_path):
    xml_file = tmp_path / "nil.xml"
    xml_file.write_text(
        '<Einstaklingar>'
        '  <Einstaklingur>'
        '    <Kennitala>1234567890</Kennitala>'
        '    <Nafn xsi:nil="true" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>'
        '  </Einstaklingur>'
        '</Einstaklingar>',
        encoding="utf-8",
    )
    records = parse_einstaklingar_xml(xml_file)
    assert records[0]["Nafn"] is None


def test_validate_records_with_invalid_kennitala():
    records = [{"Kennitala": "invalid"}, {"Kennitala": ""}]
    validated = validate_records(records)
    assert len(validated) == 2
    for rec in validated:
        val = rec["validation"]
        assert val["relaxed"] is False
        assert val["strict"] is False
        assert val["entity_type"] is None
        assert val["birth_date"] is None


def test_file_not_found_raises():
    with pytest.raises(FileNotFoundError):
        parse_einstaklingar_xml("/nonexistent/path.xml")


def test_malformed_xml_raises(tmp_path):
    xml_file = tmp_path / "bad.xml"
    xml_file.write_text("<Einstaklingar><broken", encoding="utf-8")
    with pytest.raises(Exception):
        parse_einstaklingar_xml(xml_file)


def test_main_stdout(capsys):
    ret = main([str(SAMPLE_XML)])
    assert ret == 0
    captured = capsys.readouterr()
    assert '"Einstaklingar"' in captured.out
    assert '"validation"' in captured.out


def test_main_output_file(tmp_path):
    out_file = tmp_path / "out.json"
    ret = main([str(SAMPLE_XML), "--out", str(out_file)])
    assert ret == 0
    assert out_file.exists()
    import json
    data = json.loads(out_file.read_text(encoding="utf-8"))
    assert "Einstaklingar" in data
    assert len(data["Einstaklingar"]) == 6


def test_main_mask_flag(capsys):
    ret = main([str(SAMPLE_XML), "--mask"])
    assert ret == 0
    captured = capsys.readouterr()
    # Masked output should contain asterisks and no full 10-digit kennitalas
    assert "******" in captured.out
