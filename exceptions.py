class LoginError(Exception):
    pass


class InvalidCredentials(LoginError):
    pass


class CaptchaRequired(LoginError):
    pass


class AuthenticationFlowError(LoginError):
    pass


class ConfigError(Exception):
    message = "There is something wrong with the config."

    def __init__(self, *args):
        super().__init__(self.message, *args)


class NoConfigExisting(ConfigError):
    message = "Config doesn't exist. Run config.py or make it manually."


class InvalidConfig(ConfigError):
    message = "Something was wrong with the config."
