.. _cli:

Speedify CLI
============

The Speedify CLI is a cross-platform utility to help command and monitor
Speedify without using the traditional user interface. It is meant to be
run on the same device that it is controlling.

The output from Speedify CLI is always one of the following: \* On
success, its exit value is 0 and it prints JSON to the console. If there
are more than one JSON objects they will be separated by double
newlines. \* On error, its exit value is 1 and the last line of its
output will be a non-JSON error message to the console. (Some longer
running commands can output some JSON before hitting an error and
returning. The last line is always the error message) \* On an invalid
set of options, its exit value will be 2 and it will output the plain
text usage instructions.

Speedify 7.5 introduced significant improvements in the CLI, which in
some cases, breaks compatibility with scripts which rely on the older
CLI. The older CLI is still available as "speedify\_cli\_legacy" in the
install folder. It will remain available until September 2019. Users
should transition to the new CLI before that date. # Usage

The CLI contains the following commands:

.. code:: text

  Usage : speedify_cli action
  Actions:
     adapter datalimit daily <adapter id> <data usage in bytes|unlimited>
     adapter datalimit dailyboost <adapter id> <additional bytes>
     adapter datalimit monthly <adapter id> <data usage in bytes|unlimited> <day of the month to reset on|0 for last 30 days>
     adapter encryption <adapter id> <on|off>
     adapter overlimitratelimit <adapter id> <speed in bits per second|0 to stop using>
     adapter priority <adapter id> <automatic|always|secondary|backup|never>
     adapter ratelimit <adapter id> <speed in bits per second|unlimited>
     adapter resetusage <adapter id>
     captiveportal check
     captiveportal login <on|off> <adapter id>
     headercompression <on|off>
     connect [ closest | public | private | p2p | <country> [<city> [<number>]] | last ]
     connectmethod < closest | public | private | p2p | <country> [<city> [<number>]] >
     daemon exit
     directory [directory server domain]
     dns <ip address> ...
     disconnect
     encryption <on|off>
     gateway [directory gateway uri]
     jumbo <on|off>
     login <username> [password]
     login auto
     login oauth [access token]
     logout
     mode <redundant|speed|streaming>
     overflow <speed in mbps>
     packetaggr <on|off>
     ports [port/proto] ...
     privacy requestToDisableDoH <on|off>
     route default <on|off>
     show < servers | settings | privacy | adapters | currentserver | user | directory | connectmethod | streamingbypass | disconnect | streaming | speedtest>
     speedtest
     streamtest
     startupconnect <on|off>
     state
     stats [historic | [duration in seconds] [current|day|week|month|total|<period in hours>] ...]
     streaming domains <add|rem|set> <domain> ...
     streaming ipv4 <add|rem|set> <ip address> ...
     streaming ipv6 <add|rem|set> <ip address> ...
     streaming ports <add|rem|set> [port[-portRangeEnd]/proto] ...
     streamingbypass domains <add|rem|set> <domain> ...
     streamingbypass ipv4 <add|rem|set> <ip address> ...
     streamingbypass ipv6 <add|rem|set> <ip address> ...
     streamingbypass ports <add|rem|set> <port[-portRangeEnd]/proto> ...
     streamingbypass service <service name> <on|off>
     transport <auto|tcp|tcp-multi|udp|https>
     version

Commands
--------

.. _adapter-datalimit-daily:

adapter datalimit daily <adapter id> <data usage in bytes\|unlimited>
---------------------------------------------------------------------

The ``adapter datalimit daily`` limit the data usage for a specific
adapter on a daily basis. The usage can be either limited in bytes or
unlimited. This will set the maxDaily value accordingly. The adapter
guid can be found by using the ``show adapters`` option. Whether the
adapter is disabled or rate limited is controlled by the
``adapter overlimitratelimit`` setting.

.. code:: text

    $ speedify_cli adapter datalimit daily {0748217D-A795-4D16-9034-4A4C68B52C1F} 0
    [{
            "adapterID":    "{0748217D-A795-4D16-9034-4A4C68B52C1F}",
            "description":  "ASIX AX88179 USB 3.0 to Gigabit Ethernet Adapter",
            "name": "USB Eth Home",
            "state":    "connected",
            "type": "Ethernet",
            "priority": "always",
            "connectedNetworkName": "",
            "connectedNetworkBSSID":    "",
            "rateLimit":    0,
            "dataUsage":    {
                "usageMonthly": 596463158,
                "usageDaily":   596463158,
                "usageMonthlyLimit":    0,
                "usageMonthlyResetDay": 0,
                "usageDailyLimit":  0,
                "usageDailyBoost":  0,
                "overlimitRatelimit":   0
            }
        }, {
    ...

adapter datalimit dailyboost <adapter id> <additional bytes>
------------------------------------------------------------

Bumps up the daily datalimit for today only on a specific adapter on a
daily basis. The adapter guid can be found by using the
``show adapters`` option.

.. code:: text

    $ speedify_cli adapter datalimit dailyboost {0748217D-A795-4D16-9034-4A4C68B52C1F} 0
    [{
            "adapterID":    "{0748217D-A795-4D16-9034-4A4C68B52C1F}",
            "description":  "ASIX AX88179 USB 3.0 to Gigabit Ethernet Adapter",
            "name": "USB Eth Home",
            "state":    "connected",
            "type": "Ethernet",
            "priority": "always",
            "connectedNetworkName": "",
            "connectedNetworkBSSID":    "",
            "rateLimit":    0,
            "dataUsage":    {
                "usageMonthly": 596467907,
                "usageDaily":   596467907,
                "usageMonthlyLimit":    0,
                "usageMonthlyResetDay": 0,
                "usageDailyLimit":  0,
                "usageDailyBoost":  0,
                "overlimitRatelimit":   0
            }
        }, {
    ...

.. _adapter-datalimit-monthly:

adapter datalimit monthly <adapter id> <data usage in bytes\|unlimited> <day of the month to reset on\|0 for last 30 days>
--------------------------------------------------------------------------------------------------------------------------

The ``adapter datalimit monthly`` sets a monthly data cap that resets on
a set date or lasts 30 days. The usage can be either limited in bytes or
unlimited. This will set the max and resetDay accordingly. Whether the
adapter is disabled or rate limited is controlled by the
``adapter overlimitratelimit`` setting.

.. code:: text

    $ speedify_cli adapter datalimit monthly {0748217D-A795-4D16-9034-4A4C68B52C1F} 2000000000 0
    [{
            "adapterID":    "{0748217D-A795-4D16-9034-4A4C68B52C1F}",
            "description":  "ASIX AX88179 USB 3.0 to Gigabit Ethernet Adapter",
            "name": "USB Eth Home",
            "state":    "connected",
            "type": "Ethernet",
            "priority": "always",
            "connectedNetworkName": "",
            "connectedNetworkBSSID":    "",
            "rateLimit":    0,
            "dataUsage":    {
                "usageMonthly": 596469615,
                "usageDaily":   596469615,
                "usageMonthlyLimit":    2000000000,
                "usageMonthlyResetDay": 0,
                "usageDailyLimit":  0,
                "usageDailyBoost":  0,
                "overlimitRatelimit":   0
            }
        }, {
    ...

.. _adapter-encryption:

adapter encryption <adapter id> <on\|off>
-----------------------------------------

Controls encryption on a single adapter. Note that using the
``encryption`` command will remove all per-adapter encryption settings.
Most of the time, you'll just want to use the ``encryption`` command
that changes all adapters at same time.

.. code:: text

    $ speedify_cli adapter encryption {0748217D-A795-4D16-9034-4A4C68B52C1F} off
    {
        "jumboPackets": true,
        "encrypted":    true,
        "allowChaChaEncryption":    true,
        "bondingMode":  "speed",
        "startupConnect":   true,
        "transportMode":    "auto",
        "forwardedPorts":   [{
                "protocol": "tcp",
                "port": 8001
            }],
        "perConnectionEncryptionEnabled":   true,
        "perConnectionEncryptionSettings":  [{
                "adapterID":    "{0748217D-A795-4D16-9034-4A4C68B52C1F}",
                "encrypted":    false
            }],
        "overflowThreshold":    30
    }

adapter overlimitratelimit <adapter id> <speed in bits per second\|0 to stop using>
-----------------------------------------------------------------------------------

When an ``adapter datalimit`` is hit, this rate limit (in bit per
second) is applied to the adapter. Set to 0 to disable the adapter.

.. code:: text

    $ speedify_cli adapter overlimitratelimit {0748217D-A795-4D16-9034-4A4C68B52C1F} 0
    [{
            "adapterID":    "{0748217D-A795-4D16-9034-4A4C68B52C1F}",
            "description":  "ASIX AX88179 USB 3.0 to Gigabit Ethernet Adapter",
            "name": "USB Eth Home",
            "state":    "connected",
            "type": "Ethernet",
            "priority": "always",
            "connectedNetworkName": "",
            "connectedNetworkBSSID":    "",
            "rateLimit":    0,
            "dataUsage":    {
                "usageMonthly": 596472725,
                "usageDaily":   596472725,
                "usageMonthlyLimit":    0,
                "usageMonthlyResetDay": 0,
                "usageDailyLimit":  0,
                "usageDailyBoost":  0,
                "overlimitRatelimit":   0
            }
        }, {
    ...

.. _adapter-priority:

adapter priority <adapter id> <always\|secondary\|backup\|never>
----------------------------------------------------------------

The ``adapter priority`` command allows the user to choose which adapter
gets one of the following priorities:

+-----------+--------------+
| Priority  | Description  |
+===========+==============+
| always    | Use whenever |
|           | connected    |
+-----------+--------------+
| secondary | Use less     |
|           | than Always  |
|           | connection-  |
|           | only when    |
|           | Always       |
|           | connections  |
|           | are          |
|           | congested or |
|           | not working  |
+-----------+--------------+
| backup    | Only use     |
|           | when other   |
|           | connections  |
|           | are          |
|           | unavailable  |
+-----------+--------------+
| never     | Adapter is   |
|           | not used     |
+-----------+--------------+

This will set priority as one of the above mentioned options
accordingly.

.. code:: text

    $ speedify_cli adapter priority {0748217D-A795-4D16-9034-4A4C68B52C1F} always
    [{
            "adapterID":    "{0748217D-A795-4D16-9034-4A4C68B52C1F}",
            "description":  "ASIX AX88179 USB 3.0 to Gigabit Ethernet Adapter",
            "name": "USB Eth Home",
            "state":    "connected",
            "type": "Ethernet",
            "priority": "always",
            "connectedNetworkName": "",
            "connectedNetworkBSSID":    "",
            "rateLimit":    0,
            "dataUsage":    {
                "usageMonthly": 596486806,
                "usageDaily":   596486806,
                "usageMonthlyLimit":    0,
                "usageMonthlyResetDay": 0,
                "usageDailyLimit":  0,
                "usageDailyBoost":  0,
                "overlimitRatelimit":   0
            }
        }, {
    ...

.. _adapter-ratelimit:

adapter ratelimit <adapter id> <speed in bits per second\|unlimited>
--------------------------------------------------------------------

The ``adapter ratelimit`` command allows the user to throttle the
adapter's maximum speed, in bits per second.

.. code:: text

    $ speedify_cli adapter ratelimit {0748217D-A795-4D16-9034-4A4C68B52C1F} 0
    [{
            "adapterID":    "{0748217D-A795-4D16-9034-4A4C68B52C1F}",
            "description":  "ASIX AX88179 USB 3.0 to Gigabit Ethernet Adapter",
            "name": "USB Eth Home",
            "state":    "connected",
            "type": "Ethernet",
            "priority": "always",
            "connectedNetworkName": "",
            "connectedNetworkBSSID":    "",
            "rateLimit":    0,
            "dataUsage":    {
                "usageMonthly": 596486806,
                "usageDaily":   596486806,
                "usageMonthlyLimit":    0,
                "usageMonthlyResetDay": 0,
                "usageDailyLimit":  0,
                "usageDailyBoost":  0,
                "overlimitRatelimit":   0
            }
        }, {
    ...

.. _adapter-resetusage:

adapter resetusage <adapter id>
--------------------------------------------------------------------

The ``adapter resetusage`` command allows resets the user's daily and monthly data caps.

.. code:: text

    $ speedify_cli adapter resetusage wlo1
    [{
    	"adapterID":	"wlo1",
    	"description":	"wlo1",
    	"name":	"wlo1",
    	"state":	"connected",
    	"type":	"Wi-Fi",
    	"priority":	"always",
    	"connectedNetworkName":	"",
    	"connectedNetworkBSSID":	"",
    	"rateLimit":	0,
    	"dataUsage":	{
    		"usageMonthly":	0,
    		"usageDaily":	0,
    		"usageMonthlyLimit":	0,
    		"usageMonthlyResetDay":	0,
    		"usageDailyLimit":	0,
    		"usageDailyBoost":	0,
    		"overlimitRatelimit":	0
    	}
    }, {
    ...

.. _connect:

connect [ closest \| public \| private \| p2p \| country [city [number]] \| last ]
----------------------------------------------------------------------------------

The ``connect`` command connects to a server based on your
``connectmethod`` setting, or a server of your choosing. It prints
details of the server it has selected.

The ``show servers`` command will give you a detailed list of servers
with their countries, cities and number as fields that you can use in
this command.

To connect to the nearest server in a particular country, pass along a
two-letter country code drawn from the ``speedify_cli show servers``
command:

.. code:: text

      $ speedify_cli connect ca

To connect to a particular city, pass along a two-letter country code
and city, drawn from the ``speedify_cli show servers`` command:

.. code:: text

      $ speedify_cli connect us-atlanta

To connect to a specific server, pass along a two-letter country code,
city, and number, drawn from the ``speedify_cli show servers`` command:

.. code:: text

      $ speedify_cli connect us-atlanta-3

Example:

.. code:: text

    $ speedify_cli connect
    {
        "tag":  "privateus-newark-18",
        "friendlyName": "United States - Newark #18",
        "country":  "us",
        "city": "newark",
        "num":  18,
        "isPrivate":    true,
        "torrentAllowed":   false,
        "publicIP": ["69.164.215.22"]
    }

.. _connectmethod:

connectmethod [closest \| public \| private \| p2p \| country [city [number]] ]
-------------------------------------------------------------------------------

The ``connect`` command connects to a server based on your
``connectmethod`` setting, or a server of your choosing. It prints
details of the server it has selected.

The ``show servers`` command will give you a detailed list of servers
with their countries, cities and number as fields that you can use in
this command.

To connect to the nearest server in a particular country, pass along a
two-letter country code drawn from the ``speedify_cli show servers``
command:

.. code:: text

      $ speedify_cli connect ca

To connect to a particular city, pass along a two-letter country code
and city, drawn from the ``speedify_cli show servers`` command:

.. code:: text

      $ speedify_cli connect us-atlanta

To connect to a specific server, pass along a two-letter country code,
city, and number, drawn from the ``speedify_cli show servers`` command:

.. code:: text

      $ speedify_cli connect us-atlanta-3

Example:

.. code:: text

    $ speedify_cli connect
    {
        "tag":  "privateus-newark-18",
        "friendlyName": "United States - Newark #18",
        "country":  "us",
        "city": "newark",
        "num":  18,
        "isPrivate":    true,
        "torrentAllowed":   false,
        "publicIP": ["69.164.215.22"]
    }

daemon exit
-----------

Causes the Speedify service to disconnect, and exit. In general, leave
this alone.

directory [directory server domain]
-----------------------------------

Controls the directory server. In general, leave this alone.

dns <ip address> ...
--------------------

The ``dns`` command sets the DNS servers to use for domain name
resolution.

.. code:: text

    $ speedify_cli dns 8.8.8.8
    {
      "dnsAddresses" :
      [
        "8.8.8.8"
      ],
      "requestToDisableDoH" : true
    }

disconnect
----------

The ``disconnect`` command disconnects from the server. It prints the
state immediately after the request to disconnect is made.

.. code:: text

    $ speedify_cli disconnect
    {
        "state":    "LOGGED_IN"
    }

.. _encryption:

encryption <on\|off>
--------------------

The ``encryption`` command enables or disables encryption of all
tunneled traffic. It prints the connection settings immediately after
the change is made. Note that this will clear all per-adapter encryption
settings from the ``adapter encryption`` command.

.. code:: text

    $ speedify_cli encryption off
    {
        "jumboPackets": true,
        "encrypted":    false,
        "allowChaChaEncryption":    true,
        "bondingMode":  "speed",
        "startupConnect":   true,
        "transportMode":    "auto",
        "forwardedPorts":   [{
                "protocol": "tcp",
                "port": 8001
            }],
        "perConnectionEncryptionEnabled":   false,
        "perConnectionEncryptionSettings":  [],
        "overflowThreshold":    30
    }

.. _jumbo:

jumbo <on\|off>
---------------

The ``jumbo`` command allows the TUN adapter to accept larger MTU
packets. This will set ``jumbo_packets`` to either ``True`` or
``False``.

.. code:: text

    $ speedify_cli jumbo on
    {
        "jumboPackets": true,
        "encrypted":    false,
        "allowChaChaEncryption":    true,
        "bondingMode":  "speed",
        "startupConnect":   true,
        "transportMode":    "auto",
        "forwardedPorts":   [{
                "protocol": "tcp",
                "port": 8001
            }],
        "perConnectionEncryptionEnabled":   false,
        "perConnectionEncryptionSettings":  [],
        "overflowThreshold":    30
    }

login <username> <password>
---------------------------

The ``login`` command instructs Speedify to connect with the given
username and password. It prints the state immediately after the request
to login is made. Speedify will then proceed to automatically connect if
the login succeeds.

.. code:: text

    $ speedify_cli speedify_cli.exe login user@domain.com password123
    {
            "state":        "LOGGED_IN"
    }

login auto
----------

The ``login auto`` command instructs Speedify to connect to a free
account with a set data limit. It prints the following state immediately
after the request is made.

.. code:: text

    $ speedify_cli speedify_cli.exe login auto
    {
            "state":        "LOGGED_IN"
    }

login oauth <access token>
--------------------------

The ``login oauth`` logs in with the user represented by encrypted token
passed in. It prints the state immediately after the request to login is
made. Speedify will then proceed to automatically connect if the login
succeeds.

.. code:: text

    $ speedify_cli speedify_cli.exe login oauth {encrypted_token}
    {
            "state":        "LOGGED_IN"
    }

logout
------

The ``logout`` command disconnects from the server and flushes any user
credentials that were stored.

.. code:: text

    $ speedify_cli speedify_cli.exe logout
    {
            "state":        "LOGGED_OUT"
    }

.. _mode:

mode <redundant\|speed>
-----------------------

The ``mode`` command instructs Speedify to optimize for maximum
connection speed or redundancy. Valid options are ``speed`` and
``redundant``.

.. code:: text

    $ speedify_cli mode speed
    {
        "jumboPackets": true,
        "encrypted":    false,
        "allowChaChaEncryption":    true,
        "bondingMode":  "speed",
        "startupConnect":   true,
        "transportMode":    "auto",
        "forwardedPorts":   [{
                "protocol": "tcp",
                "port": 8001
            }],
        "perConnectionEncryptionEnabled":   false,
        "perConnectionEncryptionSettings":  [],
        "overflowThreshold":    30
    }

.. _overflow:

overflow <speed in mbps>
------------------------

Speed in Mbps after which ``Secondary`` connections are not used.

.. code:: text

    $ speedify_cli overflow 10.0
    {
        "jumboPackets": true,
        "encrypted":    false,
        "allowChaChaEncryption":    true,
        "bondingMode":  "speed",
        "startupConnect":   true,
        "transportMode":    "auto",
        "forwardedPorts":   [{
                "protocol": "tcp",
                "port": 8001
            }],
        "perConnectionEncryptionEnabled":   false,
        "perConnectionEncryptionSettings":  [],
        "overflowThreshold":    10
    }

.. _packetaggr:

packetaggr <on|off>
------------------------

The ``packetaggr`` command sets packet aggregation on/off.

.. code:: text

    $ speedify_cli packetaggr on
    {
    	"jumboPackets":	true,
    	"encrypted":	false,
    	"allowChaChaEncryption":	true,
    	"bondingMode":	"speed",
    	"startupConnect":	true,
    	"transportMode":	"auto",
    	"packetAggregation":	true,
    	"forwardedPorts":	[{
    			"protocol":	"tcp",
    			"port":	8001
    		}],
    	"perConnectionEncryptionEnabled":	false,
    	"perConnectionEncryptionSettings":	[],
    	"overflowThreshold":	10
    }

.. _ports:

ports [port/proto] ...
----------------------

The ``ports`` command instructs Speedify to request public ports from a
Dedicated (private) Speed Server. These settings only go into effect
after a reconnect, and they are ignored by public Speed Servers.
Requesting a port that is already taken by another user will lead to the
connect request failing, and state will return to LOGGED\_IN. Calling
the ``ports`` command with no additional parameters will clear the port
forward requests.

.. code:: text

    $ speedify_cli ports 8001/tcp
    {
        "jumboPackets": true,
        "encrypted":    false,
        "allowChaChaEncryption":    true,
        "bondingMode":  "speed",
        "startupConnect":   true,
        "transportMode":    "auto",
        "forwardedPorts":   [{
                "protocol": "tcp",
                "port": 8001
            }],
        "perConnectionEncryptionEnabled":   false,
        "perConnectionEncryptionSettings":  [],
        "overflowThreshold":    10
    }

privacy dnsleak <on\|off>
-------------------------

A Windows-only setting to ensure DNS cannot go around the tunnel. This
could make certain LAN based printers and shared drivers inaccessible.

.. code:: text

    $ speedify_cli privacy dnsleak off
    {
        "crashReports": true,
        "killswitch":   false,
        "dnsleak":  false,
        "dnsAddreses":  ["8.8.8.8"]
    }

.. _privacy-killswitch:

privacy killswitch <on\|off>
----------------------------

A Windows-only setting that configures firewall rules to make it
impossible to access the internet when Speedify is not connected.

.. code:: text

    $ speedify_cli privacy killswitch off
    {
        "crashReports": true,
        "killswitch":   false,
        "dnsleak":  false,
        "dnsAddreses":  ["8.8.8.8"]
    }


.. _show-servers:

show servers
------------

The ``show servers`` command retrieves the current list of Speed
Servers. If you have access to any Dedicated Speed Servers, they appear
in a ``private`` array. The public pool of Speed Servers appear in a
``public`` array.

.. code:: text

    $ speedify_cli show servers
    {
        "public":   [{
                "tag":  "de-dusseldorf-1",
                "country":  "de",
                "city": "dusseldorf",
                "num":  1,
                "isPrivate":    false
            }, {
                "tag":  "us-newark-3",
                "country":  "us",
                "city": "newark",
                "num":  3,
                "isPrivate":    false
            }, {
                "tag":  "us-philadelphia-1",
                "country":  "us",
                "city": "philadelphia",
                "num":  1,
                "isPrivate":    false
            }, {
    ...
    
.. _show-settings:

show settings
-------------

The ``show settings`` command retrieves the current connection settings.
These settings are sent to the server at connect time, and they can be
retrieved at any time.

.. code:: text

    $ speedify_cli show settings
    {
        "jumboPackets": true,
        "encrypted":    false,
        "allowChaChaEncryption":    true,
        "bondingMode":  "speed",
        "startupConnect":   true,
        "transportMode":    "auto",
        "forwardedPorts":   [{
                "protocol": "tcp",
                "port": 8001
            }],
        "perConnectionEncryptionEnabled":   false,
        "perConnectionEncryptionSettings":  [],
        "overflowThreshold":    10
    }

.. _show-privacy:

show privacy
------------

Outputs privacy related settings

.. code:: text

    $ speedify_cli show privacy
    {
      "dnsAddresses" :
      [
        "8.8.8.8"
      ],
      "requestToDisableDoH" : true
    }

.. _show-adapters:

show adapters
-------------

The ``show adapters`` command allows the user to view all of the network
adapters, and their settings and statistics.

.. code:: text

    $ speedify_cli show adapters
    [{
            "adapterID":    "{0748217D-A795-4D16-9034-4A4C68B52C1F}",
            "description":  "ASIX AX88179 USB 3.0 to Gigabit Ethernet Adapter",
            "name": "USB Eth Home",
            "state":    "connected",
            "type": "Ethernet",
            "priority": "always",
            "connectedNetworkName": "",
            "connectedNetworkBSSID":    "",
            "rateLimit":    0,
            "dataUsage":    {
                "usageMonthly": 596537431,
                "usageDaily":   596537431,
                "usageMonthlyLimit":    0,
                "usageMonthlyResetDay": 0,
                "usageDailyLimit":  0,
                "usageDailyBoost":  0,
                "overlimitRatelimit":   0
            }
        }, {
    ...

.. _show-currentserver:

show currentserver
------------------

The ``show currentserver`` command displays the last server Speedify was
connected (which, if you are connected is the current server).

.. code:: text

    $ speedify_cli show currentserver
    {
        "tag":  "privateus-newark-18",
        "friendlyName": "United States - Newark #18",
        "country":  "us",
        "city": "newark",
        "num":  18,
        "isPrivate":    true,
        "torrentAllowed":   false,
        "publicIP": ["69.164.215.22"]
    }

.. _show-user:

show user
---------

Outputs information about the currently logged in user.

.. code:: text

    $ speedify_cli show user
    {
        "email":    "user@connectify.me",
        "isAutoAccount":    false,
        "isTeam":   true,
        "bytesUsed":    113576764188,
        "bytesAvailable":   -1
    }

show directory
--------------

The ``show directory`` command shows the current directory server.

.. code:: text

    $ speedify_cli show directory
    {
        "domain":   "dir-host-us-newark-3.speedifynetworks.com"
    }

.. _show-connectmethod:

show connectmethod
------------------

The ``show currentserver`` command displays information the last server
to which Speedify connected.

.. code:: text

    $ speedify_cli show connectmethod
    {
        "connectmethod":    "closest",
        "country":  "",
        "city": "",
        "num":  0
    }

.. _speedtest:

speedtest [showProgress]
------------------------

The ``speedtest`` command runs a lengthy and bandwidth intensive test to
check the upload and download speeds while using Speedify. Using
``speedtest showProgress`` reports real time information regarding the
speedtest.

.. code:: text

    $ speedify_cli speedify_cli.exe speedtest
    {
            "status":       "complete",
            "connectionResults":    [{
                            "adapterID":    "speedify",
                            "step": "not running",
                            "stepProgress": 0,
                            "rttMs":        11,
                            "downloadBps":  27821054.398594771,
                            "uploadBps":    30886263.91853809
                    }]
    }

.. _startupconnect:

startupconnect <on\|off>
------------------------

The ``startupconnect`` option tells Speedify if it should connect
automatically at startup or not. It prints the current settings
immediately after the request is made.

.. code:: text

    $ speedify_cli startupconnect on
    {
        "jumboPackets": true,
        "encrypted":    false,
        "allowChaChaEncryption":    true,
        "bondingMode":  "speed",
        "startupConnect":   true,
        "transportMode":    "auto",
        "forwardedPorts":   [{
                "protocol": "tcp",
                "port": 8001
            }],
        "perConnectionEncryptionEnabled":   false,
        "perConnectionEncryptionSettings":  [],
        "overflowThreshold":    10
    }

state
-----

The ``state`` command retrieves the current state of the connection.
Possible states are ``LOGGED_OUT``, ``LOGGING_IN``, ``LOGGED_IN``,
``AUTO_CONNECTING``, ``CONNECTING``, ``DISCONNECTING``, ``CONNECTED``,
``OVERLIMIT``, and ``UNKNOWN``

.. code:: text

    $ speedify_cli state
    {
        "state":    "CONNECTED"
    }

stats [duration in seconds]
---------------------------

The ``stats`` command subscribes to a feed of connection and session
statistics. By default, this feed will continue until the speedify\_cli
process is terminated, but an optional parameter can be given to stop
and exit after the given number of seconds. This can be useful to
monitor how many connections are being utilized by Speedify, and what
their current network activity level is in bytes per second.

.. code:: text

    $ speedify_cli stats 1

.. _transport:

transport <auto\|tcp\|udp\>
---------------------------

The ``transport`` command instructs Speedify to choose between one of
the network protocols ``auto``, ``tcp`` or ``udp``. The
``transport_mode`` value is set accordingly based on the user's
selection.

.. code:: text

    $ speedify_cli transport udp
    {
        "jumboPackets": true,
        "encrypted":    false,
        "allowChaChaEncryption":    true,
        "bondingMode":  "speed",
        "startupConnect":   true,
        "transportMode":    "udp",
        "forwardedPorts":   [{
                "protocol": "tcp",
                "port": 8001
            }],
        "perConnectionEncryptionEnabled":   false,
        "perConnectionEncryptionSettings":  [],
        "overflowThreshold":    10
    }

.. _version:

version
-------

The ``version`` command can be used to verify the version of Speedify
that is installed and running.

.. code:: text

    $ speedify_cli version
    {
        "maj":  7,
        "min":  5,
        "bug":  0,
        "build":    6498
    }
