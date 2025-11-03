# Speedify-py Test Suite

This directory contains the test suite for speedify-py, organized into unit tests and integration tests.

## Table of Contents

- [Test Organization](#test-organization)
- [Running Tests](#running-tests)
- [Test Types](#test-types)
- [Prerequisites](#prerequisites)
- [Writing Tests](#writing-tests)

## Test Organization

The test suite is organized into several files:

### Unit Tests (No Speedify Required)
- **test_unit_speedify.py** - Unit tests for speedify.py module using mocking
  - Tests CLI path finding logic
  - Tests enum conversions
  - Tests command building
  - Tests error handling
  - ~500 lines, runs in <1 second

### Integration Tests (Speedify Required)
- **test_integration_speedify.py** - Integration tests for speedify.py module
  - Tests actual CLI communication
  - Tests connection management
  - Tests settings configuration
  - Tests adapter management
  - Tests streaming bypass features
  - ~500 lines, runs in ~60 seconds

### Legacy Tests (unittest)
- **test_speedify.py** - Original unittest-based tests (kept for compatibility)
  - ~470 lines, runs in ~120 seconds

### Configuration
- **conftest.py** - Pytest fixtures and configuration
  - Shared test fixtures
  - Platform-specific test markers
  - Session-scoped setup

## Running Tests

### Install Test Dependencies

```bash
# Install with test dependencies
pip install -e ".[test]"

# Or install pytest separately
pip install pytest pytest-mock pytest-cov
```

### Run All Tests

```bash
# Run everything (including legacy tests)
pytest

# Run only pytest-style tests (recommended)
pytest tests/test_integration_*.py tests/test_unit_*.py
```

### Run Specific Test Types

```bash
# Run only unit tests (no Speedify daemon needed)
pytest -m unit

# Run only integration tests (requires Speedify)
pytest -m integration

# Run fast tests only (excludes slow integration tests)
pytest -m "not slow"

# Run Windows-specific tests only
pytest -m windows

# Run Unix-specific tests only
pytest -m unix_only
```

### Run Specific Test Files

```bash
# Run only unit tests
pytest tests/test_unit_speedify.py

# Run only integration tests for main module
pytest tests/test_integration_speedify.py
```

### Run Specific Tests

```bash
# Run a single test function
pytest tests/test_unit_speedify.py::test_find_cli_checks_env_var_first

# Run all tests matching a pattern
pytest -k "test_connect"

# Run tests in a specific class (legacy tests only)
pytest tests/test_speedify.py::TestSpeedify::test_dns
```

### Run with Coverage

```bash
# Generate coverage report
pytest --cov=speedify --cov-report=html

# View coverage report
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Run with Verbose Output

```bash
# Show test names as they run
pytest -v

# Show print statements
pytest -s

# Show detailed failure info
pytest -vv

# Show all output
pytest -vv -s
```

### Legacy Test Runner

```bash
# Run using the old unittest runner
python runtests.py

# Run single legacy test
python -m unittest tests.test_speedify.TestSpeedify.test_dns
```

## Test Types

### Unit Tests (`@pytest.mark.unit`)

**No Speedify daemon required** - These tests use mocking to test library logic without requiring Speedify to be installed or running.

**What they test:**
- CLI path finding and configuration
- Enum conversions and validation
- Command argument building
- Error handling and exceptions
- Utility functions (ping_internet, use_shell, etc.)
- JSON parsing logic

**Run with:**
```bash
pytest -m unit
```

### Integration Tests (`@pytest.mark.integration`)

**Requires Speedify daemon** - These tests communicate with the actual Speedify CLI and daemon.

**Prerequisites:**
- Speedify installed on the system
- Speedify daemon running
- User logged into Speedify account
- Active network adapters

**What they test:**
- Actual CLI communication
- Server connections
- Settings persistence
- Adapter configuration
- Network routing verification
- Streaming bypass functionality

**Run with:**
```bash
pytest -m integration
```

### Slow Tests (`@pytest.mark.slow`)

Tests that take more than 5 seconds (usually due to network operations or connecting to multiple servers).

**Exclude with:**
```bash
pytest -m "not slow"
```

### Platform-Specific Tests

**Windows-only tests** (`@pytest.mark.windows`):
- Privacy killswitch (Windows only feature)
- DNS leak protection (Windows only feature)

**Unix-only tests** (`@pytest.mark.unix_only`):
- Tests that verify certain features are NOT available on non-Windows platforms

**Run platform-specific:**
```bash
pytest -m windows      # Windows tests
pytest -m unix_only    # Unix tests
```

## Prerequisites

### For Unit Tests
- Python 3.7+
- pytest
- pytest-mock

### For Integration Tests
- All unit test requirements, plus:
- Speedify installed and running
- Valid Speedify account (logged in)
- Network connectivity

### Installing Speedify

See https://speedify.com for installation instructions.

### Logging Into Speedify

The test suite does NOT handle login/logout to avoid credential management. You must be logged in before running integration tests:

```bash
# Using Speedify CLI
speedify_cli login <username> <password>

# Or use the Speedify GUI to log in
```

The tests will skip automatically if not logged in.

## Writing Tests

### Using Fixtures

```python
import pytest
import speedify

@pytest.mark.integration
def test_my_feature(speedify_connected):
    """Test requires active connection."""
    # speedify_connected fixture ensures we're connected
    # and will disconnect after test

    result = speedify.some_function()
    assert result == expected
```

### Available Fixtures

- `speedify_available` - Session: Checks if Speedify CLI is available
- `speedify_logged_in` - Session: Ensures user is logged in
- `speedify_disconnected` - Function: Ensures disconnected before/after test
- `speedify_connected` - Function: Connects before test, disconnects after
- `speedify_default_settings` - Function: Resets to default settings before test
- `speedify_clean_state` - Function: Standard clean state for testing
- `server_list` - Function: Provides list of available servers
- `server_countries` - Function: Set of available server countries
- `adapter_ids` - Function: List of adapter IDs
- `first_adapter_id` - Function: ID of first adapter

### Parametrized Tests

```python
@pytest.mark.integration
@pytest.mark.parametrize("mode", ["tcp", "udp", "https", "auto"])
def test_transport_modes(speedify_clean_state, mode):
    """Test all transport modes."""
    speedify.transport(mode)
    settings = speedify.show_settings()
    assert settings["transportMode"] == mode
```

### Mocking for Unit Tests

```python
from unittest.mock import patch
import pytest
import speedify

@pytest.mark.unit
def test_connect_builds_correct_command():
    """Test that connect() builds CLI command correctly."""
    with patch('speedify._run_speedify_cmd') as mock_cmd:
        mock_cmd.return_value = {"tag": "us-nyc-1"}

        speedify.connect("us nyc 1")

        mock_cmd.assert_called_once_with(["connect", "us", "nyc", "1"])
```

### Platform-Specific Tests

```python
import pytest

@pytest.mark.integration
@pytest.mark.windows_only
def test_windows_feature(speedify_clean_state):
    """Test Windows-only feature."""
    # This test will be skipped on non-Windows platforms
    speedify.killswitch(True)
    # ...
```

### Error Testing

```python
import pytest
from speedify import SpeedifyAPIError

@pytest.mark.integration
def test_invalid_country(speedify_clean_state):
    """Test that invalid country raises error."""
    with pytest.raises(SpeedifyAPIError) as exc_info:
        speedify.connect_country("invalid")

    assert "country" in exc_info.value.error_message.lower()
```

## Test Markers

All available markers:

- `@pytest.mark.unit` - Unit tests (no Speedify required)
- `@pytest.mark.integration` - Integration tests (Speedify required)
- `@pytest.mark.slow` - Slow tests (>5 seconds)
- `@pytest.mark.windows` - Windows-specific features
- `@pytest.mark.windows_only` - Must run on Windows
- `@pytest.mark.unix_only` - Must run on Unix-like systems

## Continuous Integration

For CI/CD pipelines:

```bash
# Run only unit tests (no Speedify installation needed)
pytest -m unit --cov=speedify

# Run all tests if Speedify is installed in CI environment
pytest --cov=speedify --cov-report=xml
```

## Troubleshooting

### Tests Skipped: "Not logged into Speedify"

**Solution:** Log into Speedify before running tests:
```bash
speedify_cli login <username> <password>
```

### Tests Skipped: "Speedify CLI not found"

**Solution:** Install Speedify or set SPEEDIFY_CLI environment variable:
```bash
export SPEEDIFY_CLI=/path/to/speedify_cli
pytest
```

### Tests Fail: Connection Errors

**Solution:**
- Ensure Speedify daemon is running
- Check network connectivity
- Verify you have at least one active network adapter

### Tests Fail: Permission Errors

**Solution:** Some operations may require elevated privileges. Try running with appropriate permissions for your OS.

## Contributing

When adding new tests:

1. **Add unit tests** for new utility functions or parsing logic
2. **Add integration tests** for new CLI commands or features
3. **Use fixtures** to reduce setup/teardown code
4. **Use parametrize** for testing multiple similar cases
5. **Mark tests appropriately** with pytest markers
6. **Document prerequisites** in test docstrings
7. **Keep tests fast** - mark slow tests with `@pytest.mark.slow`

## Questions?

See the main README.md or visit https://github.com/speedify/speedify-py/issues
