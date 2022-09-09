import sys

sys.path.append("../")
import speedifysettings
import logging

logging.basicConfig(
    handlers=[logging.FileHandler("test.log"), logging.StreamHandler(sys.stdout)],
    format="%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s",
    level=logging.INFO,
)

# Get the default settings, and apply them to just put us in a known state
success = speedifysettings.apply_speedify_settings(speedifysettings.speedify_defaults)
if success:
    logging.info("Default settings applied successfully")
    sys.exit(0)
else:
    logging.info("Failed to apply default settings")
    sys.exit(1)
