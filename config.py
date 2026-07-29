from pathlib import Path
from pydantic import BaseModel
import json
from exceptions import ConfigError, InvalidConfig, NoConfigExisting
from getpass import getpass

CONFIG_PATH = Path("./config.json")


class User(BaseModel):
    username: str
    password: str

    def __repr__(self):
        return f'Uporabnik({self.username}, ****))'


class Config(BaseModel):
    users: list[User]


_config: Config | None = None


def get_config() -> Config:
    global _config
    if _config is None:
        if CONFIG_PATH.exists():
            try:
                with open(CONFIG_PATH) as f:
                    _config = Config.model_validate_json(f.read())
            except Exception as e:
                raise InvalidConfig(str(e))
        else:
            raise NoConfigExisting()

    return _config


if __name__ == "__main__":
    try:
        print("Trenutni config:", get_config())
    except NoConfigExisting:
        _config = Config(users=[])

    while True:
        try:
            action = input("""[ctrl + ^C] za izhod.
[1] za dodajanje uporabnika
[2] za odstranitev uporabnika
> """)
            if action == "1":
                username = input("username: ")
                password = getpass("geslo: ")
                _config.users.append(
                    User(username=username, password=password)
                )
            elif action == "2":
                username = input("username: ")
                done = False
                for i, user in enumerate(_config.users):
                    if user.username == username:
                        _config.users.pop(i)
                        done = True
                        break
                print("Opravljeno." if done else "uporabnik ne obstaja")
            else:
                print("nedefiniran ukaz")
            print("---\nTrenutni config:", get_config())
        except KeyboardInterrupt:
            print("quitting...")
            break

    with open(CONFIG_PATH, "w") as f:
        f.write(_config.model_dump_json(indent=2))
