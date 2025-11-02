import sys

sys.path.append("../")
import speedify
import logging

logging.basicConfig(
    handlers=[logging.FileHandler("test.log"), logging.StreamHandler(sys.stdout)],
    format="%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s",
    level=logging.DEBUG,
)

"""
stats_callback sample: log whenever Wi-Fi SSID or speedify state changes
"""


class speedify_callback:
    def __init__(self):
        self.last_ssid = ""
        self.last_state = None

    def __call__(self, callback_input):
        if callback_input[0] == "adapters":
            self.adapter_callback(callback_input)
        elif callback_input[0] == "state":
            self.state_callback(callback_input)

    def adapter_callback(self, callback_input):
        networklist = callback_input[1]
        for network in networklist:
            if (network["type"] == "Wi-Fi") and (network["state"] == "connected"):
                if "connectedNetworkName" in network:
                    ssid = network["connectedNetworkName"]
                    if not self.last_ssid == ssid:
                        logging.info("SSID changed to " + ssid)
                        self.last_ssid = ssid

    def state_callback(self, callback_input):
        state_obj = callback_input[1]
        if "state" in state_obj:
            new_state = state_obj["state"]
            if new_state != self.last_state:
                logging.info("State changed to " + new_state)
                self.last_state = new_state

                # Call state-specific handler based on new state
                handler_name = f"on_{new_state.lower()}"
                if hasattr(self, handler_name):
                    handler = getattr(self, handler_name)
                    handler(state_obj)

    def on_logged_out(self, state_obj):
        """Called when Speedify transitions to LOGGED_OUT state."""
        logging.info("📴 User logged out of Speedify")
        # Put your custom code here for LOGGED_OUT state
        # Examples:
        # - Clear cached credentials
        # - Notify user to log back in
        # - Disable features that require Speedify connection
        # - Update UI to show logged out status

    def on_logging_in(self, state_obj):
        """Called when Speedify transitions to LOGGING_IN state."""
        logging.info("🔐 Logging in to Speedify...")
        # Put your custom code here for LOGGING_IN state
        # Examples:
        # - Show login progress indicator
        # - Display "Authenticating..." message

    def on_logged_in(self, state_obj):
        """Called when Speedify transitions to LOGGED_IN state."""
        logging.info("✅ Successfully logged in to Speedify")
        # Put your custom code here for LOGGED_IN state
        # Examples:
        # - Enable connection controls in UI
        # - Load user preferences/settings
        # - Show available servers
        # - Auto-connect if configured

    def on_auto_connecting(self, state_obj):
        """Called when Speedify is automatically connecting."""
        logging.info("🔄 Auto-connecting to Speedify...")
        # Put your custom code here for AUTO_CONNECTING state
        # Examples:
        # - Show connection progress
        # - Display "Auto-connecting..." status

    def on_connecting(self, state_obj):
        """Called when Speedify transitions to CONNECTING state."""
        logging.info("🔄 Connecting to Speedify server...")
        # Put your custom code here for CONNECTING state
        # Examples:
        # - Show connection progress indicator
        # - Display selected server information
        # - Show "Establishing secure connection..." message
        # - Disable disconnect button until connected

    def on_connected(self, state_obj):
        """Called when Speedify transitions to CONNECTED state."""
        logging.info("🚀 Connected to Speedify!")
        # Put your custom code here for CONNECTED state
        # Examples:
        # - Show connected server info (location, latency)
        # - Enable disconnect button
        # - Start monitoring connection statistics
        # - Display connection speed/quality metrics
        # - Trigger any actions that require active connection
        # - Send notification: "VPN connected"

    def on_disconnecting(self, state_obj):
        """Called when Speedify transitions to DISCONNECTING state."""
        logging.info("🔌 Disconnecting from Speedify...")
        # Put your custom code here for DISCONNECTING state
        # Examples:
        # - Show disconnection progress
        # - Clean up connection-dependent resources
        # - Save session statistics

    def on_overlimit(self, state_obj):
        """Called when Speedify transitions to OVERLIMIT state."""
        logging.warning("⚠️ Data limit exceeded - connection limited")
        # Put your custom code here for OVERLIMIT state
        # Examples:
        # - Show data usage warning to user
        # - Display upgrade prompt
        # - Notify user about limited connectivity
        # - Suggest switching to unlimited plan
        # - Show current data usage statistics

    def on_unknown(self, state_obj):
        """Called when Speedify transitions to UNKNOWN state."""
        logging.warning("❓ Speedify in unknown state")
        # Put your custom code here for UNKNOWN state
        # Examples:
        # - Log error details for debugging
        # - Show generic status message
        # - Attempt to refresh connection state


speedify_callback = speedify_callback()
speedify.stats_callback(0, speedify_callback)
