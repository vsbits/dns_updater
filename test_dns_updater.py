import dns_updater


class TestCheckIP:
    def test_single_digits(self):
        assert dns_updater._is_ip("0.0.0.0")

    def test_three_digits(self):
        assert dns_updater._is_ip("123.111.111.123")

    def test_two_digits(self):
        assert dns_updater._is_ip("12.11.23.11")

    def test_different_digits(self):
        assert dns_updater._is_ip("1.11.111.1")

    def test_extra_line(self):
        assert dns_updater._is_ip("1.1.1.1\n") is False

    def test_too_many_digits(self):
        assert dns_updater._is_ip("1234.1.1.1") is False

    def test_not_ip(self):
        assert dns_updater._is_ip("abc") is False

    def test_extra_caracters(self):
        assert dns_updater._is_ip(" 1.1.1.1") is False
