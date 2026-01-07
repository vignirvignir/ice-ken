# Gervigögn XML Data Files — Structure and Mapping

This document explains the structure of the two XML files under `data/` and how they were converted into JSON for easier consumption in tests and tooling.

## Data Source

The synthetic datasets are obtained from Registers Iceland (Þjóðskrá Íslands):
<https://www.skra.is/gogn/gervigogn-thjodskrar/>

- Source files:
  - `data/Thjordska-Gervigogn-VartolulausarKennitolur.xml`
- Output JSON files:
  - `data/kennitala-without-checksum.json`

## 1) Thjordska-Gervigogn-VartolulausarKennitolur.xml

- Root element: `Einstaklingar`
- Child element: repeated `Einstaklingur`
- Namespace usage: some elements include `xsi:nil="true"` (XML Schema Instance), which are mapped to JSON `null`.

Each `Einstaklingur` node contains the following fields (Icelandic names kept to match the schema):

- `Stada`: Status code (e.g., `E`).
- `Kennitala`: The synthetic kennitala (10 digits). In this dataset, IDs may not satisfy Mod 11.
- `FjolskylduNumer`: Family number (often same as `Kennitala` in this dataset).
- `Logheimili` / `Logheimili112`: Residence identifiers.
- `Kyn`: Gender code (numeric; dataset-specific coding).
- `Hjuskapastada`: Marital status code.
- `Bannmerking`: Suppression/ban marker; `null` when not set.
- `Rikisfang`: Nationality (ISO alpha-2, e.g., `IS`).
- `Faedingarstadur`: Birthplace code.
- `FaedD`: Birth date-time in ISO-like string (e.g., `YYYY-MM-DDTHH:MM:SS`).
- `Nafn`: Name; synthetic names clearly include the uppercase letters `ÞÍ` as a dataset marker.
- `Birtingarnafn`: Display name; often `null`.
- `MakiKt`: Spouse kennitala; often `null`.
- `Adsetur`: Address/abode; `null` when absent.
- `DagsNyskraningar`: Registration date; `null` when absent.
- `SidastaIslLogh`: Last Icelandic legal domicile; `null` when absent.
- `Umbodsmadur`: Agent/representative; `null` when absent.
- `Kennitolubeidandi`: Kennitala requester; `null` when absent.
- `PostNr`: Postal code (e.g., `101`).
- `HeimiliNefnifall` / `HeimiliThagufall`: Declension forms of the home name.
- `Sveitarfelag`: Municipality code.
- `SkattSveitarfelag`: Tax municipality; `null` when absent.
- `DagsAndlat`: Date of death; `null` when absent.
- `UppfDT`: Update timestamp.
- `IbudNr`: Apartment number; `null` when absent.
- `Logheimilisforeldri` / `Busetuforeldri`: Parental residence markers; `null` when absent.

Notes:

- The file contains well-formed entries, but one line shows a minor XML typo (`<SidastaIslLogh xsi:nil="true" />/>`). During JSON preparation we treated it as `null`.
- Although some official synthetic datasets distinguish kennitalas by placing `14` or `15` in digits 7–8, the IDs in this particular file do not necessarily follow that convention. Use `is_dataset_id()` only when specifically working with the official dataset that uses this marker.

## Usage Suggestions

- For quick checks of kennitala shape and test-only dataset markers, use the helpers in this repository:
  - `is_valid(value, enforce_checksum=False)` for relaxed structural/date validation.
  - `is_dataset_id(value)` to detect the official Gervigögn dataset marker (positions 7–8 == `14` or `15`).
- Do not rely on dataset conventions (like the `14/15` marker) in production logic.
