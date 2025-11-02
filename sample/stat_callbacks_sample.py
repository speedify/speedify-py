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
        self.last_adapters = {}  # Dict of {adapterID: adapter_info}

    def __call__(self, callback_input):
        if callback_input[0] == "adapters":
            self.adapter_callback(callback_input)
        elif callback_input[0] == "state":
            self.state_callback(callback_input)

    def adapter_callback(self, callback_input):
        networklist = callback_input[1]

        # Build current adapters dict for comparison
        current_adapters = {}
        for adapter in networklist:
            adapter_id = adapter.get("adapterID", "unknown")
            current_adapters[adapter_id] = adapter

            # Check for Wi-Fi SSID changes (original functionality)
            if (adapter["type"] == "Wi-Fi") and (adapter["state"] == "connected"):
                if "connectedNetworkName" in adapter:
                    ssid = adapter["connectedNetworkName"]
                    if not self.last_ssid == ssid:
                        logging.info("SSID changed to " + ssid)
                        self.last_ssid = ssid

        # Detect adapter changes
        current_ids = set(current_adapters.keys())
        last_ids = set(self.last_adapters.keys())

        # Check for added adapters
        added_ids = current_ids - last_ids
        for adapter_id in added_ids:
            adapter = current_adapters[adapter_id]
            self.on_adapter_added(adapter)

        # Check for removed adapters
        removed_ids = last_ids - current_ids
        for adapter_id in removed_ids:
            adapter = self.last_adapters[adapter_id]
            self.on_adapter_removed(adapter)

        # Check for state changes in existing adapters
        common_ids = current_ids & last_ids
        for adapter_id in common_ids:
            current = current_adapters[adapter_id]
            last = self.last_adapters[adapter_id]

            current_state = current.get("state", "unknown")
            last_state = last.get("state", "unknown")

            if current_state != last_state:
                self.on_adapter_state_changed(current, last_state, current_state)

        # Update our tracking
        self.last_adapters = current_adapters

    def on_adapter_added(self, adapter):
        """Called when a new adapter is detected."""
        adapter_type = adapter.get("type", "unknown")
        adapter_id = adapter.get("adapterID", "unknown")
        adapter_state = adapter.get("state", "unknown")

        logging.info(f"➕ Adapter added - Type: {adapter_type}, ID: {adapter_id}, State: {adapter_state}")
        # Put your custom code here for when adapters are added
        # Examples:
        # - Update UI to show new adapter
        # - Configure adapter priority/settings
        # - Send notification about new network interface
        # - Automatically enable/disable based on type
        # - Log hardware connection event

    def on_adapter_removed(self, adapter):
        """Called when an adapter is no longer detected."""
        adapter_type = adapter.get("type", "unknown")
        adapter_id = adapter.get("adapterID", "unknown")
        adapter_state = adapter.get("state", "unknown")

        logging.info(f"➖ Adapter removed - Type: {adapter_type}, ID: {adapter_id}, State: {adapter_state}")
        # Put your custom code here for when adapters are removed
        # Examples:
        # - Update UI to remove adapter from list
        # - Clean up adapter-specific resources
        # - Send notification about disconnected interface
        # - Log hardware disconnection event
        # - Switch to backup adapter if this was primary
        # - Alert if critical adapter (e.g., cellular failover) is removed

    def on_adapter_state_changed(self, adapter, old_state, new_state):
        """Called when an adapter's state changes."""
        adapter_type = adapter.get("type", "unknown")
        adapter_id = adapter.get("adapterID", "unknown")

        logging.info(f"🔄 Adapter state changed - Type: {adapter_type}, ID: {adapter_id}, {old_state} → {new_state}")
        # Put your custom code here for adapter state changes
        # Examples:
        # - Update UI indicator (connected/disconnected/connecting)
        # - Adjust bonding strategy based on available adapters
        # - Log connection quality changes
        # - Send notification if adapter goes down
        # - Trigger reconnection logic
        # - Update connection statistics display
        # - Alert if adapter becomes unusable

        # You can add specific logic based on the new state:
        if new_state == "connected":
            self.on_adapter_connected(adapter)
        elif new_state == "disconnected":
            self.on_adapter_disconnected(adapter)
        elif new_state == "connecting":
            self.on_adapter_connecting(adapter)

    def on_adapter_connected(self, adapter):
        """Called when an adapter successfully connects."""
        adapter_type = adapter.get("type", "unknown")
        adapter_id = adapter.get("adapterID", "unknown")

        logging.info(f"✅ Adapter connected - Type: {adapter_type}, ID: {adapter_id}")
        # Put your custom code here for adapter connection
        # Examples:
        # - Show "Connected via Wi-Fi" notification
        # - Display connection speed/quality
        # - Update bond quality indicator
        # - Enable adapter-specific features

    def on_adapter_disconnected(self, adapter):
        """Called when an adapter disconnects."""
        adapter_type = adapter.get("type", "unknown")
        adapter_id = adapter.get("adapterID", "unknown")

        logging.warning(f"❌ Adapter disconnected - Type: {adapter_type}, ID: {adapter_id}")
        # Put your custom code here for adapter disconnection
        # Examples:
        # - Show "Lost Wi-Fi connection" alert
        # - Attempt automatic reconnection
        # - Switch to backup connection
        # - Update UI to show disconnected state

    def on_adapter_connecting(self, adapter):
        """Called when an adapter is attempting to connect."""
        adapter_type = adapter.get("type", "unknown")
        adapter_id = adapter.get("adapterID", "unknown")

        logging.info(f"🔄 Adapter connecting - Type: {adapter_type}, ID: {adapter_id}")
        # Put your custom code here for adapter connection attempt
        # Examples:
        # - Show connection progress indicator
        # - Display "Connecting via Cellular..." message
        # - Monitor connection timeout

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
