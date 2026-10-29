import json
import logging
from pathlib import Path

from findmy import AppleAccount, LocalAnisetteProvider, RemoteAnisetteProvider, LoginState
from findmy import SmsSecondFactorMethod, TrustedDeviceSecondFactorMethod

logging.basicConfig(level=logging.INFO)

STORE_PATH = "account.json"
CONFIG_PATH = "config.json"
ANISETTE_LIBS_PATH = "ani_libs.bin"
ANISETTE_SERVER = None

def setup():
    try:
        acc = AppleAccount.from_json(STORE_PATH, anisette_libs_path=ANISETTE_LIBS_PATH)
        print("Konto jest juz zalogowane. (Aby zalogowac na nowo, usun plik account.json)")
    except FileNotFoundError:
        ani = (
            LocalAnisetteProvider(libs_path=ANISETTE_LIBS_PATH)
            if ANISETTE_SERVER is None
            else RemoteAnisetteProvider(ANISETTE_SERVER)
        )
        acc = AppleAccount(ani)

        email = input("Podaj adres email (Apple ID): > ")
        password = input("Podaj haslo: > ")

        state = acc.login(email, password)

        if state == LoginState.REQUIRE_2FA:
            print("\nWymagane uwierzytelnianie dwuskladnikowe (2FA).")
            methods = acc.get_2fa_methods()

            for i, method in enumerate(methods):
                if isinstance(method, TrustedDeviceSecondFactorMethod):
                    print(f"{i} - Zaufane urzadzenie")
                elif isinstance(method, SmsSecondFactorMethod):
                    print(f"{i} - SMS ({method.phone_number})")

            ind = int(input("\nWybierz metode wysylki (wpisz numer): > "))
            method = methods[ind]
            method.request()

            code = input("Podaj kod z Apple: > ")
            method.submit(code)

        acc.to_json(STORE_PATH)
        print(f"\nZalogowano pomyslnie jako: {acc.account_name} ({acc.first_name} {acc.last_name})\n")

    print("Pobieram liste urządzen...")
    try:
        devices = acc.fetch_devices()
    except Exception as e:
        print(f"Blad pobierania urzadzen: {e}")
        return

    if not devices:
        print("Brak przypisanych urządzen do tego konta.")
        return

    print("\nZnalezione urządzenia/AirTagi:")
    for i, dev in enumerate(devices):
        name = dev.name or dev.identifier
        print(f"{i} - {name} ({dev.__class__.__name__})")

    wybor_str = input("\nPodaj numery urzadzen, ktore chcesz monitorowac (oddzielone przecinkiem, np. 0,2): > ")
    if not wybor_str.strip():
        print("Nie wybrano żadnego urzadzenia. Zakończono.")
        return

    wybrane_indeksy = [int(x.strip()) for x in wybor_str.split(",") if x.strip().isdigit()]

    wybrane_identyfikatory = []
    for idx in wybrane_indeksy:
        if 0 <= idx < len(devices):
            dev = devices[idx]
            ident = dev.identifier
            wybrane_identyfikatory.append({
                "identifier": ident,
                "name": dev.name or ident
            })

    if wybrane_identyfikatory:
        config_data = {"tags": wybrane_identyfikatory}
        with open(CONFIG_PATH, "w") as f:
            json.dump(config_data, f, indent=4)
        print(f"\nZapisano konfiguracje do {CONFIG_PATH} z {len(wybrane_identyfikatory)} urzadzeniami do monitorowania.")
    else:
        print("Nie zapisano konfiguracji - brak poprawnie wybranych urzadzen.")

if __name__ == "__main__":
    setup()
