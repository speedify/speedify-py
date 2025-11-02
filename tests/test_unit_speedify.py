"""
Unit tests for speedify module using mocking.

These tests do NOT require Speedify daemon to be running.
They test the library logic by mocking CLI interactions.

Run with: pytest tests/test_unit_speedify.py -m unit
"""
import json
import subprocess
from unittest.mock import Mock, patch, MagicMock

import pytest

import speedify
from speedify import State, Priority, SpeedifyError, SpeedifyAPIError


# ============================================================================
# CLI Finding and Path Tests
# ============================================================================

@pytest.mark.unit
def test_find_cli_checks_env_var_first():
    """Test that _find_cli checks SPEEDIFY_CLI environment variable first."""
    with patch.dict('os.environ', {'SPEEDIFY_CLI': '/custom/path/speedify_cli'}):
        with patch('os.path.isfile', return_value=True):
            # Reset the cached cli path
            speedify._cli_path = None

            cli_path = speedify._find_cli()
            assert cli_path == '/custom/path/speedify_cli'


@pytest.mark.unit
def test_set_cli_overrides_path():
    """Test that set_cli() overrides the CLI path."""
    custom_path = "/my/custom/speedify_cli"
    speedify.set_cli(custom_path)

    assert speedify.get_cli() == custom_path

    # Reset to None for other tests
    speedify._cli_path = None


@pytest.mark.unit
def test_get_cli_caches_path():
    """Test that get_cli() caches the found path."""
    with patch('speedify._find_cli', return_value='/found/path') as mock_find:
        speedify._cli_path = None

        # First call should invoke _find_cli
        path1 = speedify.get_cli()
        assert path1 == '/found/path'
        assert mock_find.call_count == 1

        # Second call should use cached value
        path2 = speedify.get_cli()
        assert path2 == '/found/path'
        assert mock_find.call_count == 1  # Still 1, not called again


# ============================================================================
# State Enum Tests
# ============================================================================

@pytest.mark.unit
def test_find_state_for_string():
    """Test converting string to State enum."""
    assert speedify.find_state_for_string("CONNECTED") == State.CONNECTED
    assert speedify.find_state_for_string("connected") == State.CONNECTED
    assert speedify.find_state_for_string(" LOGGED_IN ") == State.LOGGED_IN


@pytest.mark.unit
def test_find_state_for_invalid_string_raises():
    """Test that invalid state string raises KeyError."""
    with pytest.raises(KeyError):
        speedify.find_state_for_string("INVALID_STATE")


# ============================================================================
# Priority Enum Tests
# ============================================================================

@pytest.mark.unit
def test_priority_enum_values():
    """Test that Priority enum has expected values."""
    assert Priority.AUTOMATIC.value == "automatic"
    assert Priority.ALWAYS.value == "always"
    assert Priority.BACKUP.value == "backup"
    assert Priority.SECONDARY.value == "secondary"
    assert Priority.NEVER.value == "never"


# ============================================================================
# Exception Tests
# ============================================================================

@pytest.mark.unit
def test_speedify_error_creation():
    """Test SpeedifyError exception creation."""
    error = SpeedifyError("Test error message")
    assert error.message == "Test error message"


@pytest.mark.unit
def test_speedify_api_error_creation():
    """Test SpeedifyAPIError exception creation."""
    error = SpeedifyAPIError(
        error_code=1,
        error_type="TestError",
        error_message="Test API error"
    )

    assert error.error_code == 1
    assert error.error_type == "TestError"
    assert error.error_message == "Test API error"
    assert error.message == "Test API error"


# ============================================================================
# Command Execution Tests (Mocked)
# ============================================================================

@pytest.mark.unit
def test_run_speedify_cmd_success():
    """Test _run_speedify_cmd with successful response."""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = b'{"result": "success", "value": 42}'
    mock_result.stderr = b''

    with patch('subprocess.run', return_value=mock_result):
        with patch('speedify.get_cli', return_value='/path/to/cli'):
            result = speedify._run_speedify_cmd(['test', 'command'])

            assert result == {"result": "success", "value": 42}


@pytest.mark.unit
def test_run_speedify_cmd_handles_multiple_json_objects():
    """Test that _run_speedify_cmd parses the last JSON object from stdout."""
    mock_result = Mock()
    mock_result.returncode = 0
    # Simulate CLI that outputs multiple JSON objects (some CLIs do this)
    mock_result.stdout = b'{"log": "message1"}\n{"log": "message2"}\n{"result": "final"}'
    mock_result.stderr = b''

    with patch('subprocess.run', return_value=mock_result):
        with patch('speedify.get_cli', return_value='/path/to/cli'):
            result = speedify._run_speedify_cmd(['test'])

            # Should parse the last JSON object
            assert result == {"result": "final"}


@pytest.mark.unit
def test_run_speedify_cmd_error_response():
    """Test _run_speedify_cmd with error response."""
    import subprocess

    # Create a CalledProcessError to simulate the check=True behavior
    error = subprocess.CalledProcessError(
        returncode=1,
        cmd=['/path/to/cli', '-s', 'test', 'command'],
        output=b'',
        stderr=b'{"errorCode": 123, "errorType": "TestError", "errorMessage": "Something went wrong"}'
    )

    with patch('subprocess.run', side_effect=error):
        with patch('speedify.get_cli', return_value='/path/to/cli'):
            with pytest.raises(SpeedifyAPIError) as exc_info:
                speedify._run_speedify_cmd(['test', 'command'])

            assert exc_info.value.error_code == 123
            assert exc_info.value.error_type == "TestError"
            assert exc_info.value.error_message == "Something went wrong"


@pytest.mark.unit
def test_run_speedify_cmd_timeout():
    """Test _run_speedify_cmd with custom timeout."""
    mock_result = Mock()
    mock_result.returncode = 0
    mock_result.stdout = b'{"result": "success"}'
    mock_result.stderr = b''

    with patch('subprocess.run', return_value=mock_result) as mock_run:
        with patch('speedify.get_cli', return_value='/path/to/cli'):
            speedify._run_speedify_cmd(['test'], cmdtimeout=120)

            # Verify timeout was passed to subprocess.run
            call_kwargs = mock_run.call_args[1]
            assert call_kwargs['timeout'] == 120


# ============================================================================
# Utility Function Tests
# ============================================================================

@pytest.mark.unit
def test_use_shell_returns_correct_value():
    """Test use_shell() returns appropriate value for platform."""
    import platform

    result = speedify.use_shell()

    system = platform.system().lower()
    if system in ["darwin", "linux"]:
        assert result is False
    else:
        assert result is True


@pytest.mark.unit
def test_ping_internet_success():
    """Test ping_internet() with successful connection."""
    with patch('socket.socket') as mock_socket:
        mock_instance = MagicMock()
        mock_socket.return_value = mock_instance

        result = speedify.ping_internet()

        assert result is True
        mock_instance.connect.assert_called_once_with(("8.8.8.8", 53))


@pytest.mark.unit
def test_ping_internet_failure():
    """Test ping_internet() with failed connection."""
    import socket as socket_module

    with patch('socket.socket') as mock_socket:
        mock_instance = MagicMock()
        mock_instance.connect.side_effect = socket_module.error("Connection failed")
        mock_socket.return_value = mock_instance

        result = speedify.ping_internet()

        assert result is False


# ============================================================================
# Wrapper Function Tests (Mocked)
# ============================================================================

@pytest.mark.unit
def test_connect_calls_cli_correctly():
    """Test that connect() calls CLI with correct arguments."""
    mock_response = {"tag": "us-nyc-1", "country": "us"}

    with patch('speedify._run_speedify_cmd', return_value=mock_response) as mock_cmd:
        result = speedify.connect("us nyc 1")

        mock_cmd.assert_called_once_with(["connect", "us", "nyc", "1"])
        assert result == mock_response


@pytest.mark.unit
def test_connect_closest():
    """Test connect_closest() is shorthand for connect('closest')."""
    with patch('speedify.connect', return_value={"tag": "closest"}) as mock_connect:
        result = speedify.connect_closest()

        mock_connect.assert_called_once_with("closest")
        assert result == {"tag": "closest"}


@pytest.mark.unit
def test_disconnect_calls_cli():
    """Test that disconnect() calls CLI correctly."""
    with patch('speedify._run_speedify_cmd', return_value={}) as mock_cmd:
        result = speedify.disconnect()

        mock_cmd.assert_called_once_with(["disconnect"])
        assert result is True


@pytest.mark.unit
@pytest.mark.parametrize("mode", ["tcp", "udp", "https", "auto"])
def test_transport_modes(mode):
    """Test transport() with different modes."""
    mock_response = {"transportMode": mode}

    with patch('speedify._run_speedify_cmd', return_value=mock_response) as mock_cmd:
        result = speedify.transport(mode)

        mock_cmd.assert_called_once_with(["transport", mode])
        assert result == mock_response


@pytest.mark.unit
@pytest.mark.parametrize("enabled", [True, False])
def test_encryption(enabled):
    """Test encryption() with boolean values."""
    mock_response = {"encrypted": enabled}

    with patch('speedify._run_speedify_cmd', return_value=mock_response) as mock_cmd:
        result = speedify.encryption(enabled)

        expected_arg = "on" if enabled else "off"
        mock_cmd.assert_called_once_with(["encryption", expected_arg])
        assert result == mock_response


# ============================================================================
# Connectmethod String Conversion Tests
# ============================================================================

@pytest.mark.unit
def test_connectmethod_as_string_with_hyphens():
    """Test connectmethod_as_string() with hyphen separator."""
    cm_obj = {
        "connectMethod": "country",
        "country": "us",
        "city": "nova",
        "num": 2
    }

    result = speedify.connectmethod_as_string(cm_obj, hypens=True)
    assert result == "us-nova-2"


@pytest.mark.unit
def test_connectmethod_as_string_with_spaces():
    """Test connectmethod_as_string() with space separator."""
    cm_obj = {
        "connectMethod": "country",
        "country": "us",
        "city": "nova",
        "num": 2
    }

    result = speedify.connectmethod_as_string(cm_obj, hypens=False)
    assert result == "us nova 2"


@pytest.mark.unit
def test_connectmethod_as_string_closest():
    """Test connectmethod_as_string() with closest method."""
    cm_obj = {
        "connectMethod": "closest",
        "country": "",
        "city": "",
        "num": 0
    }

    result = speedify.connectmethod_as_string(cm_obj, hypens=True)
    assert result == "closest"


# ============================================================================
# Confirm State and List Servers Tests
# ============================================================================

@pytest.mark.unit
def test_confirm_state_speedify_matching():
    """Test confirm_state_speedify() with matching state."""
    with patch('speedify.show_state', return_value=State.CONNECTED):
        result = speedify.confirm_state_speedify(State.CONNECTED)
        assert result is True


@pytest.mark.unit
def test_confirm_state_speedify_not_matching():
    """Test confirm_state_speedify() with non-matching state."""
    with patch('speedify.show_state', return_value=State.LOGGED_IN):
        result = speedify.confirm_state_speedify(State.CONNECTED)
        assert result is False


@pytest.mark.unit
def test_list_servers_speedify_public_only():
    """Test list_servers_speedify() with public servers only."""
    mock_servers = {
        "public": [
            {"tag": "us-nyc-1", "country": "us"},
            {"tag": "uk-lon-1", "country": "uk"},
        ],
        "private": [
            {"tag": "dedicated-1", "country": "us"},
        ]
    }

    with patch('speedify.show_servers', return_value=mock_servers):
        result = speedify.list_servers_speedify(public=True, private=False)

        assert result == ["us-nyc-1", "uk-lon-1"]


@pytest.mark.unit
def test_list_servers_speedify_exclude_test():
    """Test list_servers_speedify() excludes test servers."""
    mock_servers = {
        "public": [
            {"tag": "us-nyc-1", "country": "us"},
            {"tag": "us-test-server", "country": "us"},
            {"tag": "uk-lon-1", "country": "uk"},
        ],
        "private": []
    }

    with patch('speedify.show_servers', return_value=mock_servers):
        result = speedify.list_servers_speedify(excludeTest=True)

        assert "us-nyc-1" in result
        assert "uk-lon-1" in result
        assert "us-test-server" not in result
