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
    print("Shranjeni uporabniki:")
    users_dict = {}
    for i, user in enumerate(users):
        i = str(i)
        print(i + ": " + user.username)
        users_dict[i] = user

    while True:
        e = input('Napiši številko željenega uporabnika ali pa pusti prazno. da izbereš drugega uporabnika brez shranjevanja > ')
        if e == "":
            print("Nadaljevanje brez shranjenih podatkov.")
            break
        if user := users_dict.get(e):
            break
        print("Ta uporabnik ni med shranjenimi.")
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
print("Shranjevanje v:", filename)
filename.write_text(calendar.serialize())
