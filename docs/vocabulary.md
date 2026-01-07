# Vocabulary — Icelandic-English Technical Terms

This vocabulary provides precise translations and definitions for developers and LLMs working with Icelandic national identification systems. Terms are organized alphabetically by English equivalent.

## A

**Aðsetur** (n.) — Address, abode  
*Legal residence or dwelling place*

**Agent** — See Umboðsmaður

## B

**Bannmerking** (n.) — Suppression marker, ban marker
*Indicator that individual has been marked in the national registry to avoid cold-calling*

**Birth date** — See Fæðingarstaður, FaedD

**Birtingarnafn** (n.) — Display name  
*Official name used for public display or formal documents*

**Búsetuforeldri** (n.) — Residence parent  
*Parent or guardian responsible for residence determination*

## C

**Century indicator** — Aldartala  
*10th digit of kennitala: 8=1800s, 9=1900s, 0=2000s*

**Check digit** — Vartala
*9th digit of kennitala computed using Modulus 11 algorithm*

**Checksum** — Gátsumma
*Mathematical validation using Modulus 11 algorithm*

**Company kennitala** — Fyrirtækjakennitala  
*Kennitala for legal entities other than individuals with day field DD=41-71 (day+40 rule)*

## D

**DagsAndlat** (n.) — Date of death  
*Official death registration date*

**DagsNyskraningar** (n.) — Registration date  
*Date when entry was first registered in official systems*

**Dataset ID** — Gagnagrunnsauðkenni  
*Synthetic kennitala marked with "14" or "15" in sequence positions 7 and 8*

**Day offset** — Dagavikmörk  
*Adding 40 to day field to distinguish company kennitalas*

## E

**Einstaklingur** (n.) — Individual  
*Person as opposed to legal entity or company*

**Einstaklingar** (n.) — Individuals  
*Root XML element containing multiple individual records*

**Entity type** — Tegund aðila
*Classification as "individual" or "company"*

**Enforce checksum** — Framfylgja vartölu
*Validation mode requiring Modulus 11 check digit compliance*

## F

**Fæðingarstaður** (n.) — Birthplace  
*Place of birth, typically encoded as location code*

**FaedD** (n.) — Birth date  
*Date of birth in ISO format (YYYY-MM-DDTHH:MM:SS)*

**Family number** — See FjolskylduNumer

**FjolskylduNumer / Fjölskyldunúmer** (n.) — Family number  
*Identifier linking family members, often same as kennitala but does not have to be the same*

**Format** — Snið  
*Standard kennitala presentation as DDMMYY-NNNX*

## G

**Gender code** — See Kyn

**Gervigögn** (n.) — Synthetic data  
*Official test dataset from Registers Iceland*

**Gátsumma** — See Checksum

## H

**HeimiliNefnifall** (n.) — Home name (nominative case)  
*Grammatical form of residence name in nominative*

**HeimiliThagufall** (n.) — Home name (accusative case)  
*Grammatical form of residence name in accusative*

**Hjúskapastaða** (n.) — Marital status  
*Civil status code indicating marriage, divorce, etc.*

## I

**IbudNr** (n.) — Apartment number  
*Specific unit number within building address*

**Kennitala einstaklings** — Individual kennitala
*Kennitala for persons with day field DD=01-31*

**ISO alpha-2** — ISO alfa-2  
*Two-letter country code standard (e.g., IS for Iceland)*

## K

**Kennitala** (n.) — National ID number  
*10-digit Icelandic national identification number*

**Kennitolubeidandi** (n.) — Kennitala requester  
*Entity or person who requested the kennitala issuance*

**Kerfiskennitala** (n.) — System identification number  
*Special ID for non-residents staying less than 3 months*

**Kyn** (n.) — Gender  
*Gender code using dataset-specific numeric encoding*

## L

**Legal entity** — Lögaðili  
*Company, organization, or non-person entity*

**Lögheimili** (n.) — Legal domicile  
*Official residence for legal purposes*

**Logheimili112** (n.) — Legal domicile (emergency services format)  
*Residence identifier compatible with emergency services*

**Lögheimilisforeldri** (n.) — Legal domicile parent  
*Parent determining legal residence for minor*

## M

**MakiKt** (n.) — Spouse kennitala  
*Kennitala of married partner or spouse*

**Marital status** — See Hjúskapastaða

**Mask** — Hulumynstur  
*Hide sensitive digits for display (e.g., ******-3389)*

**Modulus 11** — Módúlus 11  
*Mathematical algorithm for check digit calculation*

**Municipality** — See Sveitarfélag

## N

**Nafn** (n.) — Name  
*Full legal name of person or entity*

**National Register** — Þjóðskrá  
*Official population register maintained by Registers Iceland*

**Nationality** — See Rikisfang

**Normalize** — Staðla  
*Remove formatting to get digits-only string*

## P

**Parse** — Þátta  
*Extract structured information from kennitala*

**Personal kennitala** — See Individual kennitala

**PostNr** (n.) — Postal code  
*Mail delivery code for geographic area*

**Vartala** — See Check digit

## R

**Registers Iceland** — Þjóðskrá Íslands  
*Government agency managing population and business registers*

**Registration date** — See DagsNyskraningar

**Slök framfylgni** — Relaxed validation
*Validation mode ignoring check digit (post-2026 policy)*

**Residence** — See Lögheimili

**Rikisfang** (n.) — Nationality  
*Country of citizenship, typically ISO alpha-2 code*

## S

**Raðtölur** — Sequence digits
*Digits 7-8 of kennitala, typically starting from 20*

**SidastaIslLogh** (n.) — Last Icelandic legal domicile  
*Most recent legal residence within Iceland*

**SkattSveitarfelag** (n.) — Tax municipality  
*Municipal jurisdiction for taxation purposes*

**Staða** (n.) — Status  
*Current registration status (e.g., "E" for active)*

**Strict validation** — Ströng staðfesting  
*Validation mode enforcing check digit compliance*

**Suppression marker** — See Bannmerking

**Sveitarfélag** (n.) — Municipality  
*Local government administrative division*

**Synthetic data** — See Gervigögn

**System ID** — See Kerfiskennitala

## T

**Tax municipality** — See SkattSveitarfelag

**Þjóðskrá** — See Registers Iceland

**Þjóðskrá Íslands** — See Registers Iceland

## U

**Umboðsmaður** (n.) — Agent, representative  
*Person authorized to act on behalf of another*

**UppfDT** (n.) — Update timestamp  
*Last modification date and time for record*

## V

**Validation mode** — Staðfestingarhamur  
*Method of kennitala verification (strict vs relaxed)*

## W

**Weight vector** — Vigtarvigur
*Coefficients [3,2,7,6,5,4,3,2] used in Modulus 11 calculation*

## X

**XML Schema Instance** — XML skemadæmi  
*Namespace for xsi:nil attributes indicating null values*

**xsi:nil** — XML null marker  
*Attribute indicating element has no value (maps to JSON null)*

---

## Usage Notes

1. **Gender codes (Kyn)**: Use dataset-specific documentation as encoding varies
2. **Date formats**: FaedD uses ISO format; DagsAndlat and others may be null
3. **Company identification**: Day field 41-71 indicates legal entity (subtract 40 for actual day)
4. **Dataset markers**: Synthetic kennitalas may use "ÞÍ" in names and "14"/"15" in sequence
5. **2026 policy**: New kennitalas after Feb 18, 2026 may not satisfy Modulus 11
6. **Case sensitivity**: Icelandic field names are case-sensitive in XML/JSON
7. **Null handling**: xsi:nil="true" in XML maps to JSON null values

## Common Abbreviations

- **DD** — Day (01-31 for individuals, 41-71 for companies)
- **MM** — Month (01-12)  
- **YY** — Year (two digits)
- **NNN** — Sequence digits (positions 7-8) plus check digit (position 9)
- **X** — Century indicator (position 10)
- **kt** — Common abbreviation for kennitala
- **IS** — Iceland (ISO alpha-2 country code)

## Etymology Notes

- **Kennitala** — Literally "identification number" (kennir = identifies, tala = number)
- **Kerfiskennitala** — System + identification number  
- **Gervigögn** — Artificial/synthetic + data
- **Þjóðskrá** — People's register/national register
- **Einstaklingar** — Individuals (plural of einstaklingur)
