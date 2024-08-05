from dns_updater.core import is_valid_ip, get_ip, update_dns
import json
import pytest


class TestCheckIP:
    @pytest.mark.parametrize(
        "ip",
        ["0.0.0.0", "123.111.111.123", "12.11.23.11", "1.11.111.1"]
    )
    def test_single_digits(self, ip):
        """Test valid IPs"""
        assert is_valid_ip(ip) is True

    @pytest.mark.parametrize(
        "ip",
        ["01.0.0.0", "1.1.1.1\n", "1234.1.1.1", "abc", " 1.1.1.1"]
    )
    def test_zeros_left(self, ip):
        """Test invalid IPs"""
        assert is_valid_ip(ip) is False


class TestGetIp:
    @pytest.fixture
    def mocker(self, mocker):
        """Fixture to provide mocker for each test"""
        return mocker

    def test_get_ip_success(self, mocker):
        """Test get_ip function with a successful response"""
        mock_get = mocker.patch('requests.get')
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = '192.168.1.1'

        result = get_ip('http://example.com/api/ip')
        assert result == '192.168.1.1'

    def test_get_ip_invalid_status_code(self, mocker):
        """Test get_ip function with a non-200 status code"""
        mock_get = mocker.patch('requests.get')
        mock_get.return_value.status_code = 500

        with pytest.raises(ConnectionError):
            get_ip('http://example.com/api/ip')

    def test_get_ip_invalid_ip(self, mocker):
        """Test get_ip function with an invalid IP"""
        mock_get = mocker.patch('requests.get')
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = 'Your IP is 0.0.0.0'

        with pytest.raises(ValueError):
            get_ip('http://example.com/api/ip')

    def test_get_ip_no_ip(self, mocker):
        """Test get_ip function with an empty response"""
        mock_get = mocker.patch('requests.get')
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = ''

        with pytest.raises(ValueError):
            get_ip('http://example.com/api/ip')


class TestUpdateDns:
    @pytest.fixture
    def mocker(self, mocker):
        """Fixture to provide mocker for each test"""
        return mocker

    def test_update_dns_success(self, mocker):
        """Test update_dns function with a successful response"""
        # Mock successful response
        mock_put = mocker.patch('requests.put')
        mock_put.return_value.status_code = 200
        mock_put.return_value.text = json.dumps({'success': True})

        # Call the function with test data
        update_dns(
            tk="TEST_TKN",
            new_ip="192.168.1.1",
            name="example.com",
            proxied=True,
            rec_type="A",
            zone="zone_id",
            id="record_id"
        )

        # Assert that requests.put was called with the correct parameters
        mock_put.assert_called_once_with(
            "https://api.cloudflare.com/client/v4/zones/zone_id/"
            "dns_records/record_id",
            json={
                'content': '192.168.1.1',
                "name": "example.com",
                "proxied": True,
                "type": "A"
            },
            headers={
                "Content-Type": "application/json",
                "Authorization": "Bearer TEST_TKN"
            }
        )

    def test_update_dns_connection_error(self, mocker):
        """Test update_dns function with a connection error"""
        # Mock response with status code other than 200
        mock_put = mocker.patch('requests.put')
        mock_put.return_value.status_code = 500
        mock_put.return_value.text = ""

        with pytest.raises(ConnectionError):
            update_dns(
                tk="test_token",
                new_ip="192.168.1.1",
                name="example.com",
                proxied=True,
                rec_type="A",
                zone="zone_id",
                id="record_id"
            )

    def test_update_dns_failure(self, mocker):
        """Test update_dns function with an unsuccessful response"""
        # Mock response with success = false
        mock_put = mocker.patch('requests.put')
        mock_put.return_value.status_code = 200
        mock_put.return_value.text = json.dumps(
            {
                "success": False,
                "errors": [{"code": 1234, "message": "Invalid record ID"}]
            }
        )

        with pytest.raises(
            ValueError,
            match='[{"code": 1234, "message": "Invalid record ID"}]'
        ):
            update_dns(
                tk="test_token",
                new_ip="192.168.1.1",
                name="example.com",
                proxied=True,
                rec_type="A",
                zone="zone_id",
                id="record_id"
            )
