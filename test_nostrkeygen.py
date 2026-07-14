#!/usr/bin/env python3

"""
Unabhängiger Test für nostrkeygen.py.

Prüft die von nostrkeygen.py erzeugten Schlüssel gegen zwei etablierte,
von nostrkeygen.py unabhängige Referenz-Implementierungen:

    - ecdsa   -> SECP256k1-Punktarithmetik (Public Key aus Private Key)
    - bech32  -> NIP-19-Referenzimplementierung (nsec/npub-Kodierung)

Einmalig (mit Internetzugang) installieren:

    pip install ecdsa bech32

Danach läuft dieses Testskript komplett offline.

WICHTIG: Dies ist ein reines Testskript, nostrkeygen.py selbst bleibt
abhängigkeitsfrei. Verwende hier nie einen Private Key, den du
produktiv nutzen willst - der Zweck dieses Skripts ist es, mit
zusätzlichem, nicht selbst geprüftem Code zu vergleichen.
"""

import sys

import nostrkeygen as keygen

try:
    import ecdsa
except ImportError:
    print("Fehlt: 'ecdsa'. Installiere mit: pip install ecdsa")
    sys.exit(1)

try:
    import bech32
except ImportError:
    print("Fehlt: 'bech32'. Installiere mit: pip install bech32")
    sys.exit(1)


def parse_private_key_hex(user_input: str) -> str:
    """
    Wandelt eine Benutzereingabe in einen 64-stelligen Hex-Private-Key um.

    Akzeptiert entweder rohes Hex (64 Zeichen) oder eine
    nsec1...-Kodierung.
    """

    text = user_input.strip()

    if text.lower().startswith("nsec1"):
        hrp, data = bech32.bech32_decode(text)

        if hrp != "nsec" or data is None:
            raise ValueError("Ungültiger nsec-String (falscher HRP oder Prüfsumme).")

        decoded = bech32.convertbits(data, 5, 8, pad=False)

        if decoded is None:
            raise ValueError("Ungültige nsec-Daten.")

        return bytes(decoded).hex()

    return text


def independent_public_key_hex(private_key_hex: str) -> str:
    """
    Berechnet den X-only Public Key unabhängig von nostrkeygen.py,
    mittels der 'ecdsa'-Bibliothek.
    """

    private_value = int(private_key_hex, 16)
    signing_key = ecdsa.SigningKey.from_secret_exponent(
        private_value, curve=ecdsa.SECP256k1
    )
    point = signing_key.verifying_key.pubkey.point

    return f"{point.x():064x}"


def independent_bech32(hrp: str, data_hex: str) -> str:
    """
    Kodiert Hex-Daten als Bech32-String, unabhängig von nostrkeygen.py,
    mittels der 'bech32'-Referenzbibliothek.
    """

    payload = bytes.fromhex(data_hex)
    data = bech32.convertbits(payload, 8, 5, pad=True)

    if data is None:
        raise ValueError("Bitkonvertierung fehlgeschlagen.")

    return bech32.bech32_encode(hrp, data)


def check(label: str, expected: str, actual: str) -> bool:
    ok = expected == actual
    status = "OK" if ok else "FEHLER"
    print(f"  [{status}] {label}")

    if not ok:
        print(f"         nostrkeygen.py:  {expected}")
        print(f"         unabhängig: {actual}")

    return ok


def main() -> None:
    print("=== Unabhängiger Test von nostrkeygen.py ===")
    print("(läuft komplett offline, keine Netzwerkverbindung nötig)")
    print()

    user_input = input("Private Key (Hex oder nsec1...): ").strip()
    private_key_hex = parse_private_key_hex(user_input)
    private_key = keygen.PrivateKey(int(private_key_hex, 16))

    public_key = keygen.createPublicKey(private_key)

    print()
    print("Vergleiche nostrkeygen.py gegen unabhängige Implementierungen ...")
    print()

    results = [
        check(
            "Public Key (X-only, hex)",
            public_key.to_hex(),
            independent_public_key_hex(private_key_hex),
        ),
        check(
            "nsec-Kodierung",
            private_key.to_nsec(),
            independent_bech32("nsec", private_key_hex),
        ),
        check(
            "npub-Kodierung",
            public_key.to_npub(),
            independent_bech32("npub", public_key.to_hex()),
        ),
    ]

    print()

    if all(results):
        print("Ergebnis: Alle Prüfungen bestanden.")
        print("nostrkeygen.py ist konsistent mit unabhängigen Referenzimplementierungen.")
    else:
        print("Ergebnis: Mindestens eine Prüfung ist fehlgeschlagen!")
        sys.exit(1)


if __name__ == "__main__":
    main()
