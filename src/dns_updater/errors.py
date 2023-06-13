class CacheCreationError(FileExistsError):
    pass


class CacheLoadError(FileNotFoundError):
    pass


class ConnectionError(Exception):
    pass
