# Examples

Real outputs of `aerodoc ask` generated on 2026-11-17 with `configs/default.yaml` (regenerate with `uv run python scripts/make_examples.py`).

## 1. Directive by number

**Question:** Which airplanes are affected by AD 2026-18-03 and what is the unsafe condition?

**Answer:**

AD 2026-18-03 applies to Model A318-112; Model A319-115, -132, -133; Model A320-214, -216, -232, -233, -251N, -271N; and Model A321-211, -213, -231, -271N, -251NX, -253NX, and -271NX airplanes [4]. The unsafe condition is fatigue damage of the main landing gear (MLG) support rib 5, a safe-life principal structural element (PSE), which could result in structural failure and subsequent collapse of the MLG [1][3][4]. This condition was prompted by tool mark damage in the bore of the forward and aft lugs of the MLG support rib 5 due to an improper bush removal technique used by the supplier [1][4].

**Sources cited:**

- [4] [AD 2026-18-03, Dates / Background, FR page 56575](https://www.federalregister.gov/documents/2026/09/03/2026-18052/airworthiness-directives-airbus-sas-airplanes)
- [1] [AD 2026-18-03, (d) Subject / (e) Unsafe Condition / (f) Compliance, FR page 56578](https://www.federalregister.gov/documents/2026/09/03/2026-18052/airworthiness-directives-airbus-sas-airplanes)
- [3] [AD 2026-18-03, Justification for Immediate Adoption and Determination of the Effective Date, FR page 56577](https://www.federalregister.gov/documents/2026/09/03/2026-18052/airworthiness-directives-airbus-sas-airplanes)

_Model gemini-3.1-flash-lite, 21.7 s, 1603 + 221 tokens._

## 2. Handbook

**Question:** How should a portable fire extinguisher be inspected?

**Answer:**

Fire extinguishers should be checked periodically using a checklist [1]. If a checklist is unavailable, the following items must be checked as a minimum:
* Proper location of the appropriate extinguisher [1]
* Safety seals are unbroken [1]
* All external dirt and rust are removed [1]
* The gauge or indicator is in the operable range [1]
* Proper weight [1]
* No nozzle obstruction [1]
* No obvious damage [1]

**Sources cited:**

- [1] [FAA-H-8083-30B, Chapter 1: Safety, Ground Operations, & Servicing > Inspection of Fire Extinguishers, page 1-7](https://www.faa.gov/regulations_policies/handbooks_manuals/aviation)

_Model gemini-3.1-flash-lite, 8.2 s, 1908 + 97 tokens._

## 3. Directive by topic

**Question:** What problem was found on the ATR 72 nose landing gear drag brace panels, and which part numbers are affected?

**Answer:**

The nose landing gear (NLG) drag brace panels (DBP) were affected by a quality deficiency that was not detected in production, which could lead to NLG DBP dissymmetry at the lower area [1][3]. This condition might affect the structural strength of the NLG DBP and could lead to structural fatigue failure and subsequent collapse of the NLG [1][3]. The affected part numbers are P/N D63757 and P/N D69085 [1][3].

**Sources cited:**

- [1] [AD 2023-17-01, (d) Subject / (e) Unsafe Condition, FR page 63008](https://www.federalregister.gov/documents/2023/09/14/2023-19900/airworthiness-directives-atr-gie-avions-de-transport-rgional-airplanes)
- [3] [AD 2023-17-01, Dates / Background, FR page 63007](https://www.federalregister.gov/documents/2023/09/14/2023-19900/airworthiness-directives-atr-gie-avions-de-transport-rgional-airplanes)

_Model gemini-3.1-flash-lite, 6.2 s, 1570 + 105 tokens._

## 4. Partly outside the corpus

**Question:** What are the detailed inspection steps required by EASA AD 2026-0142?

**Answer (abstained):** I don't know based on the available documents. The provided passages do not contain information regarding EASA AD 2026-0142.

**Passages retrieved (none cited):**

- [1] [AD 2026-20-05, Material Incorporated by Reference Under 1 CFR Part 51, FR page 62305](https://www.federalregister.gov/documents/2026/10/01/2026-20119/airworthiness-directives-airbus-sas-airplanes)
- [2] [AD 2026-07-11, Material Incorporated by Reference Under 1 CFR Part 51, FR page 19071](https://www.federalregister.gov/documents/2026/04/14/2026-07183/airworthiness-directives-airbus-sas-airplanes)
- [3] [AD 2026-14-04, Material Incorporated by Reference Under 1 CFR Part 51, FR page 42647](https://www.federalregister.gov/documents/2026/07/10/2026-13982/airworthiness-directives-airbus-sas-airplanes)
- [4] [AD 2024-03-03, Related Service Information Under 1 CFR Part 51 / Interim Action, FR page 17717](https://www.federalregister.gov/documents/2024/03/12/2024-05190/airworthiness-directives-airbus-sas-airplanes)
- [5] [AD 2025-10-12, Material Incorporated by Reference Under 1 CFR Part 51, FR page 22458](https://www.federalregister.gov/documents/2025/05/28/2025-09515/airworthiness-directives-airbus-sas-airplanes)

_Model gemini-3.1-flash-lite, 3.4 s, 1192 + 29 tokens._

## 5. Outside the corpus

**Question:** What is the maximum takeoff weight of the Airbus A350-1000?

**Answer (abstained):** I don't know based on the available documents. The provided passages do not contain information regarding the Airbus A350-1000.

**Passages retrieved (none cited):**

- [1] [FAA-H-8083-30B, Chapter 6: Aircraft Weight & Balance > Scales, page 6-10](https://www.faa.gov/regulations_policies/handbooks_manuals/aviation)
- [2] [FAA-H-8083-30B, Chapter 14: Human Factors > Glossary, page G-7](https://www.faa.gov/regulations_policies/handbooks_manuals/aviation)
- [3] [FAA-H-8083-30B, Chapter 6: Aircraft Weight & Balance > Example Loading of an Airplane, page 6-19](https://www.faa.gov/regulations_policies/handbooks_manuals/aviation)
- [4] [FAA-H-8083-30B, Chapter 6: Aircraft Weight & Balance > Maximum Weight / Chapter 6: Aircraft Weight & Balance > Minimum Fuel, page 6-3](https://www.faa.gov/regulations_policies/handbooks_manuals/aviation)
- [5] [FAA-H-8083-30B, Chapter 6: Aircraft Weight & Balance > Maximum Weight, page 6-3](https://www.faa.gov/regulations_policies/handbooks_manuals/aviation)

_Model gemini-3.1-flash-lite, 13.9 s, 2178 + 27 tokens._

## 6. Question in French

**Question:** Quels avions sont concernés par l'AD 2026-18-03 ?

**Answer:**

L'AD 2026-18-03 s'applique aux modèles d'avions Airbus SAS suivants :

*   Model A318-112 [2][5]
*   Model A319-115, -132 et -133 [2][5]
*   Model A320-214, -216, -232, -233, -251N et -271N [2][5]
*   Model A321-211, -213, -231, -271N, -251NX, -253NX et -271NX [2][5]

Ces avions sont également identifiés dans l'EASA AD 2026-0142 [2].

**Sources cited:**

- [2] [AD 2026-18-03, The Amendment / PART 39--AIRWORTHINESS DIRECTIVES / Sec.  39.13   [Amended] / (a) Effective Date / (b) Affected ADs / (c) Applicability, FR page 56577](https://www.federalregister.gov/documents/2026/09/03/2026-18052/airworthiness-directives-airbus-sas-airplanes)
- [5] [AD 2026-18-03, 14 CFR Part 39 / Summary, FR page 56575](https://www.federalregister.gov/documents/2026/09/03/2026-18052/airworthiness-directives-airbus-sas-airplanes)

_Model gemini-3.1-flash-lite, 12.1 s, 2032 + 192 tokens._
