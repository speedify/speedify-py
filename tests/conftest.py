"""
Pytest configuration and shared fixtures for speedify-py tests.

This module provides reusable fixtures for testing the speedify library.
"""
import os
import sys
import logging

import pytest

# Add parent directory to path so we can import speedify modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import speedify
from speedify import State, Priority, SpeedifyError
import speedifysettings


# Configure logging for tests
logging.basicConfig(
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "test.log")),
        logging.StreamHandler(sys.stdout)
    ],
    format="%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s",
    level=logging.INFO,
)


@pytest.fixture(scope="session")
def speedify_available():
    """
    Session-scoped fixture that checks if Speedify CLI is available.

    This fixture runs once per test session and skips all tests if
    Speedify CLI cannot be found.
    """
    try:
        cli_path = speedify.get_cli()
        if not cli_path or not os.path.exists(cli_path):
            pytest.skip("Speedify CLI not found")
        return True
    except Exception as e:
        pytest.skip(f"Speedify CLI not available: {e}")


@pytest.fixture(scope="session")
def speedify_logged_in(speedify_available):
    """
    Session-scoped fixture that ensures user is logged into Speedify.

    This fixture checks login state once per session. If not logged in,
    it skips all tests that require login.

    Note: Does not perform actual login to avoid credential management.
    """
    state = speedify.show_state()
    if state == State.LOGGED_OUT:
        pytest.skip("Not logged into Speedify - tests require logged in user")
    return True


@pytest.fixture
def speedify_disconnected(speedify_logged_in):
    """
    Fixture that ensures Speedify is disconnected before and after test.

    Yields control to test, then disconnects after test completes.
    """
    # Disconnect before test
    if speedify.show_state() == State.CONNECTED:
        speedify.disconnect()

    yield

    # Disconnect after test
    if speedify.show_state() == State.CONNECTED:
        speedify.disconnect()


@pytest.fixture
def speedify_connected(speedify_logged_in):
    """
    Fixture that ensures Speedify is connected before test.

    Connects to closest server before test, disconnects after.
    """
    # Connect if not already connected
    if speedify.show_state() != State.CONNECTED:
        speedify.connect_closest()

    yield

    # Disconnect after test
    speedify.disconnect()


@pytest.fixture
def speedify_default_settings(speedify_logged_in):
    """
    Fixture that resets Speedify to default settings before test.

    Applies default settings before test runs. This ensures consistent
    starting state for tests that depend on specific settings.
    """
    # Apply defaults before test
    speedifysettings.apply_speedify_settings(speedifysettings.speedify_defaults)

    yield

    # Optionally restore defaults after test (commented out to reduce test time)
    # speedifysettings.apply_speedify_settings(speedifysettings.speedify_defaults)


@pytest.fixture
def speedify_clean_state(speedify_logged_in):
    """
    Fixture that provides a clean Speedify state before each test.

    Sets standard test settings:
    - Disconnected
    - Encryption enabled
    - Auto transport
    - Jumbo packets enabled
    - Packet aggregation enabled
    - Route default enabled
    - Connect method: closest
    """
    # Disconnect
    if speedify.show_state() == State.CONNECTED:
        speedify.disconnect()

    # Set standard test configuration
    speedify.encryption(True)
    speedify.transport("auto")
    speedify.jumbo(True)
    speedify.packetaggregation(True)
    speedify.routedefault(True)
    speedify.connectmethod("closest")

    yield

    # Cleanup: disconnect after test
    if speedify.show_state() == State.CONNECTED:
        speedify.disconnect()


@pytest.fixture
def server_list():
    """
    Fixture that provides the current Speedify server list.

    Returns combined public and private server lists.
    """
    servers = speedify.show_servers()
    all_servers = servers.get("public", []) + servers.get("private", [])
    return all_servers


@pytest.fixture
def server_countries(server_list):
    """
    Fixture that provides a set of all available server countries.

    Useful for testing country-based connections.
    """
    return {server["country"] for server in server_list}


@pytest.fixture
def adapter_ids():
    """
    Fixture that provides list of current adapter IDs.

    Returns list of adapter IDs for testing adapter-specific settings.
    """
    adapters = speedify.show_adapters()
    return [adapter["adapterID"] for adapter in adapters]


@pytest.fixture
def first_adapter_id(adapter_ids):
    """
    Fixture that provides the ID of the first available adapter.

    Useful for tests that need to operate on a single adapter.
    """
    if not adapter_ids:
        pytest.skip("No adapters available for testing")
    return adapter_ids[0]


# Markers for skipping tests on specific platforms
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line(
        "markers", "windows_only: mark test to run only on Windows"
    )
    config.addinivalue_line(
        "markers", "unix_only: mark test to run only on Unix-like systems"
    )


def pytest_runtest_setup(item):
    """Skip tests based on platform markers."""
    if "windows_only" in item.keywords and os.name != "nt":
        pytest.skip("Test runs only on Windows")
    if "unix_only" in item.keywords and os.name == "nt":
        pytest.skip("Test runs only on Unix-like systems")
