# Relecture du jeu de questions

Fichier source : `eval/questions.jsonl` (20 questions). **À relire avant de lancer `make eval`.**

Pour chaque question, vérifie en 20 secondes :
1. **La question est-elle claire** et réaliste (quelque chose qu'un technicien pourrait demander) ?
2. **La réponse attendue est-elle juste ?** Tu peux cliquer sur la source pour vérifier.
3. **Les mots-clés exigés sont-ils raisonnables ?** Une réponse est comptée juste seulement si elle contient chacun d'eux (`a|b` veut dire « a ou b »). Trop strict = de bonnes réponses comptées fausses ; trop large = de mauvaises réponses comptées justes.

Tu peux me répondre simplement : « OK », ou « q07 : enlever corrosion », « supprimer q19 », etc.

Répartition : 4 consignes par numéro, 4 consignes par sujet, 3 questions d'avions concernés, 5 questions sur le manuel, 4 questions sans réponse (20 %).

## Consigne citée par son numéro

**q01.** What does AD 2025-24-51 address, and what event prompted it?

- Réponse attendue : A malfunction of the elevator aileron computer (ELAC), prompted by an uncommanded and limited pitch-down event on an A320 with the autopilot engaged.
- Mots-clés exigés : `elevator aileron computer|ELAC`, `pitch down|pitch-down`
- Source : [AD 2025-24-51](https://www.federalregister.gov/documents/2026/01/05/2025-24242/airworthiness-directives-airbus-sas-airplanes)

**q02.** Which EASA AD must be followed to comply with AD 2024-08-02?

- Réponse attendue : EASA AD 2023-0181 (dated October 13, 2023).
- Mots-clés exigés : `2023-0181`
- Source : [AD 2024-08-02](https://www.federalregister.gov/documents/2024/05/02/2024-09355/airworthiness-directives-atr-gie-avions-de-transport-rgional-airplanes)

**q03.** Which earlier AD does AD 2023-12-11 replace?

- Réponse attendue : AD 2022-03-20.
- Mots-clés exigés : `2022-03-20`
- Source : [AD 2023-12-11](https://www.federalregister.gov/documents/2023/06/21/2023-13152/airworthiness-directives-the-boeing-company-airplanes)

**q04.** What is the effective date of AD 2022-27-01?

- Réponse attendue : February 2, 2023.
- Mots-clés exigés : `February 2, 2023|2 February 2023|2023-02-02`
- Source : [AD 2022-27-01](https://www.federalregister.gov/documents/2022/12/29/2022-28271/airworthiness-directives-airbus-sas-airplanes)

## Consigne décrite par son sujet

**q05.** Which AD addresses water entering the lower lobe electronic equipment bay of the Boeing 737-800, and what equipment could the water damage?

- Réponse attendue : AD 2022-08-05; water could damage the air data inertial reference units and flight management computers (EE bay units in the E5 rack).
- Mots-clés exigés : `2022-08-05`, `inertial reference|flight management computer|E5 rack`
- Source : [AD 2022-08-05](https://www.federalregister.gov/documents/2022/04/22/2022-08543/airworthiness-directives-the-boeing-company-airplanes)

**q06.** Why must some fasteners in the A350 center wing box be replaced, and what is the worst-case risk?

- Réponse attendue : Some fasteners rotated inside their holes during flight and fatigue testing; this could lead to loss of clamping, cracking of the nut sealant cover and, with a lightning strike, a fuel tank explosion.
- Mots-clés exigés : `rotat`, `fuel tank explosion`
- Source : [AD 2022-27-01](https://www.federalregister.gov/documents/2022/12/29/2022-28271/airworthiness-directives-airbus-sas-airplanes)

**q07.** What manufacturing defect was found on A320 family main landing gear aft pintle pins, and what could it lead to?

- Réponse attendue : A batch was made without nickel plating on the inner bore; this could cause corrosion and cracks, possibly leading to a main landing gear collapse.
- Mots-clés exigés : `nickel`, `corrosion`
- Source : [AD 2025-17-17](https://www.federalregister.gov/documents/2025/09/02/2025-16728/airworthiness-directives-airbus-sas-airplanes)

**q08.** According to the FAA, what happens when certain Ni-Cd batteries are repeatedly disconnected and reconnected during airplane parking or storage?

- Réponse attendue : Their capacity can be reduced, which could reduce battery endurance and the supply of minimum essential electrical power (AD 2024-08-08).
- Mots-clés exigés : `capacity`
- Source : [AD 2024-08-08](https://www.federalregister.gov/documents/2024/05/02/2024-09354/airworthiness-directives-airbus-sas-airplanes)

## Avions concernés

**q09.** Which Boeing 737 models are covered by AD 2023-12-11 on radio altimeter interference?

- Réponse attendue : All Boeing 737-8, 737-9 and 737-8200 airplanes.
- Mots-clés exigés : `737-8`, `737-9`, `8200`
- Source : [AD 2023-12-11](https://www.federalregister.gov/documents/2023/06/21/2023-13152/airworthiness-directives-the-boeing-company-airplanes)

**q10.** Which airplane models are affected by AD 2024-20-01 on the aft galley attachment studs?

- Réponse attendue : Airbus Model A350-941 and A350-1041 airplanes.
- Mots-clés exigés : `941`, `1041`
- Source : [AD 2024-20-01](https://www.federalregister.gov/documents/2024/10/24/2024-24465/airworthiness-directives-airbus-sas-airplanes)

**q11.** Which ATR models are affected by AD 2024-08-02?

- Réponse attendue : ATR42-200, -300, -320 and -500, and ATR72-101, -102, -201, -202, -211, -212 and -212A.
- Mots-clés exigés : `ATR42|ATR 42|ATR-42`, `ATR72|ATR 72|ATR-72`
- Source : [AD 2024-08-02](https://www.federalregister.gov/documents/2024/05/02/2024-09355/airworthiness-directives-atr-gie-avions-de-transport-rgional-airplanes)

## Manuel

**q12.** What is the Maintenance Error Decision Aid (MEDA) used for?

- Réponse attendue : A Boeing-developed tool to investigate maintenance errors, understand their root causes and prevent accidents, rather than blame maintenance personnel.
- Mots-clés exigés : `root cause|investigat`
- Source : Manuel FAA-H-8083-30B, page 14-10

**q13.** What are the three basic parts of a lever?

- Réponse attendue : The fulcrum, the effort (force) and the resistance.
- Mots-clés exigés : `fulcrum`, `effort|force`, `resistance`
- Source : Manuel FAA-H-8083-30B, page 5-8 ou 5-7

**q14.** What does Boyle's law state?

- Réponse attendue : The volume of an enclosed dry gas varies inversely with its absolute pressure, provided the temperature remains constant (V1P1 = V2P2).
- Mots-clés exigés : `volume`, `pressure`, `inverse|temperature`
- Source : Manuel FAA-H-8083-30B, page 5-24 ou 5-25

**q15.** Into which three groups can potential energy be classified?

- Réponse attendue : Energy due to position, energy due to distortion of an elastic body, and energy which produces work through chemical action.
- Mots-clés exigés : `position`, `distortion|elastic`, `chemical|work`
- Source : Manuel FAA-H-8083-30B, page 5-2 ou 5-3

**q16.** What happens to the velocity, pressure and density of supersonic air flowing through a converging passage?

- Réponse attendue : Its velocity decreases while its pressure and density both increase.
- Mots-clés exigés : `decrease|slow`, `increase`
- Source : Manuel FAA-H-8083-30B, page 5-46 ou 5-47

## Sans réponse dans les documents

**q17.** What is the maximum takeoff weight of the ATR 72-600?

- Réponse attendue : Not in the documents: the assistant should abstain.
- Mots-clés exigés : — (l'assistant doit dire « je ne sais pas »)
- Source : —

**q18.** Which airworthiness directives were issued for the Embraer E190 in 2024?

- Réponse attendue : Not in the documents (the corpus has no Embraer directives): the assistant should abstain.
- Mots-clés exigés : — (l'assistant doit dire « je ne sais pas »)
- Source : —

**q19.** What torque value must be applied to the bolts when replacing the A320 main landing gear aft pintle pins?

- Réponse attendue : Not in the documents (AD 2025-17-17 refers to EASA AD 2025-0167 for the detailed actions): the assistant should abstain or say the detail is not available.
- Mots-clés exigés : — (l'assistant doit dire « je ne sais pas »)
- Source : —

**q20.** Who is the current FAA Administrator?

- Réponse attendue : Not in the documents: the assistant should abstain.
- Mots-clés exigés : — (l'assistant doit dire « je ne sais pas »)
- Source : —
