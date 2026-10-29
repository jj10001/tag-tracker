import json
import logging
import os
from datetime import datetime
from pathlib import Path

from findmy import AppleAccount

logging.basicConfig(level=logging.INFO)

STORE_PATH = "account.json"
CONFIG_PATH = "config.json"
ANISETTE_LIBS_PATH = "ani_libs.bin"

DATA_DIR = Path("../data")

def main():
    if not os.path.exists(STORE_PATH):
        print(f"Blad: Brak pliku sesji {STORE_PATH}. Uruchom najpierw login_and_setup.py.")
        return

    if not os.path.exists(CONFIG_PATH):
        print(f"Blad: Brak pliku konfiguracji {CONFIG_PATH}. Uruchom najpierw login_and_setup.py.")
        return

    with open(CONFIG_PATH, "r") as f:
        config_data = json.load(f)

    tags_to_monitor = config_data.get("tags", [])
    if not tags_to_monitor:
        print("Brak tagów do monitorowania w konfiguracji.")
        return

    monitored_identifiers = {tag["identifier"]: tag["name"] for tag in tags_to_monitor}

    print("Wczytywanie konta...")
    acc = AppleAccount.from_json(STORE_PATH, anisette_libs_path=ANISETTE_LIBS_PATH)

    print("Pobieranie urzadzen z serwerów Apple...")
    devices = acc.fetch_devices()

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR, exist_ok=True)

    today_str = datetime.now().strftime("%Y%m%d")
    current_time_iso = datetime.now().isoformat()

    found_any = False

    for dev in devices:
        if dev.identifier in monitored_identifiers:
            found_any = True
            name = monitored_identifiers[dev.identifier]
            print(f"Znaleziono urzadzenie: {name}")

            # Use appropriate file name: YYYYMMDD-nazwa.jsonl
            # Sanitize name for file path
            safe_name = "".join([c for c in name if c.isalpha() or c.isdigit() or c in (' ', '-', '_')]).rstrip()
            filename = f"{today_str}-{safe_name}.jsonl"
            filepath = DATA_DIR / filename

            try:
                # Some devices might not have location data available right away
                # The FindMy.py library usually exposes location properties on the device object itself
                # Or we can use fetch_location if it's a specific tag

                # Fetching the most recent location via acc.fetch_location() or directly from device
                # The library fetch_devices() typically returns devices that already contain location data
                location = acc.fetch_location(dev)

                if location is None:
                    print(f" Brak lokalizacji dla {name}")
                    continue

                location_data = {
                    "timestamp": current_time_iso,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "altitude": location.altitude,
                    "accuracy": location.horizontal_accuracy,
                    "status": location.status,
                    "location_timestamp": location.timestamp.isoformat() if location.timestamp else None,
                    "identifier": dev.identifier,
                    "name": name
                }

                with open(filepath, "a") as f:
                    f.write(json.dumps(location_data) + "\n")

                print(f" Zapisano pozycje: {location.latitude}, {location.longitude} do {filepath}")
            except Exception as e:
                print(f" Blad podczas pobierania/zapisywania lokalizacji dla {name}: {e}")

    if not found_any:
        print("Nie znaleziono zadnych z monitorowanych urządzen podczas pobierania.")

    # Save the updated session token
    acc.to_json(STORE_PATH)

if __name__ == "__main__":
    main()
