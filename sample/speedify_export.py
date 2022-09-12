import sys

sys.path.append("../")
import speedifysettings
import logging

# Write out the current speedify settings to std out
logging.basicConfig(
    handlers=[logging.FileHandler("test.log"), logging.StreamHandler(sys.stdout)],
    format="%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s",
    level=logging.INFO,
)

currentsettings = speedifysettings.get_speedify_settings_as_json_string()
print(currentsettings)
