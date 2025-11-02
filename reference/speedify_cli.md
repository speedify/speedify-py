# Speedify CLI
The Speedify CLI is a cross-platform utility to help command and monitor Speedify without using the traditional user interface.  It is meant to be run on the same device that it is controlling.

The output from Speedify CLI is always one of the following:

   * On success, its exit value is 0 and it prints JSON to the console.  If there are more than one JSON objects they will be separated by double newlines.
   * On error, its exit value is one of the following:
     * 1 = Error from the Speedify API, outputs a JSON error on stderr
     * 2 = Invalid Parameter, outputs a text error message on stderr
     * 3 = Missing Parameter, outputs a text error message on stderr
     * 4 = Unknown Parameter, outputs the full usage message on stderr

For errors from the Speedify API (1), a JSON error message is emitted on stderr.  This error contains the fields:

   * "errorCode" - a numeric code representing this error,
   * "errorType" - a short text code of the error category
   * "errorMessage" - a plain text message about the problem

Example Speedify API error message:
```text
{
        "errorCode":    3841,
        "errorType":    "Timeout waiting for result",
        "errorMessage": "Timeout"
}
```

On Windows, the executable command is `speedify_cli.exe`. On Linux and Mac, it is `speedify_cli`. For the example commands below, we will use the Linux/Mac name. Add `.exe` if you are using Windows.

On Windows and Linux, please ensure that the background service is running.

On macOS, please ensure that Speedify is open and running to use the CLI.

# Usage

The CLI contains the following commands:
```text

speedify_cli v15.7.2.0
Usage : speedify_cli [-s] [-t] action
   -s : single line output
   -t : give all outputs a title
Actions:
   activationcode
   adapter datalimit daily <adapter id> <data usage in bytes|unlimited>
   adapter datalimit dailyboost <adapter id> <additional bytes>
   adapter datalimit monthly <adapter id> <data usage in bytes|unlimited> <day of the month to reset on|0 for last 30 days>
   adapter directionalmode <adapter id> <upload mode (on | backup_off | strict_off)> <download mode (on | backup_off | strict_off)>
   adapter encryption <adapter id> <on|off>
   adapter expose-dscp <adapter id> <on|off>
   adapter overlimitratelimit <adapter id> <speed in bits per second|0 to stop using>
   adapter priority <adapter id> <automatic|always|secondary|backup|never>
   adapter ratelimit <adapter id> <download speed in bits per second|unlimited> <upload speed in bits per second|unlimited>
   adapter resetusage <adapter id>
   captiveportal check
   captiveportal login <on|off> <adapter id>
   headercompression <on|off>
   connect [ closest | public | private | p2p | <country> [<city> [<number>]] | last | <tag> ]
   connectmethod < closest | public | private | p2p | <country> [<city> [<number>]] | <tag> >
   connectretry <time in seconds>
   daemon exit
   directory [directory server domain]
   dns <ip address> ...
   disconnect
   dscp queues <add|rem|set> ...
   dscp queues add [<dscp value 0-63> [priority] <on|off|auto> [replication] <on|off|auto> [retransmissions] <0-255>] ...
   dscp queues set [<dscp value 0-63> [priority] <on|off|auto> [replication] <on|off|auto> [retransmissions] <0-255>] ...
   dscp queues rem [dscp value 0-63] ...
   encryption <on|off>
   fixeddelay <domains|ips|ports|delay in ms>
   fixeddelay domains <add|rem|set> <domain> ...
   fixeddelay ips <add|rem|set> <ip address> ...
   fixeddelay ports <add|rem|set> [port[-portRangeEnd]/proto] ...
   gateway [directory gateway uri]
   jumbo <on|off>
   login <username> [password]
   login auto
   login oauth [access token]
   logout
   maxredundant <number of conns>
   mode <redundant|speed|streaming>
   networksharing set alwaysOnDiscovery <on|off>
   networksharing availableshares
   networksharing connect <peer connect code>
   networksharing discovery
   networksharing peer <allow|reject|request|unpair> <peer uuid>
   networksharing reconnect <peer uuid>
   networksharing set <host|client> <on|off>
   networksharing set autoPairBehavior <manual|auto_user|auto_user_team>
   networksharing set displayname <new name>
   networksharing set pairRequestBehavior <ask|accept|reject>
   networksharing set peer <autoreconnect|allowhost|allowclient> <peer uuid> <on|off>
   networksharing settings
   networksharing startdiscovery
   overflow <speed in mbps>
   packetaggr <on|off>
   packetpool <small|default|large>
   ports [port/proto] ...
   priorityoverflow <speed in mbps>
   privacy advancedIspStats <on|off>
   privacy apiProtection <on|off>
   privacy requestToDisableDoH <on|off>
   refresh oauth [access token]
   route default <on|off>
   log <erase|daemon>
   log erase
   log daemon <file size> <files per daemon> <total files> <verbose|info|warn|error>
   show < servers | settings | privacy | adapters | currentserver | user | directory | connectmethod | streamingbypass | disconnect | streaming | speedtest | logsettings | dscp | fixeddelay | trafficrules >
   speedtest [adapter id]
   streamtest [adapter id]
   startupconnect <on|off>
   state
   stats [historic | [duration in seconds] [networksharing] [current|day|week|month|total|<period in hours>] ...]
   streaming domains <add|rem|set> <domain> ...
   streaming ipv4 <add|rem|set> <ip address> ...
   streaming ipv6 <add|rem|set> <ip address> ...
   streaming ports <add|rem|set> [port[-portRangeEnd]/proto] ...
   streamingbypass domains <add|rem|set> [<domain> ...]
   streamingbypass ipv4 <add|rem|set> <ip address> ...
   streamingbypass ipv6 <add|rem|set> <ip address> ...
   streamingbypass ports <add|rem|set> <port[-portRangeEnd]/proto> ...
   streamingbypass service <enable|disable|service name> [<on|off>]
   subnets [subnet/length] ...
   targetconnections <number upload connections> <number download connections>
   transport <auto|tcp|tcp-multi|udp|https>
   transportretry <time in seconds>
   version

```

# Commands



## activationcode
Obtain activation code to activate a device on my.speedify.come.
```text
$ speedify_cli activationcode 
{
        "activationCode" : "123456",
        "activationUrl" : "https://my.speedify.com/activate?activationCode=123456"
}
```

## adapter datalimit daily &lt;adapter id&gt; &lt;data usage in bytes|unlimited&gt;
The ```adapter datalimit daily``` limit the data usage for a specific adapter on a daily basis. The usage can be either limited in bytes or unlimited. This will set the maxDaily value accordingly. The adapter guid can be found by using the ```show adapters``` option.  Whether the adapter is disabled or rate limited is controlled by the ```adapter overlimitratelimit``` setting.
```text
$ speedify_cli adapter datalimit daily wlan0 0 
[
	{
		"adapterID" : "eth0",
		"connectedNetworkBSSID" : "",
		"connectedNetworkName" : "",
		"dataUsage" :
		{
			"overlimitRatelimit" : 5000000,
			"usageDaily" : 0,
			"usageDailyBoost" : 0,
			"usageDailyLimit" : 0,
			"usageMonthly" : 0,
			"usageMonthlyLimit" : 0,
			"usageMonthlyResetDay" : 0
		},
		"description" : "eth0",
		"directionalSettings" :
		{
			"download" : "on",
			"upload" : "on"
...
```

## adapter datalimit dailyboost &lt;adapter id&gt; &lt;additional bytes&gt;
Bumps up the daily datalimit for today only on a specific adapter on a daily basis.  The adapter guid can be found by using the ```show adapters``` option. 
```text
$ speedify_cli adapter datalimit dailyboost wlan0 0 
[
	{
		"adapterID" : "eth0",
		"connectedNetworkBSSID" : "",
		"connectedNetworkName" : "",
		"dataUsage" :
		{
			"overlimitRatelimit" : 5000000,
			"usageDaily" : 0,
			"usageDailyBoost" : 0,
			"usageDailyLimit" : 0,
			"usageMonthly" : 0,
			"usageMonthlyLimit" : 0,
			"usageMonthlyResetDay" : 0
		},
		"description" : "eth0",
		"directionalSettings" :
		{
			"download" : "on",
			"upload" : "on"
...
```

## adapter datalimit monthly &lt;adapter id&gt; &lt;data usage in bytes|unlimited&gt; &lt;day of the month to reset on|0 for last 30 days&gt;
The ```adapter datalimit monthly``` sets a monthly data cap that resets on a set date or lasts 30 days. The usage can be either limited in bytes or unlimited. This will set the max and resetDay accordingly. Whether the adapter is disabled or rate limited is controlled by the ```adapter overlimitratelimit``` setting.
```text
$ speedify_cli adapter datalimit monthly wlan0 2000000000 0 
[
	{
		"adapterID" : "eth0",
		"connectedNetworkBSSID" : "",
		"connectedNetworkName" : "",
		"dataUsage" :
		{
			"overlimitRatelimit" : 5000000,
			"usageDaily" : 52317,
			"usageDailyBoost" : 0,
			"usageDailyLimit" : 0,
			"usageMonthly" : 52317,
			"usageMonthlyLimit" : 0,
			"usageMonthlyResetDay" : 0
		},
		"description" : "eth0",
		"directionalSettings" :
		{
			"download" : "on",
			"upload" : "on"
...
```

## adapter directionalmode &lt;adapter id&gt; &lt;upload mode (on | backup_off | strict_off)&gt; &lt;download mode (on | backup_off | strict_off)&gt;
The ```adapter directionalmode``` controls if and how the adapter is used for upload and download, respectively. Valid settings are "on", "backup_off", and "strict_off".
```text
$ speedify_cli adapter directionalmode wlan0 on on 
[
	{
		"adapterID" : "eth0",
		"connectedNetworkBSSID" : "",
		"connectedNetworkName" : "",
		"dataUsage" :
		{
			"overlimitRatelimit" : 5000000,
			"usageDaily" : 52317,
			"usageDailyBoost" : 0,
			"usageDailyLimit" : 0,
			"usageMonthly" : 52317,
			"usageMonthlyLimit" : 0,
			"usageMonthlyResetDay" : 0
		},
		"description" : "eth0",
		"directionalSettings" :
		{
			"download" : "on",
			"upload" : "on"
...
```

## adapter encryption &lt;adapter id&gt; &lt;on|off&gt;
Controls encryption on a single adapter.  Note that using the ```encryption``` command will remove all per-adapter encryption settings.  Most of the time, you'll just want to use the ```encryption``` command that changes all adapters at same time. 
```text
$ speedify_cli adapter encryption wlan0 off 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : true,
	"fixedDelay" : 150,
	"forwardedPorts" : [],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 5,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
	"overflowThreshold" : 30.0,
	"packetAggregation" : true,
	"packetPoolSize" : "default",
	"perConnectionEncryptionEnabled" : true,
	"perConnectionEncryptionSettings" :
	[
...
```

## adapter expose-dscp &lt;adapter id&gt; &lt;on|off&gt;
The ```adapter expose-dscp``` allows dscp values of internal packets to be exposed to the VPN transport connection.
```text
$ speedify_cli adapter expose-dscp wlan0 off 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : true,
	"fixedDelay" : 150,
	"forwardedPorts" : [],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 5,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
	"overflowThreshold" : 30.0,
	"packetAggregation" : true,
	"packetPoolSize" : "default",
	"perConnectionEncryptionEnabled" : true,
	"perConnectionEncryptionSettings" :
	[
...
```

## adapter overlimitratelimit &lt;adapter id&gt; &lt;speed in bits per second|0 to stop using&gt;
When an ```adapter datalimit``` is hit, this rate limit (in bit per second) is applied to the adapter.  Set to 0 to disable the adapter.
```text
$ speedify_cli adapter overlimitratelimit wlan0 0 
[
	{
		"adapterID" : "eth0",
		"connectedNetworkBSSID" : "",
		"connectedNetworkName" : "",
		"dataUsage" :
		{
			"overlimitRatelimit" : 5000000,
			"usageDaily" : 52317,
			"usageDailyBoost" : 0,
			"usageDailyLimit" : 0,
			"usageMonthly" : 52317,
			"usageMonthlyLimit" : 0,
			"usageMonthlyResetDay" : 0
		},
		"description" : "eth0",
		"directionalSettings" :
		{
			"download" : "on",
			"upload" : "on"
...
```

## adapter priority &lt;adapter id&gt; &lt;automatic|always|secondary|backup|never&gt;
 The ```adapter priority``` command allows the user to choose which adapter gets one of the following priorities:

  | Priority | Description |
  | -------- | ----------- |
  | automatic | Let Speedify manage the connection's priority |
  | always | Use whenever connected |
  | secondary | Use less than Always connection- only when Always connections are congested or not working |
  | backup | Only use when other connections are unavailable |
  | never | Adapter is not used |

This will set priority as one of the above mentioned options accordingly.
```text
$ speedify_cli adapter priority wlan0 always 
[
	{
		"adapterID" : "eth0",
		"connectedNetworkBSSID" : "",
		"connectedNetworkName" : "",
		"dataUsage" :
		{
			"overlimitRatelimit" : 5000000,
			"usageDaily" : 52317,
			"usageDailyBoost" : 0,
			"usageDailyLimit" : 0,
			"usageMonthly" : 52317,
			"usageMonthlyLimit" : 0,
			"usageMonthlyResetDay" : 0
		},
		"description" : "eth0",
		"directionalSettings" :
		{
			"download" : "on",
			"upload" : "on"
...
```

## adapter ratelimit &lt;adapter id&gt; &lt;download speed in bits per second|unlimited&gt; &lt;upload speed in bits per second|unlimited&gt;
The ```adapter ratelimit``` command allows the user to throttle the adapter's maximum speed, in bits per second.
```text
$ speedify_cli adapter ratelimit wlan0 0 
[
	{
		"adapterID" : "eth0",
		"connectedNetworkBSSID" : "",
		"connectedNetworkName" : "",
		"dataUsage" :
		{
			"overlimitRatelimit" : 5000000,
			"usageDaily" : 52317,
			"usageDailyBoost" : 0,
			"usageDailyLimit" : 0,
			"usageMonthly" : 52317,
			"usageMonthlyLimit" : 0,
			"usageMonthlyResetDay" : 0
		},
		"description" : "eth0",
		"directionalSettings" :
		{
			"download" : "on",
			"upload" : "on"
...
```

## adapter resetusage &lt;adapter id&gt;
The ```adapter resetusage``` command resets the statistics associated with this adapter.  This restarts any daily and monthly data caps.
```text
$ speedify_cli adapter resetusage wlan0 
[
	{
		"adapterID" : "eth0",
		"connectedNetworkBSSID" : "",
		"connectedNetworkName" : "",
		"dataUsage" :
		{
			"overlimitRatelimit" : 5000000,
			"usageDaily" : 52317,
			"usageDailyBoost" : 0,
			"usageDailyLimit" : 0,
			"usageMonthly" : 52317,
			"usageMonthlyLimit" : 0,
			"usageMonthlyResetDay" : 0
		},
		"description" : "eth0",
		"directionalSettings" :
		{
			"download" : "on",
			"upload" : "on"
...
```

## captiveportal check
Checks whether an interfaces are currently being blocked by a captive portal.  Returns an array of adapterIDs which are currently captive. 
```text
$ speedify_cli  captiveportal check
["{D5306735-8BD9-4F89-A1AF-F485CA23208C}"]
```

## captiveportal login &lt;on|off&gt; &lt;adapter id&gt;
Starts or stops directing web traffic out the local interface to allow users to login to the captive portal web page.
Setting this to "on" and passing in an Adapter ID, will direct and new connections on ports 53,80 and 443 out the specified adapter.
If the Speedify user interface is running it will launch a captive portal web browser component.
Setting this to "off" (no Adapter ID required in this case), will stop the forwarding of the web traffic, and will allow it to all pass over the VPN tunnel as usal.
   
```text
$ speedify_cli  captiveportal login on "{D5306735-8BD9-4F89-A1AF-F485CA23208C}"
{
        "enabled":      true,
        "adapterID":    "{D5306735-8BD9-4F89-A1AF-F485CA23208C}"
}
```

## headercompression &lt;on|off&gt;
The ```headercompression``` command sets header compression on/off.
```text
$ speedify_cli headercompression on 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : true,
	"fixedDelay" : 150,
	"forwardedPorts" : [],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 5,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
	"overflowThreshold" : 30.0,
	"packetAggregation" : true,
	"packetPoolSize" : "default",
	"perConnectionEncryptionEnabled" : true,
	"perConnectionEncryptionSettings" :
	[
...
```

## connect [ closest | public | private | p2p | &lt;country&gt; [&lt;city&gt; [&lt;number&gt;]] | last | &lt;tag&gt; ]
The ```connect``` command connects to a server based on your ```connectmethod``` setting, or a server of your choosing.  It prints details of the server it has selected.

The ```show servers``` command will give you a detailed list of servers with their countries, cities and number as fields that you can use in this command.

Since 13.4 the ```connect``` command persistently stores the arguments so that the next time the daemon connects, it will connect with the same arguments.  Previously, you needed to use the ```connectmethod``` command to persistently store the setting, but this is no longer required.

It accepts both the "tag" style of server name, such as ```us-newark-18``` or accepts country, city and num as separate arguments, ```us newark 18```.

To connect to the nearest server in a particular country, pass along a two-letter country code drawn from the ```speedify_cli show servers``` command:
```text
  $ speedify_cli connect ca
```
To connect to a particular city, pass along a two-letter country code and city, drawn from the ```speedify_cli show servers``` command:
```text
  $ speedify_cli connect us atlanta
```
To connect to a specific server, pass along a tag which consists of a two-letter country code, city, and number, separated by hyphens.  These can be drawn from the ```speedify_cli show servers``` command.  By default, if Speedify cannot connect to the named server, it will attempt to connect to another server in the same city.  However, by adding a `#` at the front of the tag, it will lock it only connect to the specific named server (note that on some operating systems, such as Linux, you may need to use quotes around the argument):
```text
  $ speedify_cli connect "#us-atlanta-3"
```
Example:

```text
$ speedify_cli connect 
{
	"city" : "nova",
	"country" : "us",
	"dataCenter" : "soladrive-nova",
	"dnsIP" :
	[
		"10.202.8.8"
	],
	"friendlyName" : "United States - Northern Virginia #17",
	"isPremium" : false,
	"isPrivate" : true,
	"num" : 17,
	"publicIP" :
	[
		"64.20.8.8"
	],
	"tag" : "privateus-nova-17",
	"torrentAllowed" : true
}

```

## connectmethod &lt; closest | public | private | p2p | &lt;country&gt; [&lt;city&gt; [&lt;number&gt;]] | &lt;tag&gt; &gt;
The ```connectmethod``` command sets the connection method used during autoconnect, without actually connecting.  It prints the state immediately after the request to set the connection method is made.  The method used can be ```private```, ```p2p``` or ```closest```.  In order for this setting to be used, you may need to begin an autoconnect after changing the method, by running ```speedify_cli connect```.  
```text
$ speedify_cli connectmethod closest 
{
	"city" : "",
	"connectMethod" : "closest",
	"country" : "",
	"num" : 0
}

```

## connectretry &lt;time in seconds&gt;
The ```connect``` command connects to a server based on your ```connectmethod``` setting, or a server of your choosing.  It prints details of the server it has selected.

The ```show servers``` command will give you a detailed list of servers with their countries, cities and number as fields that you can use in this command.

Since 13.4 the ```connect``` command persistently stores the arguments so that the next time the daemon connects, it will connect with the same arguments.  Previously, you needed to use the ```connectmethod``` command to persistently store the setting, but this is no longer required.

It accepts both the "tag" style of server name, such as ```us-newark-18``` or accepts country, city and num as separate arguments, ```us newark 18```.

To connect to the nearest server in a particular country, pass along a two-letter country code drawn from the ```speedify_cli show servers``` command:
```text
  $ speedify_cli connect ca
```
To connect to a particular city, pass along a two-letter country code and city, drawn from the ```speedify_cli show servers``` command:
```text
  $ speedify_cli connect us atlanta
```
To connect to a specific server, pass along a tag which consists of a two-letter country code, city, and number, separated by hyphens.  These can be drawn from the ```speedify_cli show servers``` command.  By default, if Speedify cannot connect to the named server, it will attempt to connect to another server in the same city.  However, by adding a `#` at the front of the tag, it will lock it only connect to the specific named server (note that on some operating systems, such as Linux, you may need to use quotes around the argument):
```text
  $ speedify_cli connect "#us-atlanta-3"
```
Example:

```text
$ speedify_cli connect 
{
	"city" : "nova",
	"country" : "us",
	"dataCenter" : "soladrive-nova",
	"dnsIP" :
	[
		"10.202.8.8"
	],
	"friendlyName" : "United States - Northern Virginia #17",
	"isPremium" : false,
	"isPrivate" : true,
	"num" : 17,
	"publicIP" :
	[
		"64.20.8.8"
	],
	"tag" : "privateus-nova-17",
	"torrentAllowed" : true
}

```

## daemon exit
Causes the Speedify service to disconnect, and exit.  In general, leave this alone. 

## directory [directory server domain]
Controls the directory server.  In general, leave this alone.    

## dns &lt;ip address&gt; ...
The ```dns``` command sets the DNS servers to use for domain name resolution.
```text
$ speedify_cli dns 8.8.8.8 
{
	"advancedIspStats" : true,
	"apiProtection" : true,
	"dnsAddresses" :
	[
		"8.8.8.8"
	],
	"requestToDisableDoH" : false
}

```

## disconnect
The ```disconnect``` command disconnects from the server.  It prints the state immediately after the request to disconnect is made.
```text
$ speedify_cli disconnect 
{
	"state" : "LOGGED_IN"
}

```

## dscp queues &lt;add|rem|set&gt; ...
Configure how dscp queues are handled.
```text
$ speedify_cli dscp queues add 0 priority on replication auto retransmissions 2 
{
	"dscpQueues" :
	[
		{
			"dscp" : 0,
			"priority" : "on",
			"replication" : "auto",
			"retransmissionAttempts" : 2
		}
	]
}

```

## dscp queues add [&lt;dscp value 0-63&gt; [priority] &lt;on|off|auto&gt; [replication] &lt;on|off|auto&gt; [retransmissions] &lt;0-255&gt;] ...
Configure how dscp queues are handled.
```text
$ speedify_cli dscp queues add 0 priority on replication auto retransmissions 2 
{
	"dscpQueues" :
	[
		{
			"dscp" : 0,
			"priority" : "on",
			"replication" : "auto",
			"retransmissionAttempts" : 2
		}
	]
}

```

## dscp queues set [&lt;dscp value 0-63&gt; [priority] &lt;on|off|auto&gt; [replication] &lt;on|off|auto&gt; [retransmissions] &lt;0-255&gt;] ...
Configure how dscp queues are handled.
```text
$ speedify_cli dscp queues add 0 priority on replication auto retransmissions 2 
{
	"dscpQueues" :
	[
		{
			"dscp" : 0,
			"priority" : "on",
			"replication" : "auto",
			"retransmissionAttempts" : 2
		}
	]
}

```

## dscp queues rem [dscp value 0-63] ...
Configure how dscp queues are handled.
```text
$ speedify_cli dscp queues add 0 priority on replication auto retransmissions 2 
{
	"dscpQueues" :
	[
		{
			"dscp" : 0,
			"priority" : "on",
			"replication" : "auto",
			"retransmissionAttempts" : 2
		}
	]
}

```

## encryption &lt;on|off&gt;
The ```encryption``` command enables or disables encryption of all tunneled traffic.  It prints the connection settings immediately after the change is made.  Note that this will clear all per-adapter encryption settings from the ```adapter encryption``` command.
```text
$ speedify_cli encryption off 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 150,
	"forwardedPorts" : [],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 5,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
	"overflowThreshold" : 30.0,
	"packetAggregation" : true,
	"packetPoolSize" : "default",
	"perConnectionEncryptionEnabled" : false,
	"perConnectionEncryptionSettings" : [],
	"perConnectionExposeDscpSettings" :
...
```

## fixeddelay &lt;domains|ips|ports|delay in ms&gt;

The ```fixeddelay``` command specifies a delay in milliseconds for a jitter buffer. The jitter buffer adds a delay to traffic and delivers it with a consistent latency through the VPN tunnel to minimize jitter. The delay is applied in each direction on top of the baseline latency, so the effective round trip time is twice the fixeddelay value plus the underlying connection latency. Rules can be defined by ports, IP addresses and domains. The rules specify which traffic should have the delay applied while other traffic is delivered normally. This feature can be helpful with live streaming and other applications which are sensitive to changes in latency, but can handle extra delay. The jitter buffer should not be used for real-time back and forth communication, such as audio / video calls or gaming where extra delay can degrade the experience.

Valid delay range: 0–1000 ms.

```text
$ speedify_cli fixeddelay 100 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" : [],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 5,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
	"overflowThreshold" : 30.0,
	"packetAggregation" : true,
	"packetPoolSize" : "default",
	"perConnectionEncryptionEnabled" : false,
	"perConnectionEncryptionSettings" : [],
	"perConnectionExposeDscpSettings" :
...
```

## fixeddelay domains &lt;add|rem|set&gt; &lt;domain&gt; ...

The ```fixeddelay``` command specifies a delay in milliseconds for a jitter buffer. The jitter buffer adds a delay to traffic and delivers it with a consistent latency through the VPN tunnel to minimize jitter. The delay is applied in each direction on top of the baseline latency, so the effective round trip time is twice the fixeddelay value plus the underlying connection latency. Rules can be defined by ports, IP addresses and domains. The rules specify which traffic should have the delay applied while other traffic is delivered normally. This feature can be helpful with live streaming and other applications which are sensitive to changes in latency, but can handle extra delay. The jitter buffer should not be used for real-time back and forth communication, such as audio / video calls or gaming where extra delay can degrade the experience.

```text
$ speedify_cli fixeddelay 100 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" : [],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 5,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
	"overflowThreshold" : 30.0,
	"packetAggregation" : true,
	"packetPoolSize" : "default",
	"perConnectionEncryptionEnabled" : false,
	"perConnectionEncryptionSettings" : [],
	"perConnectionExposeDscpSettings" :
...
```

## fixeddelay ips &lt;add|rem|set&gt; &lt;ip address&gt; ...

The ```fixeddelay``` command specifies a delay in milliseconds for a jitter buffer. The jitter buffer adds a delay to traffic and delivers it with a consistent latency through the VPN tunnel to minimize jitter. The delay is applied in each direction on top of the baseline latency, so the effective round trip time is twice the fixeddelay value plus the underlying connection latency. Rules can be defined by ports, IP addresses and domains. The rules specify which traffic should have the delay applied while other traffic is delivered normally. This feature can be helpful with live streaming and other applications which are sensitive to changes in latency, but can handle extra delay. The jitter buffer should not be used for real-time back and forth communication, such as audio / video calls or gaming where extra delay can degrade the experience.

```text
$ speedify_cli fixeddelay 100 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" : [],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 5,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
	"overflowThreshold" : 30.0,
	"packetAggregation" : true,
	"packetPoolSize" : "default",
	"perConnectionEncryptionEnabled" : false,
	"perConnectionEncryptionSettings" : [],
	"perConnectionExposeDscpSettings" :
...
```

## fixeddelay ports &lt;add|rem|set&gt; [port[-portRangeEnd]/proto] ...

The ```fixeddelay``` command specifies a delay in milliseconds for a jitter buffer. The jitter buffer adds a delay to traffic and delivers it with a consistent latency through the VPN tunnel to minimize jitter. The delay is applied in each direction on top of the baseline latency, so the effective round trip time is twice the fixeddelay value plus the underlying connection latency. Rules can be defined by ports, IP addresses and domains. The rules specify which traffic should have the delay applied while other traffic is delivered normally. This feature can be helpful with live streaming and other applications which are sensitive to changes in latency, but can handle extra delay. The jitter buffer should not be used for real-time back and forth communication, such as audio / video calls or gaming where extra delay can degrade the experience.

```text
$ speedify_cli fixeddelay 100 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" : [],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 5,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
	"overflowThreshold" : 30.0,
	"packetAggregation" : true,
	"packetPoolSize" : "default",
	"perConnectionEncryptionEnabled" : false,
	"perConnectionEncryptionSettings" : [],
	"perConnectionExposeDscpSettings" :
...
```

## gateway [directory gateway uri]
Configures the OAuth gateway url to use.
```text
$ speedify_cli gateway https://my.domain.com/oauth/gateway/path 
{
	"domain" : "",
	"enableEsni" : false,
	"gatewayUri" : "https://my.domain.com/oauth/gateway/path"
}

```

## jumbo &lt;on|off&gt;
The ```jumbo``` command allows the TUN adapter to accept larger MTU packets. This will set ```jumbo_packets``` to either ```True``` or ```False```.
```text
$ speedify_cli jumbo on 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" : [],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 5,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
	"overflowThreshold" : 30.0,
	"packetAggregation" : true,
	"packetPoolSize" : "default",
	"perConnectionEncryptionEnabled" : false,
	"perConnectionEncryptionSettings" : [],
	"perConnectionExposeDscpSettings" :
...
```

## login &lt;username&gt; [password]
The ```login``` command instructs Speedify to connect with the given username and password.  It prints the state immediately after the request to login is made.  Speedify will then proceed to automatically connect if the login succeeds.
```text
$ speedify_cli  login user@domain.com password123
{
        "state":        "LOGGED_IN"
}
```

## login auto
The ```login auto``` command instructs Speedify to connect to a free account with a set data limit. It prints the following state immediately after the request is made.
```text
$ speedify_cli  login auto
{
        "state":        "LOGGED_IN"
}
```

## login oauth [access token]
The ```login oauth``` logs in with the user represented by encrypted token passed in.  It prints the state immediately after the request to login is made.  Speedify will then proceed to automatically connect if the login succeeds.
```text
$ speedify_cli  login oauth {encrypted_token}
{
        "state":        "LOGGED_IN"
}
```

## logout
The ```logout``` command disconnects from the server and flushes any user credentials that were stored.
```text
$ speedify_cli  logout
{
        "state":        "LOGGED_OUT"
}
```

## maxredundant &lt;number of conns&gt;
The ```maxredundant``` command controls the maximum number of connections will be use simultaneously in redundant mode.
```text
$ speedify_cli maxredundant 3 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" : [],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 3,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
	"overflowThreshold" : 30.0,
	"packetAggregation" : true,
	"packetPoolSize" : "default",
	"perConnectionEncryptionEnabled" : false,
	"perConnectionEncryptionSettings" : [],
	"perConnectionExposeDscpSettings" :
...
```

## mode &lt;redundant|speed|streaming&gt;
The ```mode``` command instructs Speedify to optimize for maximum connection speed or redundancy.  Valid options are ```speed```, ```redundant```, and ```streaming```.
```text
$ speedify_cli mode speed 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" : [],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 3,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
	"overflowThreshold" : 30.0,
	"packetAggregation" : true,
	"packetPoolSize" : "default",
	"perConnectionEncryptionEnabled" : false,
	"perConnectionEncryptionSettings" : [],
	"perConnectionExposeDscpSettings" :
...
```

## networksharing set alwaysOnDiscovery &lt;on|off&gt;
Controls if Pair and Share peer discovery is always active. This can use more power when on battery.
```text
$ speedify_cli networksharing set alwaysOnDiscovery on
{
    "alwaysOnDiscovery" : true,
    "autoPairBehavior" : "auto_user_team",
    "clientEnabled" : true,
    "displayName" : "peer device",
    "hostConnectCode" : "",
    "hostEnabled" : false,
    "pairRequestBehavior" : "accept"
}
```

## networksharing availableshares
The `networksharing` commands control the Pair & Share behavior of this device, allowing it to share cellular connections over a Wi-Fi network to act as virtual network adapters. 
        `availableshares` returns an array of all currently available networksharing peers that were found via discovery, and what is known about them.
```text
$ speedify_cli networksharing availableshares
[
  {
    "autoReconnect" : true,
    "displayName" : "peer device",
    "haveAuthToken" : false,
    "peerAsClient" :
    {
      "allowed" : true,
      "peerStatus" : "disconnected",
      "tunnelStatus" : "inactive",
      "usage" :
      {
        "month" : 0,
        "today" : 0,
        "total" : 0,
        "week" : 0
      }
    },
    "peerAsHost" :
    {
      "allowed" : true,
      "peerStatus" : "unauthenticated",
      "tunnelStatus" : "inactive",
      "usage" :
      {
        "month" : 0,
        "today" : 0,
        "total" : 0,
        "week" : 0
      }
    },
    "supportsHost" : true,
    "uuid" : "F1C1290C-CA03-17B4-9989-A22222A28B74"
  }
]
```

## networksharing connect &lt;peer connect code&gt;
Connect to a peer, using a connect code (`hostConnectCode`), if that peer is available on the local network.
        Connect codes normally come from scanning the peer's QR code.  You probable actually want to use `networksharing peer request <uuid>` if you are trying to connect to peer you found in `availableshares`.
        
```text
$ speedify_cli networksharing connect F1C1290C-CA03-17B4-9989-A22222A28B74
{
    "peerStatus" : "authenticated",
    "role" : "host",
    "uuid" : "F1C1290C-CA03-17B4-9989-A22222A28B74"
}
```

## networksharing discovery
Shows the current state of Pair & Share discovery.
```text
$ speedify_cli networksharing discovery 
{
    "discoveryActive" : false
}
```

## networksharing peer &lt;allow|reject|request|unpair&gt; &lt;peer uuid&gt;
Controls pairing behavior with the peer with the given `uuid`.  The `uuid` can be found with `networksharing availableshares`.
        The options are:
  * `allow` - accepts a request to pair from this peer
  * `reject` - refuses a request to pair from this peer
  * `request` - sends a request to pair to this peer
  * `unpair` - disconnects and unpairs from this peer.  You will need to `request` / `allow` again before using this peer again.

  
  
```text
$ speedify_cli allow F1C1290C-CA03-17B4-9989-A22222A28B74 on
{
  "displayName" : "peer device",
  "haveAuthToken" : true,
  "uuid" : "F1C1290C-CA03-17B4-9989-A22222A28B74"
}
```

## networksharing reconnect &lt;peer uuid&gt;
Reconnect to the peer at <uuid>.
```text
$ speedify_cli networksharing reconnect F1C1290C-CA03-17B4-9989-A22222A28B74
{
  "peerStatus" : "authenticated",
  "role" : "host",
  "uuid" : "F1C1290C-CA03-17B4-9989-A22222A28B74"
}
```

## networksharing set &lt;host|client&gt; &lt;on|off&gt;
Controls if device acts as a `client` (using peers' shared cellular) or a `host` (allowing peers to use our cellular).  Currently only mobile platforms can act as hosts.
```text
$ speedify_cli networksharing set client on 
{
	"alwaysOnDiscovery" : true,
	"autoPairBehavior" : "auto_user_team",
	"clientEnabled" : true,
	"displayName" : "andorra",
	"hostConnectCode" : "",
	"hostEnabled" : false,
	"pairRequestBehavior" : "ask",
	"sameUserAutoPair" : true
}

```

## networksharing set autoPairBehavior &lt;manual|auto_user|auto_user_team&gt;
Controls if peers of the same user and/or team are automatically paired.
```text
$ speedify_cli networksharing set autoPairBehavior auto_user_team
{
    "alwaysOnDiscovery" : true,
    "autoPairBehavior" : "auto_user_team",
    "clientEnabled" : true,
    "displayName" : "peer device",
    "hostConnectCode" : "",
    "hostEnabled" : false,
    "pairRequestBehavior" : "accept"
}
```

## networksharing set displayname &lt;new name&gt;
A valid utf-8 display name. Other devices will see this name when they pair/share with this device.  Name is for display only, settings and connections are based on the automatically generated `uuid`.
```text
$ speedify_cli networksharing set displayname peer device 
{
	"alwaysOnDiscovery" : true,
	"autoPairBehavior" : "auto_user_team",
	"clientEnabled" : true,
	"displayName" : "peer device",
	"hostConnectCode" : "",
	"hostEnabled" : false,
	"pairRequestBehavior" : "ask",
	"sameUserAutoPair" : true
}

```

## networksharing set pairRequestBehavior &lt;ask|accept|reject&gt;
Set the behavior for incoming connection requests; ask, accept, or reject.
```text
$ speedify_cli networksharing set client on 
{
	"alwaysOnDiscovery" : true,
	"autoPairBehavior" : "auto_user_team",
	"clientEnabled" : true,
	"displayName" : "peer device",
	"hostConnectCode" : "",
	"hostEnabled" : false,
	"pairRequestBehavior" : "ask",
	"sameUserAutoPair" : true
}

```

## networksharing set peer &lt;autoreconnect|allowhost|allowclient&gt; &lt;peer uuid&gt; &lt;on|off&gt;
Turns on and off settings related to an individual peer, identified by `uuid`. 
dir

  * `autoconnect` controls whether to automatically reconnect to this peer when it is available.
  * `allowhost` controls whether to allow peer to act as a host (e.g. will we use its offered cellular connections).
  * `allowclient` controls whether to allow peer to use any cellular adapters this computer is sharing as a host.

        
```text
$ speedify_cli networksharing set peer autoreconnect F1C1290C-CA03-17B4-9989-A22222A28B74 on
[
    {
        "autoReconnect" : true,
        "displayName" : "peer device",
        "haveAuthToken" : true,
        "peerAsClient" :
        {
            "allowed" : true,
            "peerStatus" : "unauthenticated",
            "tunnelStatus" : "inactive",
            "usage" :
            {
                "month" : 0,
                "today" : 0,
                "total" : 0,
                "week" : 0
            }
        },
        "peerAsHost" :
        {
            "allowed" : true,
            "peerStatus" : "authenticated",
            "tunnelStatus" : "active",
            "usage" :
            {
                "month" : 0,
                "today" : 0,
                "total" : 0,
                "week" : 0
            }
        },
        "supportsHost" : true,
        "uuid" : "F1C1290C-CA03-17B4-9989-A22222A28B74"
    }
]
```

## networksharing settings
Shows the current Pair & Share settings.
        
        
        
```text
$ speedify_cli networksharing settings
{
    "alwaysOnDiscovery" : true,
    "autoPairBehavior" : "auto_user_team",
    "clientEnabled" : true,
    "displayName" : "peer device",
    "hostConnectCode" : "",
    "hostEnabled" : false,
    "pairRequestBehavior" : "accept"
}
```

## networksharing startdiscovery
Begin discovering other devices on the local network.
```text
$ speedify_cli networksharing startdiscovery 
{
	"discoveryActive" : true
}

```

## overflow &lt;speed in mbps&gt;
Speed in Mbps after which ```Secondary``` connections are not used.
```text
$ speedify_cli overflow 10.0 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" : [],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 3,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
	"overflowThreshold" : 10.0,
	"packetAggregation" : true,
	"packetPoolSize" : "default",
	"perConnectionEncryptionEnabled" : false,
	"perConnectionEncryptionSettings" : [],
	"perConnectionExposeDscpSettings" :
...
```

## packetaggr &lt;on|off&gt;
The ```packetaggr``` command sets packet aggregation on/off.
```text
$ speedify_cli packetaggr on 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" : [],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 3,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
	"overflowThreshold" : 10.0,
	"packetAggregation" : true,
	"packetPoolSize" : "default",
	"perConnectionEncryptionEnabled" : false,
	"perConnectionEncryptionSettings" : [],
	"perConnectionExposeDscpSettings" :
...
```

## packetpool &lt;small|default|large&gt;
The ```packetpool``` command controls the size of the packet pool. A larger pool can provide better performance, but may use more memory.
```text
$ speedify_cli packetpool default 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" : [],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 3,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
	"overflowThreshold" : 10.0,
	"packetAggregation" : true,
	"packetPoolSize" : "default",
	"perConnectionEncryptionEnabled" : false,
	"perConnectionEncryptionSettings" : [],
	"perConnectionExposeDscpSettings" :
...
```

## ports [port/proto] ...
The ```ports``` command instructs Speedify to request public ports from a Dedicated (private) Speed Server. These settings only go into effect after a reconnect, and they are ignored by public Speed Servers.  Requesting a port that is already taken by another user will lead to the connect request failing, and state will return to LOGGED_IN. Calling the ```ports``` command with no additional parameters will clear the port forward requests.
```text
$ speedify_cli ports 8001/tcp 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" :
	[
		{
			"port" : 8001,
			"protocol" : "tcp"
		}
	],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 3,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
...
```

## priorityoverflow &lt;speed in mbps&gt;
Speed in Mbps after which ```Secondary``` connections are not used for priority traffic.
```text
$ speedify_cli priorityoverflow 10.0 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" :
	[
		{
			"port" : 8001,
			"protocol" : "tcp"
		}
	],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 3,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
...
```

## privacy advancedIspStats &lt;on|off&gt;
Enables or disables advanced ISP statistics. When enabled, extra stats are available from some ISPs, such as Starlink.
```text
$ speedify_cli privacy advancedIspStats on 
{
	"advancedIspStats" : true,
	"apiProtection" : true,
	"dnsAddresses" :
	[
		"8.8.8.8"
	],
	"requestToDisableDoH" : false
}

```

## privacy apiProtection &lt;on|off&gt;
Enables or disables protection on the Speedify API port. When disabled, speedify_cli can be used to control a remote Speedify instalation.
```text
$ speedify_cli privacy apiProtection on 
{
	"advancedIspStats" : true,
	"apiProtection" : true,
	"dnsAddresses" :
	[
		"8.8.8.8"
	],
	"requestToDisableDoH" : false
}

```

## privacy requestToDisableDoH &lt;on|off&gt;
If the Speedify VPN connection should request that browsers disable DNS over HTTPS. Enabling this can help streaming and streamingbypass rules function.
```text
$ speedify_cli privacy requestToDisableDoH on 
{
	"advancedIspStats" : true,
	"apiProtection" : true,
	"dnsAddresses" :
	[
		"8.8.8.8"
	],
	"requestToDisableDoH" : false
}

```

## refresh oauth [access token]
Accepts a new security token for the same user to be used when communicating with servers.  If changing users, use ```login oauth``` instead.
```text
$ speedify_cli refresh oauth abdef1234567890
```

## route default &lt;on|off&gt;
Configures whether Speedify will obtain a 'default' route to the Internet over the VPN adapter.
```text
$ speedify_cli route default on 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" :
	[
		{
			"port" : 8001,
			"protocol" : "tcp"
		}
	],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 3,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
...
```


## log erase
Deletes the Speedify daemon's log files.
```text
$ speedify_cli log erase 

```

## log daemon &lt;file size&gt; &lt;files per daemon&gt; &lt;total files&gt; &lt;verbose|info|warn|error&gt;
The ```log daemon``` configures the size and number of the Speedify daemon's log files.
```text
$ speedify_cli log daemon 3145728 7 9 info 
{
	"daemon" :
	{
		"fileSize" : 3145728,
		"filesPerDaemon" : 7,
		"logLevel" : 1,
		"totalFiles" : 9
	}
}

```

## show servers
The ```show servers``` command retrieves the current list of Speed Servers. If you have access to any Dedicated Speed Servers, they appear in a ```private``` array.  The public pool of Speed Servers appear in a ```public``` array.
```text
$ speedify_cli show servers 
{
	"private" :
	[
		{
			"city" : "la",
			"country" : "us",
			"dataCenter" : "oneprovider-la",
			"friendlyName" : "United States - Los Angeles #43",
			"isPremium" : false,
			"isPrivate" : true,
			"num" : 43,
			"tag" : "privateus-la-43",
			"torrentAllowed" : false
		},
		{
			"city" : "sydney",
			"country" : "au",
			"dataCenter" : "linode-sydney",
			"friendlyName" : "Australia - Sydney #35",
			"isPremium" : false,
...
```

## show settings
The ```show settings``` command retrieves the current connection settings. These settings are sent to the server at connect time, and they can be retrieved at any time.
```text
$ speedify_cli show settings 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" :
	[
		{
			"port" : 8001,
			"protocol" : "tcp"
		}
	],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 3,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
...
```

## show privacy
Outputs privacy related settings
```text
$ speedify_cli show privacy 
{
	"advancedIspStats" : true,
	"apiProtection" : true,
	"dnsAddresses" :
	[
		"8.8.8.8"
	],
	"requestToDisableDoH" : false
}

```

## show adapters
The ```show adapters``` command allows the user to view all of the network adapters, and their settings and statistics.
```text
$ speedify_cli show adapters 
[
	{
		"adapterID" : "eth0",
		"connectedNetworkBSSID" : "",
		"connectedNetworkName" : "",
		"dataUsage" :
		{
			"overlimitRatelimit" : 5000000,
			"usageDaily" : 86584,
			"usageDailyBoost" : 0,
			"usageDailyLimit" : 0,
			"usageMonthly" : 86584,
			"usageMonthlyLimit" : 0,
			"usageMonthlyResetDay" : 0
		},
		"description" : "eth0",
		"directionalSettings" :
		{
			"download" : "on",
			"upload" : "on"
...
```

## show currentserver
The ```show currentserver``` command displays the last server Speedify was connected (which, if you are connected is the current server). 
```text
$ speedify_cli show currentserver 
{
	"city" : "nova",
	"country" : "us",
	"dataCenter" : "soladrive-nova",
	"dnsIP" :
	[
		"10.202.8.8"
	],
	"friendlyName" : "United States - Northern Virginia #17",
	"isPremium" : false,
	"isPrivate" : true,
	"num" : 17,
	"publicIP" :
	[
		"64.20.8.8"
	],
	"tag" : "privateus-nova-17",
	"torrentAllowed" : true
}

```

## show user
Outputs information about the currently logged in user.
```text
$ speedify_cli show user 
{
	"action" : "none",
	"bytesAvailable" : -1,
	"bytesUsed" : 89623508283,
	"dataPeriodEnd" : "2025-09-01",
	"email" : "****@connectify.me",
	"isAutoAccount" : false,
	"isTeam" : true,
	"minutesAvailable" : -1,
	"minutesUsed" : 1814927,
	"paymentType" : "yearly"
}

```

## show directory
The ```show directory``` command shows the current directory server. 
```text
$ speedify_cli show directory 
{
	"domain" : "",
	"enableEsni" : false,
	"gatewayUri" : ""
}

```

## show connectmethod
The ```show connectmethod``` command displays the stored connectmethod (the default settings for ```connect```).
```text
$ speedify_cli show connectmethod 
{
	"city" : "",
	"connectMethod" : "closest",
	"country" : "",
	"num" : 0
}

```

## show streamingbypass
The ```show streamingbypass``` command displays current streaming bypass service settings.
```text
$ speedify_cli show streamingbypass 
{
	"domainWatchlistEnabled" : true,
	"domains" : [],
	"ipv4" : [],
	"ipv6" : [],
	"ports" : [],
	"services" :
	[
		{
			"enabled" : true,
			"title" : "Netflix"
		},
		{
			"enabled" : true,
			"title" : "HBO"
		},
		{
			"enabled" : true,
			"title" : "Hulu"
		},
...
```

## show disconnect
Displays the reason for the last disconnect.
```text
$ speedify_cli show disconnect 
{
	"disconnectReason" : "USERINITIATED"
}

```

## show streaming
The ```show streaming``` command displays current streaming mode settings.
```text
$ speedify_cli show streaming 
{
	"domains" : [],
	"ipv4" : [],
	"ipv6" : [],
	"ports" : []
}

```

## show speedtest
The ```show speedtest``` command displays the last speed test results.
```text
$ speedify_cli show speedtest 
[]

```

## show logsettings
The ```show dscp``` command retrieves the current log settings.
```text
$ speedify_cli show logsettings 
{
	"daemon" :
	{
		"fileSize" : 3145728,
		"filesPerDaemon" : 7,
		"logLevel" : 1,
		"totalFiles" : 9
	}
}

```

## show dscp
The ```show dscp``` command retrieves the current dscp settings.
```text
$ speedify_cli show dscp 
{
	"dscpQueues" :
	[
		{
			"dscp" : 0,
			"priority" : "on",
			"replication" : "auto",
			"retransmissionAttempts" : 2
		}
	]
}

```

## show fixeddelay
Shows the current rules for including traffic in the jitter buffer. Rules for domains, ports, and IP addresses are supported.
```text
$ speedify_cli show fixeddelay 
{
	"trafficRules" :
	[
		{
			"actions" :
			[
				{
					"type" : "fixed_delay"
				}
			],
			"conditions" :
			[
				{
					"type" : "ports",
					"value" :
					[
						{
							"port" : 9000,
							"portRangeEnd" : 9010,
							"proto" : "udp"
...
```

## show trafficrules
Shows the current traffic rules setting.
```text
$ speedify_cli show trafficrules 
{
	"trafficRules" :
	[
		{
			"actions" :
			[
				{
					"type" : "fixed_delay"
				}
			],
			"conditions" :
			[
				{
					"type" : "ports",
					"value" :
					[
						{
							"port" : 9000,
							"portRangeEnd" : 9010,
							"proto" : "udp"
...
```

## speedtest [adapter id]
Runs a speed test over the VPN tunnel, using a bundled iPerf3 client.
```text
$ speedify_cli speedtest 
[
	{
		"city" : "",
		"country" : "",
		"errorMessage" : "Cannot test speed while disconnected",
		"isError" : true,
		"latency" : 0,
		"numConnections" : 0,
		"time" : 1754508166,
		"type" : "speed"
	}
]

```

## streamtest [adapter id]
Runs a stream test over the VPN tunnel, using a bundled iPerf3 client.  The streamtest is emulating broadcating a live stream; it sends 60 Mbps of UDP traffic and measures the results.
```text
$ speedify_cli streamtest 
[
	{
		"city" : "",
		"country" : "",
		"errorMessage" : "Cannot test speed while disconnected",
		"isError" : true,
		"latency" : 0,
		"numConnections" : 0,
		"time" : 1754508166,
		"type" : "streaming"
	}
]

```

## startupconnect &lt;on|off&gt;
The ```startupconnect``` option tells Speedify if it should connect automatically at startup or not.  It prints the current settings immediately after the request is made.
```text
$ speedify_cli startupconnect on 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" : [],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" :
	[
		{
			"port" : 8001,
			"protocol" : "tcp"
		}
	],
	"headerCompression" : true,
	"jumboPackets" : true,
	"maxRedundant" : 3,
	"maximumConnectRetry" : 0,
	"maximumTransportRetry" : 0,
...
```

## state
The ```state``` command retrieves the current state of the connection.  Possible states are ```LOGGED_OUT```, ```LOGGING_IN```, ```LOGGED_IN```, ```AUTO_CONNECTING```, ```CONNECTING```, ```DISCONNECTING```, ```CONNECTED```, ```OVERLIMIT```, and ```UNKNOWN```
```text
$ speedify_cli state 
{
	"state" : "CONNECTING"
}

```

## stats [historic | [duration in seconds] [networksharing] [current|day|week|month|total|&lt;period in hours&gt;] ...]
The ```stats``` command subscribes to a feed of connection and session statistics.  By default, this feed will continue until the speedify_cli process is terminated, but an optional parameter can be given to stop and exit after the given number of seconds.  This can be useful to monitor how many connections are being utilized by Speedify, and what their current network activity level is in bytes per second. You can specify up to 5 time periods to receive stats over.
```text
$ speedify_cli stats 1 
[
	"state",
	{
		"state" : "CONNECTING"
	}
]

[
	"connection_stats",
	{
		"connections" :
		[
			{
				"adapterID" : "eth0",
				"congested" : false,
				"connected" : true,
				"connectionID" : "eth0%10.1.0.0/24",
				"downloadCongested" : false,
				"inFlight" : 802,
				"inFlightWindow" : 60000,
...
```

## streaming domains &lt;add|rem|set&gt; &lt;domain&gt; ...
Configure extra domains to be treated as high priority streams when in streaming mode.
```text
$ speedify_cli streaming domains add mynewstreamingservice.com 
{
	"domains" :
	[
		"mynewstreamingservice.com"
	],
	"ipv4" : [],
	"ipv6" : [],
	"ports" : []
}

```

## streaming ipv4 &lt;add|rem|set&gt; &lt;ip address&gt; ...
Configure extra IPv4 addresses to be treated as high priority streams when in streaming mode.
```text
$ speedify_cli streaming ipv4 add 8.8.8.8 
{
	"domains" :
	[
		"mynewstreamingservice.com"
	],
	"ipv4" :
	[
		"8.8.8.8"
	],
	"ipv6" : [],
	"ports" : []
}

```

## streaming ipv6 &lt;add|rem|set&gt; &lt;ip address&gt; ...
Configure extra IPv6 addresses to be treated as high priority streams when in streaming mode.
```text
$ speedify_cli streaming ipv6 add 2001:4860:4860::8888 
{
	"domains" :
	[
		"mynewstreamingservice.com"
	],
	"ipv4" :
	[
		"8.8.8.8"
	],
	"ipv6" :
	[
		"2001:4860:4860::8888"
	],
	"ports" : []
}

```

## streaming ports &lt;add|rem|set&gt; [port[-portRangeEnd]/proto] ...
Configure extra ports to be treated as high priority streams when in streaming mode.
```text
$ speedify_cli streaming ports add 8200/tcp 
{
	"domains" :
	[
		"mynewstreamingservice.com"
	],
	"ipv4" :
	[
		"8.8.8.8"
	],
	"ipv6" :
	[
		"2001:4860:4860::8888"
	],
	"ports" :
	[
		{
			"port" : 8200,
			"protocol" : "tcp"
		}
	]
...
```

## streamingbypass domains &lt;add|rem|set&gt; [&lt;domain&gt; ...]
Configure extra domains to bypass the VPN.
```text
$ speedify_cli streamingbypass domains add hulu.com 
{
	"domainWatchlistEnabled" : true,
	"domains" :
	[
		"hulu.com"
	],
	"ipv4" : [],
	"ipv6" : [],
	"ports" : [],
	"services" :
	[
		{
			"enabled" : true,
			"title" : "Netflix"
		},
		{
			"enabled" : true,
			"title" : "HBO"
		},
		{
...
```

## streamingbypass ipv4 &lt;add|rem|set&gt; &lt;ip address&gt; ...
Configure extra IPv4 addresses to bypass the VPN.
```text
$ speedify_cli streamingbypass ipv4 add 8.8.8.8 
{
	"domainWatchlistEnabled" : true,
	"domains" :
	[
		"hulu.com"
	],
	"ipv4" :
	[
		"8.8.8.8"
	],
	"ipv6" : [],
	"ports" : [],
	"services" :
	[
		{
			"enabled" : true,
			"title" : "Netflix"
		},
		{
			"enabled" : true,
...
```

## streamingbypass ipv6 &lt;add|rem|set&gt; &lt;ip address&gt; ...
Configure extra IPv6 addresses to bypass the VPN.
```text
$ speedify_cli streamingbypass ipv4 add 2001:4860:4860::8888 
{
	"domainWatchlistEnabled" : true,
	"domains" :
	[
		"hulu.com"
	],
	"ipv4" :
	[
		"8.8.8.8",
		"170.170.8.8"
	],
	"ipv6" : [],
	"ports" : [],
	"services" :
	[
		{
			"enabled" : true,
			"title" : "Netflix"
		},
		{
...
```

## streamingbypass ports &lt;add|rem|set&gt; &lt;port[-portRangeEnd]/proto&gt; ...
Configure extra ports to bypass the VPN.
```text
$ speedify_cli streamingbypass ports add 4800/tcp 
{
	"domainWatchlistEnabled" : true,
	"domains" :
	[
		"hulu.com"
	],
	"ipv4" :
	[
		"8.8.8.8",
		"170.170.8.8"
	],
	"ipv6" : [],
	"ports" :
	[
		{
			"port" : 4800,
			"protocol" : "tcp"
		}
	],
	"services" :
...
```

## streamingbypass service &lt;enable|disable|service name&gt; [&lt;on|off&gt;]
Configures whether Speedify will allow traffic from a service to bypass the VPN.
```text
$ speedify_cli streamingbypass service Netflix on 
{
	"domainWatchlistEnabled" : true,
	"domains" :
	[
		"hulu.com"
	],
	"ipv4" :
	[
		"8.8.8.8",
		"170.170.8.8"
	],
	"ipv6" : [],
	"ports" :
	[
		{
			"port" : 4800,
			"protocol" : "tcp"
		}
	],
	"services" :
...
```

## subnets [subnet/length] ...
Configures a group of subnets connected to this machine as accessible by other clients on a private server. Only for advanced enterprise routing scenarios.
```text
$ speedify_cli subnets 192.168.202.1/23 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" :
	[
		{
			"address" : "192.168.8.8",
			"prefixLength" : 23
		}
	],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" :
	[
		{
			"port" : 8001,
			"protocol" : "tcp"
		}
...
```

## targetconnections &lt;number upload connections&gt; &lt;number download connections&gt;
The ```targetconnections``` command controls the amount of connections Speedify will attempt to use for upload and download, respectively.
```text
$ speedify_cli targetconnections 5 5 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" :
	[
		{
			"address" : "192.168.8.8",
			"prefixLength" : 23
		}
	],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" :
	[
		{
			"port" : 8001,
			"protocol" : "tcp"
		}
...
```

## transport &lt;auto|tcp|tcp-multi|udp|https&gt;
The ```transport``` command instructs Speedify to choose between one of the network protocols ```auto```, ```tcp```, ```tcp-multi```, ```udp```, or ```https```. The ```transport_mode``` value is set accordingly based on the user's selection.
```text
$ speedify_cli transport udp 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" :
	[
		{
			"address" : "192.168.8.8",
			"prefixLength" : 23
		}
	],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" :
	[
		{
			"port" : 8001,
			"protocol" : "tcp"
		}
...
```

## transportretry &lt;time in seconds&gt;
The ```transport``` command instructs Speedify to choose between one of the network protocols ```auto```, ```tcp```, ```tcp-multi```, ```udp```, or ```https```. The ```transport_mode``` value is set accordingly based on the user's selection.
```text
$ speedify_cli transport udp 
{
	"allowChaChaEncryption" : true,
	"bondingMode" : "speed",
	"downstreamSubnets" :
	[
		{
			"address" : "192.168.8.8",
			"prefixLength" : 23
		}
	],
	"enableAutomaticPriority" : true,
	"enableDefaultRoute" : true,
	"encrypted" : false,
	"fixedDelay" : 100,
	"forwardedPorts" :
	[
		{
			"port" : 8001,
			"protocol" : "tcp"
		}
...
```

## version
The ```version``` command can be used to verify the version of Speedify that is installed and running.
```text
$ speedify_cli version 
{
	"bug" : 2,
	"build" : 0,
	"maj" : 15,
	"min" : 7
}

```



_Copyright Connectify, Inc._

