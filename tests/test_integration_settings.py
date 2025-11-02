"""
Integration tests for speedifysettings module.

These tests require:
- Speedify daemon to be running
- User to be logged in

Run with: pytest tests/test_integration_settings.py
"""
import logging

import pytest

import speedify
from speedify import State
import speedifysettings


logger = logging.getLogger(__name__)


# ============================================================================
# Settings Read/Write Tests
# ============================================================================

@pytest.mark.integration
def test_reset_settings(speedify_clean_state):
    """Test reading and reapplying current settings."""
    # Read current settings
    current_settings = speedifysettings.get_speedify_settings()

    # Write them back
    result = speedifysettings.apply_speedify_settings(current_settings)
    assert result is True


@pytest.mark.integration
def test_set_defaults(speedify_clean_state):
    """Test applying default settings."""
    # Change some settings away from defaults
    speedify.encryption(False)
    speedify.transport("tcp")

    # Apply defaults
    result = speedifysettings.apply_speedify_settings(speedifysettings.speedify_defaults)
    assert result is True

    # Verify defaults were applied
    settings = speedify.show_settings()
    assert settings["encrypted"] is True
    assert settings["jumboPackets"] is True
    assert settings["transportMode"] == "auto"


@pytest.mark.integration
def test_read_settings(speedify_clean_state):
    """Test reading settings into dictionary."""
    # Set known values
    speedify.encryption(False)
    speedify.transport("tcp")
    speedify.packetaggregation(False)

    # Read settings
    settings = speedifysettings.get_speedify_settings()

    # Verify
    assert "encryption" in settings
    assert settings["encryption"] is False
    assert "packet_aggregation" in settings
    assert settings["packet_aggregation"] is False
    assert "transport" in settings
    assert settings["transport"] == "tcp"
    assert "jumbo" in settings
    assert settings["jumbo"] is True  # Unchanged from setUp


@pytest.mark.integration
def test_set_json_settings(speedify_clean_state):
    """Test applying settings from JSON string."""
    json_string = '''{
        "encryption": false,
        "jumbo": false,
        "packet_aggregation": false,
        "transport": "tcp",
        "adapter_priority_wifi": "backup",
        "route_default": false
    }'''

    result = speedifysettings.apply_speedify_settings(json_string)
    assert result is True

    # Verify settings were applied
    settings = speedify.show_settings()
    assert settings["encrypted"] is False
    assert settings["jumboPackets"] is False
    assert settings["packetAggregation"] is False
    assert settings["enableDefaultRoute"] is False
    assert settings["transportMode"] == "tcp"


@pytest.mark.integration
def test_get_settings_as_json_string(speedify_clean_state):
    """Test getting settings as JSON string."""
    # Set some known values
    speedify.encryption(True)
    speedify.transport("auto")
    speedify.jumbo(True)

    # Get as JSON string
    json_string = speedifysettings.get_speedify_settings_as_json_string()

    assert json_string is not None
    assert isinstance(json_string, str)
    assert "encryption" in json_string
    assert "transport" in json_string


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.integration
def test_bad_json_nonexistent_setting(speedify_clean_state):
    """Test that applying nonexistent setting returns False."""
    json_string = '{"encryption_nonexistant": true}'

    result = speedifysettings.apply_speedify_settings(json_string)
    assert result is False


@pytest.mark.integration
def test_bad_json_wrong_data_type(speedify_clean_state):
    """Test that applying wrong data type returns False."""
    json_string = '{"jumbo": "bob", "transport": "auto"}'

    result = speedifysettings.apply_speedify_settings(json_string)
    assert result is False


@pytest.mark.integration
def test_bad_json_invalid_priority(speedify_clean_state):
    """Test that applying nonexistent priority returns False."""
    json_string = '{"adapter_priority_all": "frank"}'

    result = speedifysettings.apply_speedify_settings(json_string)
    assert result is False


# ============================================================================
# Individual Setting Tests
# ============================================================================

@pytest.mark.integration
@pytest.mark.parametrize("setting,value,verify_key,verify_value", [
    ("encryption", True, "encrypted", True),
    ("encryption", False, "encrypted", False),
    ("jumbo", True, "jumboPackets", True),
    ("jumbo", False, "jumboPackets", False),
    ("packet_aggregation", True, "packetAggregation", True),
    ("packet_aggregation", False, "packetAggregation", False),
    ("transport", "tcp", "transportMode", "tcp"),
    ("transport", "udp", "transportMode", "udp"),
    ("transport", "auto", "transportMode", "auto"),
    ("mode", "speed", "bondingMode", "speed"),
    ("mode", "redundant", "bondingMode", "redundant"),
])
def test_apply_individual_settings(speedify_clean_state, setting, value, verify_key, verify_value):
    """Test applying individual settings via apply_setting()."""
    speedifysettings.apply_setting(setting, value)

    settings = speedify.show_settings()
    assert settings[verify_key] == verify_value


@pytest.mark.integration
def test_apply_connectmethod_setting(speedify_clean_state):
    """Test applying connectmethod setting."""
    speedifysettings.apply_setting("connectmethod", "closest")

    cm_settings = speedify.show_connectmethod()
    assert cm_settings["connectMethod"] == "closest"


@pytest.mark.integration
def test_apply_overflow_threshold(speedify_clean_state):
    """Test applying overflow threshold setting."""
    threshold = 25.0
    speedifysettings.apply_setting("overflow_threshold", threshold)

    settings = speedify.show_settings()
    assert settings["overflowThreshold"] == threshold


# ============================================================================
# Adapter Settings Tests
# ============================================================================

@pytest.mark.integration
def test_apply_adapter_priority_all(speedify_clean_state, adapter_ids):
    """Test applying priority to all adapters."""
    if not adapter_ids:
        pytest.skip("No adapters available")

    json_string = '{"adapter_priority_all": "backup"}'
    result = speedifysettings.apply_speedify_settings(json_string)
    assert result is True

    # Verify (disconnected adapters may still be NEVER)
    adapters = speedify.show_adapters()
    for adapter in adapters:
        if adapter["priority"] != "never":
            assert adapter["priority"] == "backup"


@pytest.mark.integration
def test_apply_adapter_ratelimit(speedify_clean_state):
    """Test applying rate limit to all adapters."""
    json_string = '{"adapter_ratelimit": {"download_bps": 5000000, "upload_bps": 5000000}}'

    result = speedifysettings.apply_speedify_settings(json_string)
    assert result is True

    adapters = speedify.show_adapters()
    for adapter in adapters:
        assert adapter["rateLimit"]["downloadBps"] == 5000000
        assert adapter["rateLimit"]["uploadBps"] == 5000000


@pytest.mark.integration
def test_apply_adapter_data_limits(speedify_clean_state):
    """Test applying data limits to all adapters."""
    json_string = '''{
        "adapter_datalimit_daily_all": 1000000000,
        "adapter_datalimit_monthly_all": 30000000000
    }'''

    result = speedifysettings.apply_speedify_settings(json_string)
    assert result is True

    adapters = speedify.show_adapters()
    for adapter in adapters:
        assert adapter["dataUsage"]["usageDailyLimit"] == 1000000000
        assert adapter["dataUsage"]["usageMonthlyLimit"] == 30000000000
