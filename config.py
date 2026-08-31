import secrets
from models import Config, User
from exceptions import NoConfigExisting
from getpass import getpass

if __name__ == "__main__":
    try:
        config = Config.load()
    except NoConfigExisting:
        config = Config(user_configs=[])

    while True:
        try:
            action = input("""[ctrl + ^C] za izhod.
[1] za dodajanje uporabnika
[2] za odstranitev uporabnika
[3] za regeneriranje URL za uporabnika
> """)
            if action == "1":
                username = input("username: ")
                password = getpass("geslo: ")
                user = User(username=username, password=password, calendar_token=secrets.token_urlsafe(config.token_lenght))
                config.users.append(user)
                print(f"URL za tega uporabnika je: /calendar/{user.calendar_token}")  # todo: add url prefix or sum shit into config?
            elif action == "2":
                username = input("username: ")
                done = False
                for i, user in enumerate(config.users):
                    if user.username == username:
                        config.users.pop(i)
                        done = True
                        break
                print("Opravljeno." if done else "uporabnik ne obstaja")
            elif action == "3":
                username = input("username: ")
                done = False
                for i, user in enumerate(config.users):
                    if user.username == username:
                        user.calendar_token = secrets.token_urlsafe(config.token_length)
                        done = True
                        break
                print(f"Opravljeno. Novi URL je zdaj /calendar/{user.calendar_token}" if done else "uporabnik ne obstaja")
            else:
                print("nedefiniran ukaz")
            print("---\nTrenutni config:", config)
            config.save()
        except KeyboardInterrupt:
            print("\nizhod ...", end="\r")
            break
    config.save()
