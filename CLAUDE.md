# CLAUDE.md

Instructies voor Claude Code in dit project.

## Project
Scrabble in Python 3.12+ voor Windows 11 (64-bit). Taal van de code: Engels (namen, docstrings).
Taal van communicatie met de gebruiker: Nederlands.
Het spel wordt eerst voor het **Nederlands** gebouwd; andere talen (bijv. Engels) komen mogelijk later.

## Opdrachten (PowerShell)
- Setup: `.\scripts\setup.ps1`
- Activeren: `.\.venv\Scripts\Activate.ps1`
- Tests: `pytest`
- Lint: `ruff check .` en `ruff format .`
- Types: `mypy`
- Alles in één keer voor een commit: `ruff check . ; ruff format --check . ; mypy ; pytest`

## Architectuur
- `src/scrabble/` bevat de spellogica en mag **nooit** een GUI-bibliotheek importeren
  (geen tkinter, pygame, PySide6).
- De interface komt in een apart pakket (`src/scrabble/ui/`) en roept alleen de logica aan.
- Woordenlijst: `WordList` met een `set` voor validatie. Een trie/DAWG/GADDAG komt pas bij de computerspeler.
- Letterwaarden en -aantallen staan per taal in `src/scrabble/languages/<code>.json` (nu `nl.json`),
  geladen met `load_language("nl")`. Hardcodeer nooit letters, aantallen of punten in de code.
- Een nieuwe taal toevoegen = een JSON-bestand toevoegen plus een woordenlijst; geen codewijziging.
- Een blanco is `Tile.blank()`; pas bij het leggen krijgt hij een letter via `Tile.as_letter(...)`
  en blijft hij 0 punten waard.

## Regels
- Schrijf eerst of tegelijk met de code een pytest-test, vooral voor score en kruiswoorden.
- Type hints overal; `mypy --strict` moet slagen.
- Kleine, gerichte commits met duidelijke berichten. Werk op een feature-branch, niet direct op `main`.
- Voeg geen afhankelijkheden toe zonder het te melden en `pyproject.toml` bij te werken.
- Commit geen woordenlijsten zonder dat de licentie dat toestaat (`data/*.txt` is genegeerd).
- Gebruik `pathlib` en vermijd hardgecodeerde Windows-paden.

## Scrabble-regels (kernpunten)
- Eerste zet moet over de middenster (7,7) lopen.
- Alle gevormde woorden (hoofdwoord én kruiswoorden) moeten in de woordenlijst staan.
- Bonusvakken tellen alleen voor nieuw gelegde tegels.
- Alle 7 rekletters in één beurt = 50 punten bonus.
- Een blanco heeft waarde 0, ook als hij een letter voorstelt.

## Status
- Fase 0 (omgeving): klaar
- Fase 1 (datamodel: bord, zakje, rek, spelers, spelstart): klaar
- Volgende: fase 2 (zetvalidatie en score)
- Interfacekeuze is nog open.
