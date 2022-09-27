Speedify for Python
=======================

Lets you control [Speedify](https://speedify.com), the bonding VPN, from Python.  Nearly everything available to the user interface is available via this library.

This library exposes all of the functionality from the [Speedify CLI](https://support.speedify.com/article/285-speedify-command-line-interface).  

Tested on Windows, macOS, Ubuntu, Raspbian.

Automatically looks for `speedify_cli` in a number of standard locations.  

You can force it to use a particular location by either setting the environment variable `SPEEDIFY_CLI` or by calling `speedify.set_cli()`.  In either case it takes the full path of the `speedify_cli` executable.

## Usage

Put Speedify in speed mode with UDP transport
```python
import speedify
speedify.mode("speed")
speedify.transport("udp")
```

Alternatively:
```python
from speedifysettings import apply_setting
#Put Speedify in speed mode with UDP transport
apply_setting("mode", "speed")
apply_setting("transport", "udp")
```

Apply multiple settings at once, and print current settings:
```python
from speedifysettings import apply_speedify_settings, get_speedify_settings

speedify_settings = '''{"connectmethod" : "closest","encryption" : true, "jumbo" : true,
    "mode" : "speed", "privacy_killswitch":false, "privacy_dnsleak": true, 
    "startupconnect": true,    "transport":"auto","overflow_threshold": 30.0,
    "adapter_priority_ethernet" : "always","adapter_priority_wifi" : "always",
    "adapter_priority_cellular" : "secondary", "adapter_datalimit_daily_all" : 0,
    "adapter_datalimit_monthly_all" : 0, "adapter_ratelimit_all" : 0
    }'''

#Apply settings
apply_speedify_settings(speedify_settings)
#Print current settings
print(get_speedify_settings())
```

For the full list of settings, build the sphinx documentation by running make html in the docs/ folder.

## Changelog

### Release 12.5.x

Added
  - `dns(str)`
  - `streamtest()`
  - `directory(str)`
  - `gateway(str)`
  - `esni(bool)`
  - `headercompression(bool)`
  - `privacy(str, bool)`
  - `daemon(str)`
  - `login_auto()`
  - `login_oauth(token)`
  - `streamingbypass_domains(str, str)`
  - `streamingbypass_ports(str, str)`
  - `streamingbypass_ipv4(str, str)`
  - `streamingbypass_ipv6(str, str)`
  - `streamingbypass_service(str, bool)`
  - `adapter_overratelimit(str, int)`
  - `adapter_dailylimit_boost(str, int)`
  - `show_servers()`
  - `show_settings()`
  - `show_privacy()`
  - `show_adapters()`
  - `show_currentserver()`
  - `show_user()`
  - `show_directory()`
  - `show_connectmethod()`
  - `show_streamingbypass()`
  - `show_disconnect()`
  - `show_streaming()`
  - `show_speedtest()`

Changed
  - `adapter_encryption(str, str) -> adapter_encryption(str, str or bool)`
  - `encryption(str) -> encryption(str or bool)`
  - `mode(str = "speed") -> mode(str)`

