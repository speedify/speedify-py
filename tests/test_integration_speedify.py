"""
Integration tests for speedify module.

These tests require:
- Speedify daemon to be running
- User to be logged in
- Active network connections

Run with: pytest tests/test_integration_speedify.py
Run only fast tests: pytest tests/test_integration_speedify.py -m "not slow"
"""
import logging
import random
import os

import pytest

import speedify
from speedify import State, Priority, SpeedifyError, SpeedifyAPIError


logger = logging.getLogger(__name__)


# ============================================================================
# Connection Tests
# ============================================================================

@pytest.mark.integration
def test_connect_closest(speedify_clean_state):
    """Test connecting to the closest server."""
    serverinfo = speedify.connect_closest()
    state = speedify.show_state()

    assert state == State.CONNECTED
    assert "tag" in serverinfo
    assert "country" in serverinfo


@pytest.mark.integration
@pytest.mark.slow
def test_connect_country(speedify_clean_state, server_countries):
    """Test connecting to servers in different countries."""
    # Test with 3 random countries to keep test time reasonable
    country_sample = random.sample(list(server_countries), min(3, len(server_countries)))

    for country in country_sample:
        serverinfo = speedify.connect_country(country)
        state = speedify.show_state()

        assert state == State.CONNECTED
        assert "tag" in serverinfo
        assert "country" in serverinfo
        assert serverinfo["country"] == country

        # Verify current server matches
        current = speedify.show_currentserver()
        assert current["country"] == country


@pytest.mark.integration
def test_disconnect(speedify_clean_state):
    """Test disconnecting from Speedify."""
    # Connect first
    speedify.connect_closest()
    assert speedify.show_state() == State.CONNECTED

    # Disconnect
    speedify.disconnect()
    state = speedify.show_state()
    assert state == State.LOGGED_IN


@pytest.mark.integration
def test_bad_country_raises_error(speedify_clean_state):
    """Test that connecting to invalid country raises SpeedifyAPIError."""
    state = speedify.show_state()
    assert state == State.LOGGED_IN

    with pytest.raises(SpeedifyAPIError):
        speedify.connect_country("pp")  # Invalid country code

    # State should remain LOGGED_IN after failed connection
    state = speedify.show_state()
    assert state == State.LOGGED_IN


# ============================================================================
# Settings Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.parametrize("mode", ["tcp", "https"])
def test_transport_modes(speedify_clean_state, mode):
    """Test setting different transport modes."""
    speedify.transport(mode)
    speedify.connect()

    settings = speedify.show_settings()
    assert settings["transportMode"] == mode


@pytest.mark.integration
@pytest.mark.parametrize("enabled", [False, True])
def test_basic_settings(speedify_clean_state, enabled):
    """Test toggling basic boolean settings."""
    speedify.packetaggregation(enabled)
    speedify.jumbo(enabled)

    settings = speedify.show_settings()
    assert settings["packetAggregation"] == enabled
    assert settings["jumboPackets"] == enabled


@pytest.mark.integration
@pytest.mark.parametrize("enabled", [False, True])
def test_header_compression(speedify_clean_state, enabled):
    """Test header compression settings."""
    result = speedify.headercompression(enabled)
    assert result["headerCompression"] == enabled


@pytest.mark.integration
@pytest.mark.parametrize("dns_ip", ["8.8.8.8", ""])
def test_dns_settings(speedify_clean_state, dns_ip):
    """Test DNS address configuration."""
    result = speedify.dns(dns_ip)
    expected = [dns_ip] if dns_ip != "" else []
    assert result["dnsAddresses"] == expected


# ============================================================================
# Connect Method Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.slow
def test_connectmethod(speedify_clean_state, server_countries):
    """Test different connection methods."""
    speedify.connect_closest()

    # Test private method
    country = random.choice(list(server_countries))
    speedify.connectmethod("private", country)

    cm_settings = speedify.show_connectmethod()
    assert cm_settings["connectMethod"] == "private"
    # Country is ignored for private/dedicated
    assert cm_settings["country"] == ""
    assert cm_settings["num"] == 0
    assert cm_settings["city"] == ""

    # Test p2p method
    speedify.connectmethod("p2p")
    cm_settings = speedify.show_connectmethod()
    assert cm_settings["connectMethod"] == "p2p"
    assert cm_settings["country"] == ""

    # Test country method with random countries
    country_sample = random.sample(list(server_countries), min(3, len(server_countries)))
    for country in country_sample:
        retval = speedify.connectmethod("country", country=country)
        cm_settings = speedify.show_connectmethod()

        assert cm_settings["connectMethod"] == "country"
        assert cm_settings["country"] == country

        # Returned value should match settings
        assert cm_settings["connectMethod"] == retval["connectMethod"]
        assert cm_settings["country"] == retval["country"]

    # Reset to closest
    speedify.connectmethod("closest")
    cm_settings = speedify.show_connectmethod()
    assert cm_settings["connectMethod"] == "closest"


# ============================================================================
# Show Commands Tests
# ============================================================================

@pytest.mark.integration
def test_show_commands_return_data(speedify_logged_in):
    """Test that all show_* commands return non-empty data."""
    show_functions = [
        speedify.show_servers,
        speedify.show_settings,
        speedify.show_privacy,
        speedify.show_adapters,
        speedify.show_currentserver,
        speedify.show_user,
        speedify.show_directory,
        speedify.show_connectmethod,
        speedify.show_streamingbypass,
        speedify.show_disconnect,
        speedify.show_streaming,
        speedify.show_speedtest,
    ]

    for func in show_functions:
        result = func()
        assert result is not None
        assert result != ""


@pytest.mark.integration
def test_show_version(speedify_logged_in):
    """Test version information retrieval."""
    version = speedify.show_version()

    assert "maj" in version
    assert version["maj"] > 7  # Expect at least Speedify 8.0
    assert "min" in version
    assert "bug" in version
    assert "build" in version


@pytest.mark.integration
def test_directory_setting(speedify_logged_in):
    """Test directory settings show prod or dev."""
    import re

    result = speedify.show_directory()["domain"]
    is_prod = result == ""
    is_dev = re.search(r"devdirectory.*", result) is not None

    assert is_prod or is_dev


# ============================================================================
# Server List Tests
# ============================================================================

@pytest.mark.integration
def test_serverlist(speedify_logged_in, server_list):
    """Test server list retrieval and connecting to specific server."""
    servers = speedify.show_servers()
    assert "public" in servers

    public_list = servers["public"]
    assert len(public_list) > 0

    server_info = public_list[0]
    assert "tag" in server_info
    assert "country" in server_info
    assert "city" in server_info
    assert "num" in server_info
    assert server_info["isPrivate"] is False

    # Connect to specific server
    new_server = speedify.connect(
        f"{server_info['country']} {server_info['city']} {server_info['num']}"
    )

    assert server_info["tag"] == new_server["tag"]
    assert server_info["country"] == new_server["country"]
    assert server_info["city"] == new_server["city"]
    assert server_info["num"] == new_server["num"]


# ============================================================================
# Streaming Bypass Tests
# ============================================================================

@pytest.mark.integration
def test_streamingbypass_domains(speedify_clean_state):
    """Test streaming bypass for domains."""
    domain = "test.example.com"

    # Add domain
    result = speedify.streamingbypass_domains_add(domain)
    assert domain in result["domains"]

    # Remove domain
    result = speedify.streamingbypass_domains_rem(domain)
    assert domain not in result["domains"]


@pytest.mark.integration
def test_streamingbypass_ipv4(speedify_clean_state):
    """Test streaming bypass for IPv4 addresses."""
    ip = "68.80.59.53"

    # Add IPv4
    result = speedify.streamingbypass_ipv4_add(ip)
    assert ip in result["ipv4"]

    # Remove IPv4
    result = speedify.streamingbypass_ipv4_rem(ip)
    assert ip not in result["ipv4"]


@pytest.mark.integration
def test_streamingbypass_ipv6(speedify_clean_state):
    """Test streaming bypass for IPv6 addresses."""
    ip = "2001:db8:1234:ffff:ffff:ffff:ffff:f0f"

    # Add IPv6
    result = speedify.streamingbypass_ipv6_add(ip)
    assert ip in result["ipv6"]

    # Remove IPv6
    result = speedify.streamingbypass_ipv6_rem(ip)
    assert ip not in result["ipv6"]


@pytest.mark.integration
def test_streamingbypass_ports(speedify_clean_state):
    """Test streaming bypass for ports."""
    port_num = "9999"

    def get_port(result):
        """Extract port number from result."""
        try:
            return result["ports"][0]["port"]
        except (IndexError, KeyError):
            return None

    # Add port
    result = speedify.streamingbypass_ports_add(f"{port_num}/tcp")
    assert get_port(result) == int(port_num)

    # Remove port
    result = speedify.streamingbypass_ports_rem(f"{port_num}/tcp")
    assert get_port(result) != int(port_num)


@pytest.mark.integration
@pytest.mark.slow
@pytest.mark.parametrize("service", ["Netflix", "Disney+", "Hulu"])
@pytest.mark.parametrize("enabled", [False, True])
def test_streamingbypass_service(speedify_clean_state, service, enabled):
    """Test streaming bypass for specific services."""
    result = speedify.streamingbypass_service(service, enabled)

    # Find the service in the result
    for item in result["services"]:
        if item["title"] == service:
            assert item["enabled"] == enabled
            break
    else:
        pytest.fail(f"Service '{service}' not found in results")


# ============================================================================
# Adapter Tests
# ============================================================================

@pytest.mark.integration
def test_adapters_exist(speedify_logged_in):
    """Test that adapters are available."""
    adapters = speedify.show_adapters()
    assert len(adapters) > 0
    assert "adapterID" in adapters[0]


@pytest.mark.integration
def test_adapter_priority(speedify_clean_state, adapter_ids):
    """Test setting adapter priority."""
    if not adapter_ids:
        pytest.skip("No adapters available")

    for adapter_id in adapter_ids:
        speedify.adapter_priority(adapter_id, Priority.BACKUP)

    # Verify priorities were set
    adapters = speedify.show_adapters()
    for adapter in adapters:
        # Disconnected adapters may have priority NEVER, which can't be changed
        if adapter["priority"] != Priority.NEVER.value:
            assert adapter["priority"] == Priority.BACKUP.value


@pytest.mark.integration
def test_adapter_ratelimit(speedify_clean_state, first_adapter_id):
    """Test setting adapter rate limits."""
    limit = 10000000  # 10 Mbps

    speedify.adapter_ratelimit(first_adapter_id, limit, limit)

    adapters = speedify.show_adapters()
    first_adapter = next(a for a in adapters if a["adapterID"] == first_adapter_id)

    assert first_adapter["rateLimit"]["uploadBps"] == limit
    assert first_adapter["rateLimit"]["downloadBps"] == limit


@pytest.mark.integration
def test_adapter_overratelimit(speedify_clean_state):
    """Test setting adapter overlimit rate limit."""
    adapters = speedify.show_adapters()
    if not adapters:
        pytest.skip("No adapters available")

    first_adapter_id = adapters[0]["adapterID"]
    original_limit = adapters[0]["dataUsage"]["overlimitRatelimit"]

    # Set new limit
    new_limit = 2000000
    result = speedify.adapter_overratelimit(first_adapter_id, new_limit)
    assert result[0]["dataUsage"]["overlimitRatelimit"] == new_limit

    # Restore original
    result = speedify.adapter_overratelimit(first_adapter_id, original_limit)
    assert result[0]["dataUsage"]["overlimitRatelimit"] == original_limit


@pytest.mark.integration
def test_adapter_encryption(speedify_clean_state, first_adapter_id):
    """Test per-adapter encryption settings."""
    # Set adapter-specific encryption to False
    speedify.adapter_encryption(first_adapter_id, False)

    settings = speedify.show_settings()
    assert settings["perConnectionEncryptionEnabled"] is True
    assert settings["encrypted"] is True  # Main encryption still on

    # Check per-connection settings
    per_conn_settings = settings["perConnectionEncryptionSettings"]
    first_setting = per_conn_settings[0]
    assert first_setting["adapterID"] == first_adapter_id
    assert first_setting["encrypted"] is False

    # Turn off all encryption
    speedify.encryption(False)
    settings = speedify.show_settings()
    assert settings["perConnectionEncryptionEnabled"] is False
    assert settings["encrypted"] is False

    # Turn encryption back on (should clear per-connection settings)
    speedify.encryption(True)
    settings = speedify.show_settings()
    assert settings["perConnectionEncryptionEnabled"] is False
    assert settings["encrypted"] is True


# ============================================================================
# Stats Tests
# ============================================================================

@pytest.mark.integration
def test_stats(speedify_connected):
    """Test statistics retrieval."""
    report_list = speedify.stats(2)

    assert report_list  # Non-empty list
    reports = [item[0] for item in report_list]
    assert "adapters" in reports  # At least one adapters report


@pytest.mark.integration
@pytest.mark.slow
def test_streamtest(speedify_connected):
    """Test stream testing functionality."""
    result = speedify.streamtest()
    assert result[0]["isError"] is False


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.integration
def test_invalid_command_raises_error(speedify_logged_in):
    """Test that invalid CLI command raises SpeedifyError."""
    with pytest.raises(SpeedifyError) as exc_info:
        speedify._run_speedify_cmd(["invalidcommand"])
    assert "Unknown Parameter" in exc_info.value.message


@pytest.mark.integration
def test_missing_required_argument_raises_error(speedify_logged_in):
    """Test that missing required argument raises SpeedifyError."""
    with pytest.raises(SpeedifyError) as exc_info:
        speedify._run_speedify_cmd(["overflow"])
    assert "Missing parameters" in exc_info.value.message


@pytest.mark.integration
def test_invalid_argument_raises_error(speedify_logged_in):
    """Test that invalid argument raises SpeedifyError."""
    with pytest.raises(SpeedifyError) as exc_info:
        speedify._run_speedify_cmd(["overflow", "bob"])
    assert "Invalid parameters" in exc_info.value.message


# ============================================================================
# Platform-Specific Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.windows
@pytest.mark.windows_only
def test_privacy_killswitch_windows(speedify_clean_state):
    """Test killswitch on Windows (Windows-only feature)."""
    # Enable killswitch
    speedify.killswitch(True)
    privacy_settings = speedify.show_privacy()
    assert privacy_settings["killswitch"] is True

    # Disable killswitch
    speedify.killswitch(False)
    privacy_settings = speedify.show_privacy()
    assert privacy_settings["killswitch"] is False


@pytest.mark.integration
@pytest.mark.unix_only
def test_privacy_killswitch_not_on_unix(speedify_clean_state):
    """Test that killswitch raises error on non-Windows platforms."""
    with pytest.raises(SpeedifyError):
        speedify.killswitch(True)
