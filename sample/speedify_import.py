import sys

sys.path.append("../")
import speedifysettings
import logging
import fileinput

# takes a settings json and applies the settings.  Either name on command line or piped in a stdin.
logging.basicConfig(
    handlers=[logging.FileHandler("test.log"), logging.StreamHandler(sys.stdout)],
    format="%(asctime)s\t%(levelname)s\t%(module)s\t%(message)s",
    level=logging.INFO,
)

for line in fileinput.input():
    speedifysettings.apply_speedify_settings(line)
