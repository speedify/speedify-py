Speedify for Python
=======================

Lets you control [Speedify](https://speedify.com), the bonding VPN, from Python.  Nearly everything available to th)e user interface is available via this library.

This library exposes all of the functionality from the [Speedify CLI](https://support.speedify.com/article/285-speedify-command-line-interface).  

Tested on Windows, macOS, Ubuntu, Raspbian.

Automatically looks for speedify_cli in a number of standard locations.  

You can force it to use a particular location by either setting the environment variable SPEEDIFY_CLI or by calling speedify.set_cli().  In either case it takes the full path of the speedify_cli executable.

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
    "mode" : "speed", "privacy_killswitch":false, "privacy_dnsleak": true, "privacy_crashreports": true,
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
