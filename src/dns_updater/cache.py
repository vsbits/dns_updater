from .errors import CacheCreationError, CacheLoadError


class Cache:
    """Class represent cache storage"""
    def __init__(self):
        self.filepath = None
        self.value = None

    def new(self, filepath: str, value: str | None = None):
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
        self.filepath = filepath
        self.value = value

    def load(self, filepath: str):
        """Loads the value from an existing cache file

        filepath: path to file
        """
        try:
            with open(filepath) as file:
                self.value = file.read().strip()
        except FileNotFoundError as e:
            raise CacheLoadError(e)

    def save(self):
        """Saves the current value to file"""
        if self.filepath and self.value:
            with open(self.filepath) as file:
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
