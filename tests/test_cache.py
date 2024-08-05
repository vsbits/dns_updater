import pytest
import os
from dns_updater.cache import (
    Cache, load_cache, create_cache, CacheCreationError, CacheLoadError
)


class TestCache:
    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Fixture to provide a temp text file to be used as cache"""
        self.filepath = '.test_cache_file.temp'

        if os.path.exists(self.filepath):
            os.remove(self.filepath)

        yield

        if os.path.exists(self.filepath):
            os.remove(self.filepath)

    def test_create_cache(self):
        """Test cache creation with a value"""
        cache = create_cache(self.filepath, '0.0.0.0')
        assert cache.filepath == self.filepath
        assert cache.value == '0.0.0.0'
        with open(self.filepath) as f:
            assert f.read().strip() == '0.0.0.0'

    def test_create_cache_empty(self):
        """Test cache creation with no initial value"""
        cache = create_cache(self.filepath)
        assert cache.filepath == self.filepath
        assert cache.value is None
        with open(self.filepath) as f:
            assert f.read() == ''

    def test_load_cache(self):
        """Test loading cache from file"""
        _ = create_cache(self.filepath, '0.0.0.0')
        cache = load_cache(self.filepath)
        assert cache.filepath == self.filepath
        assert cache.value == '0.0.0.0'

    def test_load_cache_file_not_found(self):
        """Test loading cache from a non-existent file"""
        with pytest.raises(CacheLoadError):
            load_cache('non_existent_file.txt')

    def test_save_cache(self):
        """Test saving cache to a file"""
        cache = create_cache(self.filepath, '0.0.0.0')
        cache.update('1.1.1.1', save=True)
        assert cache.value == "1.1.1.1"
        with open(self.filepath) as f:
            assert f.read().strip() == '1.1.1.1'

    def test_update_cache(self):
        """Test updating cache value without saving"""
        cache = create_cache(self.filepath, '0.0.0.0')
        cache.update('1.1.1.1')
        assert cache.value == '1.1.1.1'
        with open(self.filepath) as f:
            assert f.read().strip() == '0.0.0.0'

    def test_compare_cache(self):
        """Test comparing cache value"""
        cache = create_cache(self.filepath, '0.0.0.0')
        assert cache.compare('0.0.0.0') is True
        assert cache.compare('1.1.1.1') is False
        cache.compare('1.1.1.1', update=True)
        assert cache.value == '1.1.1.1'

    def test_save_cache_no_filepath(self):
        """Test saving cache with no value"""
        cache = Cache(self.filepath, None)
        with pytest.raises(CacheCreationError):
            cache.save()

    def test_create_cache_file_exists(self):
        """Test creating cache when file already exists"""
        create_cache(self.filepath, '0.0.0.0')
        with pytest.raises(CacheCreationError):
            create_cache(self.filepath, '0.0.0.0')
