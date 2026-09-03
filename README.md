eAsistent to ICS
---
This project implements a reverse engineered internal API of a common school management system in Slovenia, eAsistent, to convert its timetable to [iCalendar format.](https://en.wikipedia.org/wiki/ICalendar)
A simple .ics service server using FastAPI is also implemented. I assume anyone actually interested in this project would know Slovenian, so instructions are written in Slovenian, as well as some user interface scripts.

Ta projekt uporablja razvozlan interni API sistema eAsistent, da spremeni šolski urnik v [iCalendar obliko](https://en.wikipedia.org/wiki/ICalendar). Prav tako pa vsebuje še enostavni strežnik .ics storitve, narejen z FastAPI.

Funkcije:
- 
- samodejna avtentifikacija
- validacija z knjižnico Pydantic
- možnost shranjevanja urnika v datoteko z .ics formatom
- že prej omenjen strežnik .ics storitve
- možnost uporabe več uporabniških računov hkrati
- enostavna konfiguracija z scriptom (work in progress :))

Namestitev
-
1. Prepričajte se, da imate naložen Python (projekt je bil narejen za Python 3.14.7)
2. naložite projekt (npr. `git clone https://github.com/TKobe28/eAsistentToICS.git`)
3. (opcijsko) naredite virtual environment, na primer: `python -m venv venv` ali `python3 -m venv venv`
4. če ste naredili prejšnji korak, to naredite pred vsako uporabo tega projekta: `"venv\Scripts\activate.bat"` ali `venv\Scripts\Activate.ps1` na Windows sistemih, `source venv/bin/activate` na Unix sistemih
5. `pip install -r requirements.txt`
6. naredite si konfiguracijo, tako da zaženete config.py: `python config.py`

Konfiguracija
-
Projekt ima dve konfiguracijski datoteki:
- config.json
- server_config.json


Prvo se mora generirati za config.py in vsebuje uporabniške račune in nastavitve za delovanje ics storitve.
Druga se generira med zagonom server.py, če ne obstaja, oziroma se samo kopira default_config.json. Vsebuje argumente za implementiran ASGI Uvicorn, kot je recimo port, ip ipd.

Uporaba
-
- za shranjevanje v datoteko: `python export.py`
- za zagon strežnika za ics storitev: `python server.py`
- zagon strežnika je mogoč tudi direktno prek ASGI strežnikov, na primer: `gunicorn server:app` na unix sistemih

Uporaba ics storitve:
-
Privzeta vrata (port) strežnika so 55555. Glej "Konfiguracija".

Pri ustvarjanju uporabnika z config.py se avtomatsko generira tudi ti. "token" oziroma žeton uporabnika. V istem scriptu se da tudi regenerirati.
Za vsakega uporabnika se tako naredi mesto, kjer se lahko dostopa do njegovega koledarja. To je formula URLja:
```
http://{ip}:55555/calendar/{žeton}
```
Če imamo ip `95.14.15.35` in žeton `n5imB1SO7shhAanwQnfSyV5B2eE4Exq7-uL0xY3dfuA`, vrata pa pustimo na `55555`, potem je naš url tak:
```
http://95.14.15.35:55555/calendar/n5imB1SO7shhAanwQnfSyV5B2eE4Exq7-uL0xY3dfuA
```

Opozorila
-
- Z NIKOMUR NE DELITE DATOTEKE `config.json`. Vsebuje gesla.
- Če boste strežnik izpostavljali, priporočam da si omislite kakšen reverse proxy (ker brez tega in brez ssl certifikata ne morete uporabljati HTTPS)
- Ta projekt ni uradno povezan z eAsistentom ali eŠola d.o.o. - uporaba na lastno odgovornost!