import math
import json
from matplotlib.ticker import EngFormatter

fmt_hz = EngFormatter(unit='Hz')

default_settings = {
    "searchband_scale": 10.0,
    "peak_threshold": 0.5,
    "show_plots": False,
    "custom_freq": None,
}

filename = "vmf_config.json"

# Global variables
SEARCHBAND_SCALE = None
PEAK_THRESHOLD = None
SHOW_PLOTS = None
CUSTOM_FREQ = None


def load_settings():
    """Load settings from the configuration file."""
    with open(filename, "r") as read_file:
        settings = json.load(read_file)
        print("Settings loaded.")
        return settings


def set_float(prompt, min_val=-math.inf, max_val=math.inf, allow_none=False):
    while True:
        response = input(f"\n{prompt}")
        try:
            response = float(response)
            if min_val <= response <= max_val:
                break
            else:
                print("Value out of bounds.")
        except ValueError:
            if allow_none and response.strip() == '':
                response = None
                break
            else:
                print("Enter a floating point number.")
    return response


def menu(prompt, choices, current_vals, units, show_reset_option=False):
    count = len(choices)
    print(f"\n{prompt}")
    for i in range(count):
        if units[i] == 'kHz':
            try:
                current_vals[i] = float(current_vals[i]) / 1000.0
            except:
                pass
        elif units[i] == 'eng_format_Hz' and str(current_vals[i]) != 'None':
            current_vals[i] = fmt_hz(float(current_vals[i]))
            units[i] = ''
        if str(current_vals[i]) == 'None':
            print(f"  [{i+1}] {choices[i]} = {current_vals[i]}")
        else:
            print(f"  [{i+1}] {choices[i]} = {current_vals[i]} {units[i]}")
    if show_reset_option:
        print("  ------------------------------------------")
        print("  [R] Reset all settings to default")
    print("\nPress Enter or 0 to continue.")
    response = input("\nYour choice: ")
    try:
        response = int(response)
        if response <= 0 or response > count:
            response = 0
    except ValueError:
        if show_reset_option and response.lower() == 'r':
            response = 'r'
        else:
            response = 0
    return response


def main():
    global SEARCHBAND_SCALE, PEAK_THRESHOLD, SHOW_PLOTS, CUSTOM_FREQ, settings

    settings = load_settings()
    menu_response = -1
    while menu_response != 0:
        menu_response = menu(
            "To change settings, choose from the following:",
            ['Searchband scale', 'Minimum peak width', 'Interactive mode', 'Show values at chosen frequency'],
            [settings["searchband_scale"], settings["peak_threshold"], settings["show_plots"], settings["custom_freq"]],
            ['', 'kHz', '', 'eng_format_Hz'],
            show_reset_option=True
        )
        if menu_response == 1:
            print("\nSearchband scale: adjusts the frequency window used to search for values corresponding to each peak.")
            settings["searchband_scale"] = set_float("New searchband scale [>= 1.0]: ", min_val=1.0)
        elif menu_response == 2:
            print("\nMinimum peak width: ignore peak if (Fp - Fs) is less than this value.")
            settings["peak_threshold"] = set_float("New minimum peak width [kHz, >= 0.0]: ", min_val=0.0) * 1000.0
        elif menu_response == 3:
            print("\nInteractive mode: show an interactive plot window for each CSV file.")
            settings["show_plots"] = set_float("[0] to disable, [1] to enable: ", min_val=0, max_val=1)
        elif menu_response == 4:
            print("\nAdd markers at a specified frequency.")
            settings["custom_freq"] = set_float("Enter a frequency [kHz] or leave blank for None: ", min_val=0.0, allow_none=True)
            if settings["custom_freq"] is not None:
                settings["custom_freq"] *= 1000.0
        elif menu_response == 'r':
            settings = default_settings.copy()
    # Amount to scale the search band by, as a multiplier to (Fp - Fs).
    SEARCHBAND_SCALE = settings["searchband_scale"]
    # Minimum width of peak considered (Fp - Fs)
    PEAK_THRESHOLD = settings["peak_threshold"]   # [Hz]
    # Whether to display VNA plots
    SHOW_PLOTS = False
    # Plot Z magnitude at user-specified frequency.
    CUSTOM_FREQ = settings["custom_freq"]   # [Hz]
    return SEARCHBAND_SCALE