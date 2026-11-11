# Paradigm Maker
*Oskar Hamre*
---
Denne filen inneholder en forklaring på padaragigmMaker-mappen, for en med grunnleggende Python-kunnskap.

## `main.py`
- Det er kun denne filen man skal kjøre for å lage et story-listening paradigme
- Øverst i filen blir språk, navn og historiens tema spesifisert. Dersom tema er en tom streng, blir historien tilpasset kulturen til språket.
- **VIKTIG**
    - Alle API-kall bruker tokens (koster penker)
    - Dersom en lydfil allerede er generert, kan linjen som kaller på `generate_story_and_sound` kommenters ut for testing av andre deler av pipelinen.

## `storycreation_and_text_to_speech.py`
- Denne filen innehoder funksjoner som:
    - 1: generer en historie i spesifisert språk med et spesifisert tema.
    - 2: spiller inn og lagrer en lydfil av denne historien.
    - lydfilen lagres i en mappe `Audiofiles generated`.
    - Her kan man endre på funskjonen `_generate_prompt`for å tilpasse prompten som sendes til claude for å generere historien.
- **VIKTIG om API-key**
    - Her brukes eksterne AI-tjenester i koden.
    - Anthropic (claude) brukes til generering av historien.
    - Elevenlabs brukes til å spille inn lydfil.
    - For at denne koden skal kjøre må en `.env` fil i hovedmappen som må inneholde:
        ANTHROPIC_API_KEY=INSERT_YOUR_API_KEY
        ELEVENLABS_API_KEY=INSERT_YOUR_API_KEY
    - Dette gjør at koden kaller på AI-tjenestene fra din bruker.
    - **ALDRI** del disse API-nøklene med noen andre (ikke lim inn i chat, legg ut på github eller lignende)!!!

## `splitAudio.py`
- Dette programmet leser inn den genererte lydfilen, resampler den slik at den varer i nøyaktig 2 minutter, deler den opp i 6 deler, reverserer alle delene og lagrer alle de nye filene i selve paradigme-mappen under `audio`.
- Problem: Claude lager ikke historier som tar nøyaktig 2 minutter å lese inn. Denne resamplingen endrer også tonehøyde, noe som kan bli problematisk for altfor lange eller korte historier.

## `generateJson.py`
- Genrerer en komplett JSON-fil kompatibel med nordicAktiva.
- Tar utgangspunkt i `protocol.json` og endrer slides, UUID for å spille av riktige lydfiler. Se `JSON_STRUCTURE.md` for en grundigere forklaring av JSON-strukturen.
- Den komplette json-filen blir lagt til i paradigme-mappen
