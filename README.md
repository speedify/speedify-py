Speedify for Python
=======================

Lets you control [Speedify](https://speedify.com), the bonding VPN, from Python.  Nearly everything available to the user interface is available via this library.

This library exposes all of the functionality from the [Speedify CLI](https://support.speedify.com/article/285-speedify-command-line-interface).  

Tested on Windows, macOS, Ubuntu, Raspbian.

Automatically looks for `speedify_cli` in a number of standard locations.  

You can force it to use a particular location by either setting the environment variable `SPEEDIFY_CLI` or by calling `speedify.set_cli()`.  In either case it takes the full path of the `speedify_cli` executable.

Please see the documentation on our [CLI](https://support.speedify.com/article/285-speedify-cli) for more information on the commands and options available.

## Examples

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
    "adapter_datalimit_monthly_all" : 0, "adapter_ratelimit" : {"download_bps": 0, "upload_bps": 0},
    }'''

#Apply settings
apply_speedify_settings(speedify_settings)
#Print current settings
print(get_speedify_settings())
```

`privacy_killswitch` and `privacy_dnsleak` are only supported on Windows.

The example settings above contain all of the possible settings.

## Changelog

### Release 16.0.2

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
  - `streamingbypass_domains_add(str)`
  - `streamingbypass_domains_rem(str)`
  - `streamingbypass_domains_set(str)`
  - `streamingbypass_ipv4_add(str)`
  - `streamingbypass_ipv4_rem(str)`
  - `streamingbypass_ipv4_set(str)`
  - `streamingbypass_ipv6_add(str)`
  - `streamingbypass_ipv6_rem(str)`
  - `streamingbypass_ipv6_set(str)`
  - `streamingbypass_ports_add(str)`
  - `streamingbypass_ports_rem(str)`
  - `streamingbypass_ports_set(str)`
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

