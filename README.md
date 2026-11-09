# Scrabble

Scrabble in Python voor Windows 11 (64-bit).

## Snel starten

```powershell
git clone https://github.com/<jouw-gebruikersnaam>/scrabble.git
cd scrabble
.\scripts\setup.ps1
.\.venv\Scripts\Activate.ps1
pytest
```

## Spelen (tekstversie)

Zet eerst een woordenlijst in `data/woorden.txt` (zie `data/README.md` voor het maken uit OpenTaal).
Start daarna in de geactiveerde omgeving:

```powershell
python -m scrabble
python -m scrabble --spelers Anna Bram
python -m scrabble --woordenlijst pad\naar\lijst.txt
```

Commando's tijdens het spel: `leg H8 h HUIS`, `pas`, `ruil AEI`, `rek`, `bord`, `score`, `hulp`, `stop`.
Een blanco schrijf je tussen haakjes: `leg H8 h H(U)IS`. Kleine letters op het bord zijn blanco's.

## Tests

```powershell
pytest
```

`tests/helpers.py` bevat gedeelde hulpfuncties. `tests/test_simulation.py` speelt willekeurige
hele spellen met een eenvoudige testspeler en controleert na elke actie dat er nog 102 stenen
zijn en dat de scores kloppen.

## Structuur

- `src/scrabble/`: spellogica (geen GUI-imports); `cli.py` is de tekstversie
- `tests/`: pytest-tests
- `data/`: woordenlijsten (zie `data/README.md`)
- `CLAUDE.md`: afspraken voor Claude Code

## Roadmap

- [x] Fase 0: ontwikkelomgeving (Git, GitHub, CI, CLAUDE.md)
- [x] Fase 1: datamodel (bord, zakje, rek, spelers, spelstart) voor het Nederlands
- [x] Fase 2: zetvalidatie en score (zetten, passen, ruilen, einde spel)
- [x] Fase 2b: tekstversie in de terminal (`python -m scrabble`)
- [x] Fase 3: uitgebreide tests (randgevallen, spelsimulatie, controle van het bord)
- [ ] Fase 4: interface (keuze: Tkinter, Pygame of PySide6)
- [ ] Fase 5: computerspeler (trie/DAWG/GADDAG)
- [ ] Fase 6: afwerking en `.exe` (PyInstaller)

## Talen

Taalgegevens (letterverdeling en punten) staan in `src/scrabble/languages/`.
Nu beschikbaar: Nederlands (`nl`). Een nieuwe taal toevoegen betekent een nieuw JSON-bestand
toevoegen, bijvoorbeeld `en.json`.
