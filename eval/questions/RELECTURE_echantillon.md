# Relecture d'un échantillon de 20 questions (sur 73)

Jeu complet : `eval/questions/dev.jsonl` (45) et `test.jsonl` (28). 47 questions ont été générées par le LLM à partir de passages tirés au hasard, puis filtrées automatiquement et relues par Claude (19 retirées car ambiguës, mots-clés assouplis : `scripts/curate_questions.py`). 26 ont été écrites à la main (cas difficiles et 16 questions sans réponse).

Pour chaque question : **est-elle claire et réaliste ? la réponse attendue est-elle juste (voir le passage) ? les mots-clés sont-ils raisonnables ?** (`a|b` = a ou b ; une réponse est juste si elle contient chaque mot-clé).

Réponds par exemple : « OK », ou « g21 : supprimer », « h07 : trop dur mais à garder ».

### g10 · consigne par numéro · dev

**Question :** What specific structural failure is AD 2022-25-15 intended to prevent in the affected Boeing 737 fleet?

- Réponse attendue : The directive aims to mitigate the risk of the wing rear spar lower chord failing to support required load limits, which could compromise airframe stability and lead to potential loss of flight control.
- Mots-clés exigés : `structural integrity`, `loss of control`
- Source : [AD 2022-25-15](https://www.federalregister.gov/documents/2022/12/22/2022-27751/airworthiness-directives-the-boeing-company-airplanes)
- Passage source : <details><summary>afficher</summary>

> This AD is effective January 26, 2023. The Director of the Federal Register approved the incorporation by reference of a certain publication listed in this AD as of January 26, 2023. The FAA issued a notice of proposed rulemaking (NPRM) to amend 14 CFR part 39 by adding an AD that would apply to all The Boeing Company Model 737-100, -200, -200C, -300, -400, and -500 series airplanes. The NPRM published in the Federal Register on September 8, 2022 (87 FR 54922). The NPRM was prompted by a report indicating that a crack was found in one of the holes of the wing rear spar lower chord at the MLG aft fitting at WBL 157 on a Model 737-400 airplane. In the NPRM, the FAA proposed to require repetitive open hole HFEC inspections or surface HFEC and UT inspections for cracking of the wing rear spar lower chord at the MLG aft fitting at a certain WBL, and applicable on- condition actions. The FAA is issuing this AD to address cracking in the rear spar lower chord at a fastener common to the MLG aft support fitting. This condition, if not addressed, could result in the inability of the rear spar lower chord to sustain limit loads, resulting in reduced structural integrity of the airplane and possible loss of control of the airplane.

</details>

### g14 · consigne par sujet · test

**Question :** What specific structural failure on B737 primary exhaust nozzles necessitates corrective action to prevent potential fuselage or stabilizer impact during a fan blade-out incident?

- Réponse attendue : The primary exhaust nozzles must be strengthened because existing units are prone to detaching during engine blade-out events, which poses a risk of striking the aircraft's tail or cabin area.
- Mots-clés exigés : `strengthen`
- Source : [AD 2025-04-03](https://www.federalregister.gov/documents/2025/03/04/2025-03396/airworthiness-directives-the-boeing-company-airplanes)
- Passage source : <details><summary>afficher</summary>

> Air Transport Association (ATA) of America Code 78, Exhaust. This AD was prompted by two engine fan blade-out (FBO) events that resulted in the separation of engine inlet cowl and fan cowl parts from the airplane damaging the fuselage, which caused loss of pressurization and subsequent emergency descent. The FBO events also resulted in cracks in the primary exhaust nozzle, which could result in the departure of the primary exhaust nozzle. The FAA is issuing this AD to address primary exhaust nozzles that are not strengthened, which during an FBO event, could depart the engine, potentially damaging a stabilizer or striking the fuselage and window. The unsafe condition, if not addressed, could result in loss of control of the airplane, or in a rapid decompression and hazard to window-seated passengers aft of the wing.

</details>

### g15 · consigne par numéro · test

**Question :** What specific operational issue prompted the issuance of AD 2023-13-03 regarding the external door handle assembly?

- Réponse attendue : The directive was initiated because the external handle flap could become stuck in a non-flush position, which in one instance prevented the door from being opened from the interior.
- Mots-clés exigés : `stuck`
- Source : [AD 2023-13-03](https://www.federalregister.gov/documents/2023/07/31/2023-16095/airworthiness-directives-airbus-sas-airplanes)
- Passage source : <details><summary>afficher</summary>

> This AD is effective September 5, 2023. The Director of the Federal Register approved the incorporation by reference of a certain publication listed in this AD as of September 5, 2023. The FAA issued a notice of proposed rulemaking (NPRM) to amend 14 CFR part 39 by adding an AD that would apply to all Airbus SAS Model A318-111, A318-112, A318-121, A318-122, A319-111, A319-112, A319-113, A319-114, A319-115, A319-131, A319-132, A319-133, A319-151N, A319-153N, A319-171N, A320-211, A320-212, A320-214, A320-216, A320-231, A320-232, A320-233, A320-251N, A320-252N, A320-253N, A320-271N, A320-272N, A320- 273N, A321-111, A321-112, A321-131, A321-211, A321-212, A321-213, A321- 231, A321-232, A321-251N, A321-251NX, A321-252N, A321-252NX, A321-253N, A321-253NX, A321-271N, A321-271NX, A321-272N, and A321-272NX airplanes. The NPRM published in the Federal Register on March 8, 2023 (88 FR 14298). The NPRM was prompted by AD 2022-0213R1, dated November 8, 2022, issued by EASA, which is the Technical Agent for the Member States of the European Union (EASA AD 2022-0213R1) (also referred to as the MCAI). The MCAI states one operator has reported two cases of a passenger/flight crew door external handle flap remained stuck in an intermediate or fully pushed position (not flush with the door skin) on two recently delivered Model A320 series airplanes after the door was opened from outside. With the external handle flap in this intermediate position, in one of the reported cases, the operator was not able to open the door normally from inside. Subsequent investigation determined that on the production line of one door supplier, corrosion protection compound (CPC) was inadvertently

</details>

### g17 · consigne par numéro · dev

**Question :** What specific safety hazard does AD 2023-23-08 aim to prevent regarding the 10VU rack?

- Réponse attendue : The directive addresses potential visual impairment of essential flight data for pilots during takeoff or landing, which could lead to an inability to maintain safe aircraft control.
- Mots-clés exigés : `read`, `loss of control|loss of airplane control`
- Source : [AD 2023-23-08](https://www.federalregister.gov/documents/2023/12/01/2023-26404/airworthiness-directives-airbus-sas-airplanes)
- Passage source : <details><summary>afficher</summary>

> Agent for the Member States of the European Union (EASA AD 2022-0266) (also referred to as the MCAI). The MCAI states that during an unscheduled maintenance operation on an A330 airplane, the 10VU rack was removed for access, and cracks were discovered on 10VU rack side fittings on lugs 1, 3, and 4. As a similar design is installed on A320 family airplanes, a sampling review was done to determine the possible fleet impact. The result showed that several airplanes had cracked or broken 10VU rack side fittings. This condition, if not detected and corrected, could lead to a high vibration level on the primary flight and navigation displays during critical flight phases (take-off and landing), possibly creating reading difficulties for the crew. In the NPRM, the FAA proposed to continue to require repetitive inspections for cracking of the 10VU rack fitting lugs, and repair of any cracking. In the NPRM, the FAA also proposed to require reduced compliance times and to remove airplanes having a certain modification from the applicability. The FAA is issuing this AD to address reading difficulties of flight-critical information displayed to the flightcrew during a critical phase of flight, such as an approach or takeoff, which could result in loss of airplane control at an altitude insufficient for recovery. You may examine the MCAI in the AD docket at regulations.gov under Docket No. FAA-2023-1409.

</details>

### g21 · consigne par sujet · dev

**Question :** What specific structural concern regarding the FR 96 foot radius on Airbus A350-941 aircraft necessitates fastener removal and inspection?

- Réponse attendue : The issue involves insufficient clearance between the installed nut and the foot radius, which can lead to structural damage that compromises the airframe's integrity.
- Mots-clés exigés : `interference`, `stringer`
- Source : [AD 2023-03-07](https://www.federalregister.gov/documents/2023/02/27/2023-03694/airworthiness-directives-airbus-sas-airplanes)
- Passage source : <details><summary>afficher</summary>

> This AD is effective April 3, 2023. The Director of the Federal Register approved the incorporation by reference of a certain publication listed in this AD as of April 3, 2023. The FAA issued a notice of proposed rulemaking (NPRM) to amend 14 CFR part 39 by adding an AD that would apply to certain Airbus SAS Model A350-941 airplanes. The NPRM published in the Federal Register on November 25, 2022 (87 FR 72414). The NPRM was prompted by AD 2022-0093, dated May 25, 2022, issued by EASA, which is the Technical Agent for the Member States of the European Union (EASA AD 2022-0093) (also referred to as the MCAI). The MCAI states that an interference was detected between the installed nut and the foot radius of FR 96, between stringer 6 and stringer 7, on the right-hand side. Further investigation showed that the minimum distances for nut installation were not fulfilled, and some airplanes were damaged in the FR 96 foot radius area. Damage at the FR 96 foot radius area, if not addressed, may affect the structural integrity of the airplane. In the NPRM, the FAA proposed to require removing the affected fasteners and inspecting the affected area for damage, and applicable corrective actions if necessary, as specified in EASA AD 2022-0093. The FAA is issuing this AD to address possible damage at the FR 96 foot radius area. This condition, if not addressed, may affect the structural integrity of the airplane. You may examine the MCAI in

</details>

### g23 · consigne par numéro · dev

**Question :** What specific maintenance actions are mandated by AD 2026-05-12 to resolve the identification issues with the main landing gear hardware?

- Réponse attendue : Technicians must verify the identification markings, document the work order and original serial numbers as the updated identifier, and revise the relevant service logs.
- Mots-clés exigés : `inspect`, `record`
- Source : [AD 2026-05-12](https://www.federalregister.gov/documents/2026/03/12/2026-04830/airworthiness-directives-airbus-sas-airplanes)
- Passage source : <details><summary>afficher</summary>

> [Docket No. FAA-2026-2291; Project Identifier MCAI-2026-00074-T; Amendment 39-23285; AD 2026-05-12] RIN 2120-AA64 The FAA is adopting a new airworthiness directive (AD) for certain Airbus SAS Model A350-941 airplanes. This AD was prompted by a report of a non-conformity in the serialization process of certain fuse pins and retaining pins installed in the main landing gear (MLG) trunnion block attachment, resulting in a non-unique combination of part number and serial number that could lead to a lack of traceability. This AD requires doing a check to identify the part number and serial number of the affected parts. This AD also requires inspecting the affected MLG trunnion block attachment retaining pin and fuse pins, recording the combination of work order number and original serial number as the new serial number, and updating the maintenance records, as applicable. The FAA is issuing this AD to address the unsafe condition on these products.

</details>

### g24 · consigne par numéro · dev

**Question :** What specific technical concern regarding 5G signals triggered the issuance of AD 2021-23-12?

- Réponse attendue : The directive was initiated because radio altimeters might fail to operate correctly due to signal disruption from wireless broadband networks operating in the 5G Lower C-Band.
- Mots-clés exigés : `radio altimeter`, `interference`
- Source : [AD 2026-13-13](https://www.federalregister.gov/documents/2026/06/30/2026-13206/airworthiness-directives-the-boeing-company-airplanes)
- Passage source : <details><summary>afficher</summary>

> This AD is effective July 1, 2026. The FAA must receive comments on this AD by August 14, 2026. The FAA issued AD 2021-23-12, Amendment 39-21810 (86 FR 69984, December 9, 2021) (AD 2021-23-12), for all transport and commuter category airplanes equipped with a radio altimeter. AD 2021-23-12 was prompted by a determination that radio altimeters cannot be relied upon to perform their intended function if they experience interference from wireless broadband operations in the 5G Lower C-Band, which is close to the frequency bands used by radio altimeters (4.2-4.4 GHz). AD 2021-23- 12 required revising the limitations section of the existing AFM to incorporate limitations prohibiting certain operations requiring radio altimeter data when in the presence of 5G Lower C-Band interference as identified by Notices to Air Missions (NOTAMs). The agency issued AD 2021-23-12 because radio altimeter anomalies that are undetected by the automation or pilot, particularly close to the ground (e.g., landing flare), could lead to loss of continued safe flight and landing. The FAA subsequently identified an additional hazard presented by 5G Lower C-Band interference on Boeing Model 737-100, -200, -200C, - 300, -400, -500, -600, -700, -700C, -800, -900, and -900ER series airplanes, except for Model 737-200 and -200C series airplanes equipped with an SP-77 flight control system, and issued AD 2022-05-04, Amendment 39-21955 (87 FR 10299, February 24, 2022) (AD 2022-05-04). AD 2022-05-04 was prompted by the unsafe condition in AD 2021-23-12, as well as a determination that, during approach, landings, and go- arounds, as

</details>

### g27 · consigne par sujet · dev

**Question :** What specific maintenance tasks are required for the center wing box spars on Airbus SAS Model A350-941 and -1041 aircraft to address the updated safety concerns?

- Réponse attendue : Technicians must swap out the specified hardware and install extra protective caps on the head nuts located at the forward and aft spars.
- Mots-clés exigés : `fastener`, `cap`
- Source : [AD 2025-14-09](https://www.federalregister.gov/documents/2025/07/21/2025-13594/airworthiness-directives-airbus-sas-airplanes)
- Passage source : <details><summary>afficher</summary>

> [Docket No. FAA-2025-0345; Project Identifier MCAI-2024-00475-T; Amendment 39-23087; AD 2025-14-09] RIN 2120-AA64 The FAA is superseding Airworthiness Directive (AD) 2022-27- 01, which applied to certain Airbus SAS Model A350-941 and -1041 airplanes. AD 2022-27-01 required replacing affected fasteners and applying additional head nut cap protection at the front and rear spars in the center wing box (CWB). Since the FAA issued AD 2022-27-01, the FAA determined that additional Airbus SAS Model A350 manufacturer serial numbers (MSNs) are affected by the same potential unsafe condition. This AD continues to require the actions in AD 2022-27-01 and expands the applicability to include the additional Airbus SAS Model A350 MSNs. The FAA is issuing this AD to address the unsafe condition on these products.

</details>

### g41 · consigne par numéro · dev

**Question :** Which specific variants of the B737 fleet are subject to the requirements mandated by AD 2026-13-17?

- Réponse attendue : This directive covers the 737-8, 737-9, and 737-8200 versions of the Boeing aircraft.
- Mots-clés exigés : `737-8`, `737-9`, `8200`
- Source : [AD 2026-13-17](https://www.federalregister.gov/documents/2026/06/30/2026-13208/airworthiness-directives-the-boeing-company-airplanes)
- Passage source : <details><summary>afficher</summary>

> Accordingly, under the authority delegated to me by the Administrator, the FAA amends 14 CFR part 39 as follows: 0 1. The authority citation for part 39 continues to read as follows: Authority: 49 U.S.C. 106(g), 40113, 44701. 0 2. The FAA amends Sec. 39.13 by adding the following new airworthiness directive: 2026-13-17 The Boeing Company: Amendment 39-23400; Docket No. FAA- 2026-7208; Project Identifier AD-2026-00557-T. This airworthiness directive (AD) is effective July 1, 2026. None. This AD applies to all The Boeing Company Model 737-8, 737-9, and 737-8200 airplanes, certificated in any category.

</details>

### g42 · consigne par numéro · dev

**Question :** What specific hazard does AD 2024-23-03 aim to prevent regarding the autothrottle system?

- Réponse attendue : The directive addresses the risk of uncommanded roll and potential loss of aircraft control caused by a failure to disengage the autothrottle during asymmetric thrust events.
- Mots-clés exigés : `roll`
- Source : [AD 2024-23-03](https://www.federalregister.gov/documents/2024/12/02/2024-28134/airworthiness-directives-the-boeing-company-airplanes)
- Passage source : <details><summary>afficher</summary>

> This airworthiness directive (AD) is effective January 6, 2025. None. This AD applies to The Boeing Company Model 737-300 and -400 series airplanes, certificated in any category, as identified in Boeing Alert Requirements Bulletin 737-22A1399 RB, dated April 13, 2023. Air Transport Association (ATA) of America Code 27, Flight controls. This AD was prompted by a report that flight control rigging tolerances could result in spoiler deflection not reaching the minimal level required to engage the cruise thrust split monitor (MONFD) used by the autothrottle (A/T) system. The FAA is issuing this AD to address failure of the spoiler deflection to engage the MONFD. The unsafe condition, if not addressed, could lead to significant throttle split, leading to asymmetric thrust and the subsequent lack of autothrottle disengagement, which could result in an uncommanded roll and consequent loss of control of the airplane, and reduced ability of the flightcrew to maintain the safe flight and landing of the airplane.

</details>

### g45 · manuel · dev

**Question :** What is the primary application for natural rubber within aircraft fluid systems?

- Réponse attendue : Natural rubber is utilized as a sealing component for systems containing water and methanol.
- Mots-clés exigés : `water/methanol|water methanol|water-methanol`
- Source : Manuel, page 7-32
- Passage source : <details><summary>afficher</summary>

> core. Rubber Rubber is used to prevent the entrance of dirt, water, or air, and to prevent the loss of fluids, gases, or air. It is also used to absorb vibration, reduce noise, and cushion impact loads. The term “rubber” is as all-inclusive as the term “metal.” It is used to include not only natural rubber, but also all synthetic and silicone rubbers. Natural Rubber Natural rubber has better processing and physical properties than synthetic or silicone rubber. These properties include flexibility, elasticity, tensile strength, tear strength, and low heat buildup due to flexing (hysteresis). Natural rubber is a general-purpose product; however, its suitability for aircraft use is somewhat limited because of its inferior resistance to most influences that cause deterioration. Although it provides an excellent seal for many applications, it swells and often softens in all aircraft fuels and in many solvents (naphthas and so forth). Natural rubber deteriorates more rapidly than synthetic rubber. It is used as a sealing material for water/methanol systems. Synthetic Rubber Synthetic rubber is available in several types, each of which is compounded of different materials to give the desired properties. The most widely used are the butyls, Bunas, and neoprene. Butyl is a hydrocarbon rubber with superior resistance to gas permeation. It is also resistant to deterioration; however, its comparative physical properties are significantly less than those of natural rubber. Butyl resists oxygen, vegetable oils, animal fats, alkalies, ozone, and weathering. Like natural rubber, butyl swells in petroleum or coal tar solvents. It

</details>

### g51 · manuel · test

**Question :** What is the standard mathematical method for calculating the surface area of a four-sided shape that features only one set of parallel edges?

- Réponse attendue : The area of a trapezoid is determined by multiplying one-half of the sum of its two bases by its height.
- Mots-clés exigés : `height`, `1/2|half|½|1⁄2|/ 2|/2`
- Source : Manuel, page 3-18
- Passage source : <details><summary>afficher</summary>

> triangle has all three angles less than 90°. A right triangle has one right angle (a 90° angle). An obtuse triangle has one angle greater than 90°. Each of these types of triangles is shown in Figure 3-16. The formula for the area of a triangle is area = 1⁄2 × (base × height) = 1⁄2 × (b × h) Example: Find the area of the obtuse triangle shown in Figure 3-17. First, substitute the known values in the area formula. a = 1⁄2 × (b × h) = 1⁄2 × (2'6" × 3'2") Next, convert all dimensions to inches: 2'6" = (2 × 12") + 6" = (24 + 6) = 30 inches 3'2" = (3 × 12") + 2" = (36 + 2) = 38 inches Now, solve the formula for the unknown value: a = 1⁄2 × (30 inches × 38 inches) = 570 square inches Parallelogram A parallelogram is a four-sided figure with two pairs of parallel sides. [Figure 3-18] Parallelograms do not necessarily have four right angles. The formula for the area of a parallelogram is: area = length × height = l × h Trapezoid A trapezoid is a four-sided figure with one pair of parallel sides. [Figure 3-19] The formula for the area of a trapezoid is: area = 1⁄2 (base1 + base2) × height

</details>

### g52 · manuel · test

**Question :** Which Phillips screwdriver sizes are appropriate for specific screw dimensions?

- Réponse attendue : A Number 1 Phillips driver is intended for screw sizes 2 through 4, whereas a Number 2 Phillips driver is utilized for screw sizes 5 through 9.
- Mots-clés exigés : `Number 1|No. 1|#1|size 1`, `Number 2|No. 2|#2|size 2`
- Source : Manuel, page 11-1
- Passage source : <details><summary>afficher</summary>

> on some aircraft. The two types of recessed head screws for common use are the Phillips and the Reed & Prince. Both the Phillips and Reed & Prince recessed heads are optional on several types of screws. As shown in Figure 11-2, the Reed & Prince recessed head forms a perfect cross. The screwdriver used with this screw is pointed on the end. Since the Phillips screw has a slightly larger center in the cross, the Phillips screwdriver is blunt on the end. The Phillips screwdriver is not interchangeable with the Reed & Prince. The use of the wrong type of screwdriver results in mutilation of the screwdriver and the screw head. When turning a recessed head screw, use only the proper recessed head screwdriver of the correct size. The most common crosspoint screwdrivers are the Number 1 and Number 2 Phillips. Each of these are designed to be used for specific sized screws. A Number 1 Phillips screwdriver is used on 2, 3, and 4 screws, while a Number 2 Phillips is used for screw sizes 5, 6, 7, 8, and 9. An offset screwdriver may be used when vertical space

</details>

### g59 · manuel · dev

**Question :** What is the standard procedure for managing steel corrosion on aircraft parts?

- Réponse attendue : The most effective method involves physically eliminating all oxidation and reapplying protective finishes.
- Mots-clés exigés : `remov`, `coating`
- Source : Manuel, page 8-15
- Passage source : <details><summary>afficher</summary>

> [Figure 8-26] Its presence in these areas is generally not dangerous and has no immediate effect on the structural strength of any major components. The residue from the rust may also contaminate other ferrous components, promoting corrosion of those parts. The rust is indicative of a need for maintenance and of possible corrosive attack in more critical areas. It is also a factor in the general appearance of the equipment. When paint failures occur or mechanical damage exposes highly-stressed steel surfaces to the atmosphere, even the smallest amount of rusting is potentially dangerous in these areas and must be removed and controlled. Rust removal from structural components, followed by an inspection and damage assessment, must be done as soon as feasible. [Figure 8-27] Mechanical Removal of Iron Rust The most practicable means of controlling the corrosion of steel is the complete removal of corrosion products by mechanical means and restoring corrosion preventive coatings. Except on highly-stressed steel surfaces, the use of abrasive papers and compounds, small power buffers and buffing compounds, hand wire brushing, or steel wool are all acceptable cleanup procedures. However, it should be recognized that in any such use of abrasives, residual rust

</details>

### g62 · manuel · test

**Question :** Why is air considered an ineffective medium for transferring thermal energy through direct contact?

- Réponse attendue : Air is a poor conductor because its molecules are spaced significantly further apart than those found in solid materials, which hinders the efficient transfer of kinetic energy between adjacent particles.
- Mots-clés exigés : `farther apart|far apart|spaced`
- Source : Manuel, page 5-19
- Passage source : <details><summary>afficher</summary>

> interesting to note that silver, copper, and aluminum are also excellent conductors of electricity. Liquids are poorer conductors of heat than metals. Notice that the ice in the test tube shown in Figure 5-28 is not melting rapidly even though the water at the top is boiling. The water conducts heat so poorly that not enough heat reaches the ice to melt it. Gases are even poorer conductors of heat than liquids. It is possible to stand quite close to a stove without being burned because air is such a poor conductor. Since conduction is a process whereby the increase in molecular energy is passed along by actual contact, gases are poor conductors. At the point of application of the heat source, the molecules become violently agitated. These molecules strike adjacent molecules causing them to become agitated. This process continues until the heat energy is distributed evenly throughout the substance. The gases are much poorer conductors of heat because molecules are farther apart in gases than in solids.

</details>

### g64 · manuel · dev

**Question :** How is the total opposition to current flow calculated in an alternating current circuit that includes both resistance and inductive reactance?

- Réponse attendue : The total impedance is determined by taking the square root of the sum of the squares of the resistance and the inductive reactance.
- Mots-clés exigés : `Pythagorean|square root`
- Source : Manuel, page 12-60
- Passage source : <details><summary>afficher</summary>

> 110V AC 60 cycles A XL1 XL2 Figure 12-130. AC circuit containing inductance. Figure 12-131. Inductances in series. + L2 − L1 Figure 12-129. Two inductors in parallel. resistance, R. The impedance of a circuit is the circuit’s total opposition to the flow of current. In an AC circuit, this opposition consists of resistance and reactance, either inductive or capacitive or elements of both. Resistance and reactance cannot be added directly, but they can be considered as two forces acting at right angles to each other. Thus, the relation between resistance, reactance, and impedance may be illustrated by a right triangle. [Figure 12-134] Since these quantities may be related to the sides of a right triangle, the formula for finding the impedance, or total opposition to current flow in an AC circuit, can be found by using the law of right triangles. This theorem, called the Pythagorean theorem, applies to any right triangle. It states that the square of the hypotenuse is equal to the sum of the squares of the other two sides. Thus, the value of any side of a right triangle can be found if the other two sides are known. If an AC circuit contains resistance and inductance, as shown in Figure 12-135, the relation between the sides can be stated as: Z2 = R2 + XL2 The square root of both sides of the equation gives Z = R2 + XL2 This formula can be used to determine the impedance when the values of inductive

</details>

### h05 · plusieurs consignes · test

**Question :** Which ATR 72 directives in the documents concern the landing gear?

- Réponse attendue : AD 2023-17-01 (nose landing gear drag brace panels) and AD 2025-04-04 (main landing gear rear hinge pin).
- Mots-clés exigés : `2023-17-01`, `2025-04-04`
- Source : [AD 2023-17-01](https://www.federalregister.gov/documents/2023/09/14/2023-19900/airworthiness-directives-atr-gie-avions-de-transport-rgional-airplanes), [AD 2025-04-04](https://www.federalregister.gov/documents/2025/02/28/2025-03292/airworthiness-directives-atr-gie-avions-de-transport-rgional-airplanes)

### h08 · en français · dev

**Question :** Quel problème a été constaté sur l'axe de charnière arrière du train principal de l'ATR 72 ?

- Réponse attendue : Des axes de charnière arrière du train principal ont été trouvés rompus (AD 2025-04-04).
- Mots-clés exigés : `rompu|rupture|cassé|ruptured|rupt`
- Source : [AD 2025-04-04](https://www.federalregister.gov/documents/2025/02/28/2025-03292/airworthiness-directives-atr-gie-avions-de-transport-rgional-airplanes)

### u07 · sans réponse · dev

**Question :** What is the tire pressure of the Airbus A350-1000 main landing gear wheels?

- Réponse attendue : Not in the documents.
- Mots-clés exigés : —
- Source : — (l'assistant doit dire « je ne sais pas »)

### u09 · sans réponse · dev

**Question :** How many Airbus A321neo airplanes are registered in the United States?

- Réponse attendue : Not in the documents.
- Mots-clés exigés : —
- Source : — (l'assistant doit dire « je ne sais pas »)
