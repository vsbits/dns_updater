from typing import Optional
from .errors import CacheCreationError, CacheLoadError


class Cache:
    """Class to represent cache storage"""
    def __init__(self, filepath: str, value: str | None = None):
        self.filepath = filepath
        self.value = value

    def save(self):
        """Saves the current value to file"""
        if self.filepath and self.value:
            with open(self.filepath, "w") as file:
                file.write(self.value)
        else:
            raise CacheCreationError("Filepath is not defined")

    def update(self, value: str, save: bool = False):
        """Updates the corrent value of the cache object

        value: value to be stored
        save: if True, value is also saved to file
        """
        self.value = value
        if save:
            self.save()

    def compare(self, value: str, update: bool = False) -> bool:
        """Compares a new value to the value stored

        value: value to compare
        """
        same = self.value == value
        if update and not same:
            self.update(value)

        return same


def load_cache(filepath: str) -> Cache:
    """Loads cache from file and returns it as a `Cache` object

    filepath: Path to where the file is located"""
    try:
        with open(filepath) as file:
            value = file.read().strip()
    except FileNotFoundError as e:
        raise CacheLoadError(e)
    return Cache(filepath, value)


def create_cache(filepath: str, value: Optional[str] = None) -> Cache:
    """Creates a new file to use as cache

    filepath: Path to where the file should be created
    value: Value to be store on file upon creation. If not specified,
    creates empty file
    """
    try:
        with open(filepath, "x") as file:
            if value:
                file.write(value)
    except FileExistsError as e:
        raise CacheCreationError(e)
    return Cache(filepath, value)
