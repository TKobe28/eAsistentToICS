"""
Simple exporting script.
"""
import asyncio
import models
from pathlib import Path

config = models.Config.load()
users = config.users
user = None
if len(users) != 0:
    print("Shranjeni uporabniki:", ", ".join([user.username for user in users]))
    while True:
        e = input('Izberi uporabnika ali napiši "NE" da izbereš drugega uporabnika brez shranjevanja > ')
        if e == "NE":
            break
        for usr in users:
            if usr.username == e:
                user = usr
                break
            print("Ta uporabnik ni med shranjenimi.")
        if user is not None:
            break
else:
    print(
        "Ni nobenega shranjenega uporabnika. Zaženi config.py za dodajanje uporabnikov. Zdaj pa lahko vneseš podatke za drugega uporabnika brez shranjevanja.")
if user is None:
    username = input("username > ")
    password = input("password > ")
    user = models.User(username=username, password=password, config=config, calendar_token="")

hard = input("A naj se ves urnik ponovno naloži? [ja/ne] ")
hard = hard.lower() == "ja"
print("prosim počakajte ...", end="")
calendar = asyncio.run(user.update_calendar(hard=hard))
print("\rurnik je naložen    ")
config.save()

while True:
    filename = input('Kam naj se shrani? (pusti prazno za "calendar.ics") > ')
    if filename == "":
        filename = Path("calendar.ics")
    else:
        filename = Path(filename)
    if filename.exists():
        e = input("Ta datoteka že obstaja. Jo zamenjamo? Sicer izberi drugo ime. [ja/ne] ")
        if e.lower() == "ja":
            break
    else:
        filename.parent.mkdir(exist_ok=True, parents=True)
        break
print("Saving to", filename)
filename.write_text(calendar.serialize())
