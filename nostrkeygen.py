#!/usr/bin/env python3

"""
Eigenständiger Nostr-Key-Generator.

Keine externen Bibliotheken erforderlich.
Verwendet ausschließlich die Python-Standardbibliothek.

Erzeugte Formate:

Private Key:
    - Hex:  64 Hex-Zeichen
    - NIP-19: nsec1...

Public Key:
    - Hex:  64 Hex-Zeichen, X-only gemäß BIP-340/Nostr
    - NIP-19: npub1...

Empfohlene Python-Version: Python 3.10 oder neuer.
"""

from dataclasses import dataclass
import secrets
import socket
import sys
from typing import Optional, Union


# ---------------------------------------------------------------------------
# secp256k1-Parameter
# ---------------------------------------------------------------------------

# Primzahl des endlichen Feldes.
FIELD_PRIME = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F

# Ordnung der von G erzeugten Untergruppe.
CURVE_ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Generatorpunkt G.
GENERATOR_X = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
GENERATOR_Y = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8

GENERATOR = (GENERATOR_X, GENERATOR_Y)

# Der Punkt im Unendlichen wird als None dargestellt.
Point = Optional[tuple[int, int]]


# ---------------------------------------------------------------------------
# Key-Typen
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PrivateKey:
    """
    Ein gültiger secp256k1-Private-Key.

    Intern wird der Schlüssel als Integer gespeichert.
    """

    value: int

    def __post_init__(self) -> None:
        if not 1 <= self.value < CURVE_ORDER:
            raise ValueError(
                "Ein Private Key muss im Bereich 1 <= key < CURVE_ORDER liegen."
            )

    def to_bytes(self) -> bytes:
        return self.value.to_bytes(32, byteorder="big")

    def to_hex(self) -> str:
        return self.to_bytes().hex()

    def to_nsec(self) -> str:
        return bech32_encode("nsec", self.to_bytes())


@dataclass(frozen=True)
class PublicKey:
    """
    Ein Nostr-Public-Key im X-only-Format.

    Nostr verwendet nur die 32 Byte lange X-Koordinate des
    secp256k1-Punktes.
    """

    x: int

    def __post_init__(self) -> None:
        if not 0 <= self.x < FIELD_PRIME:
            raise ValueError("Ungültige X-Koordinate.")

    def to_bytes(self) -> bytes:
        return self.x.to_bytes(32, byteorder="big")

    def to_hex(self) -> str:
        return self.to_bytes().hex()

    def to_npub(self) -> str:
        return bech32_encode("npub", self.to_bytes())


Key = Union[PrivateKey, PublicKey]


# ---------------------------------------------------------------------------
# Öffentliche API
# ---------------------------------------------------------------------------

def createPrivateKey() -> PrivateKey:
    """
    Erzeugt einen kryptographisch zufälligen, gültigen Private Key.

    secrets.randbelow() verwendet die sichere Zufallsquelle des
    Betriebssystems.

    Der gültige Wertebereich ist:

        1 <= private_key < CURVE_ORDER
    """

    private_value = secrets.randbelow(CURVE_ORDER - 1) + 1
    return PrivateKey(private_value)


def createPublicKey(privateKey: PrivateKey) -> PublicKey:
    """
    Berechnet den Nostr-Public-Key aus einem Private Key.

    Der vollständige elliptische Kurvenpunkt ist:

        P = privateKey * G

    Nostr verwendet davon nur die 32 Byte lange X-Koordinate.
    """

    if not isinstance(privateKey, PrivateKey):
        raise TypeError("privateKey muss ein PrivateKey-Objekt sein.")

    point = scalar_multiply(privateKey.value, GENERATOR)

    if point is None:
        raise RuntimeError("Unerwarteter Punkt im Unendlichen.")

    public_x, _public_y = point
    return PublicKey(public_x)


def toString(key: Key) -> str:
    """
    Gibt einen Schlüssel im üblichen NIP-19-Format zurück:

        PrivateKey -> nsec1...
        PublicKey  -> npub1...
    """

    if isinstance(key, PrivateKey):
        return key.to_nsec()

    if isinstance(key, PublicKey):
        return key.to_npub()

    raise TypeError("key muss PrivateKey oder PublicKey sein.")


# ---------------------------------------------------------------------------
# secp256k1-Arithmetik
# ---------------------------------------------------------------------------

def modular_inverse(value: int, modulus: int) -> int:
    """
    Berechnet das multiplikative Inverse:

        value^(-1) mod modulus

    FIELD_PRIME ist eine Primzahl. Deshalb kann Fermats kleiner Satz
    verwendet werden:

        value^(-1) = value^(modulus - 2) mod modulus
    """

    value %= modulus

    if value == 0:
        raise ZeroDivisionError("Null besitzt kein multiplikatives Inverses.")

    return pow(value, modulus - 2, modulus)


def is_on_curve(point: Point) -> bool:
    """
    Prüft, ob ein Punkt auf secp256k1 liegt.

    secp256k1:

        y² = x³ + 7 mod FIELD_PRIME
    """

    if point is None:
        return True

    x, y = point

    if not (0 <= x < FIELD_PRIME and 0 <= y < FIELD_PRIME):
        return False

    return (y * y - (x * x * x + 7)) % FIELD_PRIME == 0


def point_add(point_a: Point, point_b: Point) -> Point:
    """
    Addiert zwei Punkte auf secp256k1.
    """

    if point_a is None:
        return point_b

    if point_b is None:
        return point_a

    if not is_on_curve(point_a) or not is_on_curve(point_b):
        raise ValueError("Mindestens ein Punkt liegt nicht auf secp256k1.")

    x1, y1 = point_a
    x2, y2 = point_b

    # P + (-P) ergibt den Punkt im Unendlichen.
    if x1 == x2 and (y1 + y2) % FIELD_PRIME == 0:
        return None

    if point_a == point_b:
        # Punktverdopplung.
        #
        # Steigung:
        #   m = 3*x1² / (2*y1)
        if y1 == 0:
            return None

        numerator = 3 * x1 * x1
        denominator = modular_inverse(2 * y1, FIELD_PRIME)
    else:
        # Addition zweier verschiedener Punkte.
        #
        # Steigung:
        #   m = (y2-y1) / (x2-x1)
        numerator = y2 - y1
        denominator = modular_inverse(x2 - x1, FIELD_PRIME)

    slope = numerator * denominator % FIELD_PRIME

    x3 = (slope * slope - x1 - x2) % FIELD_PRIME
    y3 = (slope * (x1 - x3) - y1) % FIELD_PRIME

    result = (x3, y3)

    if not is_on_curve(result):
        raise RuntimeError("Fehler bei der elliptischen Kurvenberechnung.")

    return result


def scalar_multiply(scalar: int, point: Point) -> Point:
    """
    Berechnet:

        scalar * point

    mit dem Double-and-Add-Verfahren.
    """

    if not isinstance(scalar, int):
        raise TypeError("scalar muss ein Integer sein.")

    if scalar < 0:
        raise ValueError("Negative Skalare werden nicht unterstützt.")

    if point is not None and not is_on_curve(point):
        raise ValueError("Der Punkt liegt nicht auf secp256k1.")

    scalar %= CURVE_ORDER

    if scalar == 0 or point is None:
        return None

    result: Point = None
    addend: Point = point

    while scalar:
        if scalar & 1:
            result = point_add(result, addend)

        addend = point_add(addend, addend)
        scalar >>= 1

    return result


# ---------------------------------------------------------------------------
# Bech32 / NIP-19
# ---------------------------------------------------------------------------

BECH32_CHARSET = "qpzry9x8gf2tvdw0s3jn54khce6mua7l"


def bech32_polymod(values: list[int]) -> int:
    """
    Berechnet die Bech32-Prüfsumme.
    """

    generators = (
        0x3B6A57B2,
        0x26508E6D,
        0x1EA119FA,
        0x3D4233DD,
        0x2A1462B3,
    )

    checksum = 1

    for value in values:
        top = checksum >> 25
        checksum = ((checksum & 0x1FFFFFF) << 5) ^ value

        for index, generator in enumerate(generators):
            if (top >> index) & 1:
                checksum ^= generator

    return checksum


def bech32_expand_hrp(hrp: str) -> list[int]:
    """
    Expandiert den Human-Readable Part für die Prüfsumme.
    """

    return (
        [ord(character) >> 5 for character in hrp]
        + [0]
        + [ord(character) & 31 for character in hrp]
    )


def bech32_create_checksum(hrp: str, data: list[int]) -> list[int]:
    """
    Erzeugt die sechs Bech32-Prüfsummenwerte.
    """

    values = bech32_expand_hrp(hrp) + data
    polymod = bech32_polymod(values + [0, 0, 0, 0, 0, 0]) ^ 1

    return [
        (polymod >> (5 * (5 - index))) & 31
        for index in range(6)
    ]


def convert_bits(
    data: bytes,
    from_bits: int,
    to_bits: int,
    pad: bool = True,
) -> list[int]:
    """
    Konvertiert eine Folge von from_bits-Gruppen in to_bits-Gruppen.

    Für NIP-19 werden 8-Bit-Bytes in 5-Bit-Werte umgewandelt.
    """

    accumulator = 0
    bit_count = 0
    result: list[int] = []

    max_output_value = (1 << to_bits) - 1
    max_accumulator = (1 << (from_bits + to_bits - 1)) - 1

    for value in data:
        if value < 0 or value >> from_bits:
            raise ValueError("Ungültiger Wert für die Bitkonvertierung.")

        accumulator = (
            ((accumulator << from_bits) | value)
            & max_accumulator
        )
        bit_count += from_bits

        while bit_count >= to_bits:
            bit_count -= to_bits
            result.append(
                (accumulator >> bit_count) & max_output_value
            )

    if pad:
        if bit_count:
            result.append(
                (accumulator << (to_bits - bit_count))
                & max_output_value
            )
    else:
        if bit_count >= from_bits:
            raise ValueError("Ungültige Restbits.")

        if (
            (accumulator << (to_bits - bit_count))
            & max_output_value
        ):
            raise ValueError("Nicht-null Padding erkannt.")

    return result


def bech32_encode(hrp: str, payload: bytes) -> str:
    """
    Kodiert Bytes als Bech32-String.

    Beispiele für den HRP:

        nsec -> privater Nostr-Schlüssel
        npub -> öffentlicher Nostr-Schlüssel
    """

    if not hrp:
        raise ValueError("Der Bech32-HRP darf nicht leer sein.")

    if hrp.lower() != hrp:
        raise ValueError("Der HRP muss kleingeschrieben sein.")

    if any(ord(character) < 33 or ord(character) > 126 for character in hrp):
        raise ValueError("Der HRP enthält ungültige Zeichen.")

    data = convert_bits(payload, from_bits=8, to_bits=5, pad=True)
    checksum = bech32_create_checksum(hrp, data)

    encoded_data = "".join(
        BECH32_CHARSET[value]
        for value in data + checksum
    )

    result = hrp + "1" + encoded_data

    if len(result) > 90:
        raise ValueError("Der Bech32-String überschreitet 90 Zeichen.")

    return result


# ---------------------------------------------------------------------------
# Selbsttests
# ---------------------------------------------------------------------------

def run_self_tests() -> None:
    """
    Führt grundlegende Tests aus.

    Der bekannte secp256k1-Testvektor für Private Key 1 lautet:

        Public X =
        79be667ef9dcbbac55a06295ce870b070
        29bfcdb2dce28d959f2815b16f81798
    """

    assert is_on_curve(GENERATOR)

    private_key = PrivateKey(1)
    public_key = createPublicKey(private_key)

    expected_public_hex = (
        "79be667ef9dcbbac55a06295ce870b070"
        "29bfcdb2dce28d959f2815b16f81798"
    )

    assert private_key.to_hex() == "0" * 63 + "1"
    assert public_key.to_hex() == expected_public_hex

    assert private_key.to_nsec().startswith("nsec1")
    assert public_key.to_npub().startswith("npub1")

    assert len(private_key.to_bytes()) == 32
    assert len(public_key.to_bytes()) == 32


# ---------------------------------------------------------------------------
# Sicherheits-Utilities
# ---------------------------------------------------------------------------

def check_internet_access(timeout: float = 1.0) -> bool:
    """
    Prüft, ob gerade eine Internetverbindung besteht.

    Baut testweise eine TCP-Verbindung zu bekannten, öffentlichen
    DNS-Servern auf. Es werden dabei keine Anwendungsdaten gesendet,
    nur der TCP-Handshake dient als Erreichbarkeitstest.
    """

    probe_targets = (
        ("1.1.1.1", 53),
        ("8.8.8.8", 53),
    )

    for host, port in probe_targets:
        try:
            connection = socket.create_connection((host, port), timeout=timeout)
            connection.close()
            return True
        except OSError:
            continue

    return False


def abort_if_internet_reachable() -> None:
    """
    Bricht das Programm ab, falls das Gerät gerade online ist.

    Für maximale Sicherheit darf dieses Skript nur ohne aktive
    Internetverbindung ausgeführt werden (WLAN/LAN trennen oder
    Flugmodus aktivieren).
    """

    if not check_internet_access():
        print("Internet-Check: Keine Verbindung erkannt.")
        print()
        return

    print("!" * 70)
    print("ABBRUCH: Dieses Gerät hat aktuell Zugriff auf das Internet.")
    print("Trenne WLAN/Netzwerkkabel bzw. aktiviere den Flugmodus und")
    print("starte das Skript danach erneut.")
    print("!" * 70)

    raise SystemExit(1)


def clear_terminal() -> None:
    """
    Löscht den sichtbaren Bildschirm inklusive Scrollback-Puffer.

    Nutzt ANSI-Escape-Sequenzen (funktioniert in Terminal.app,
    iTerm2 und den meisten modernen Terminals).
    """

    print("\033[H\033[2J\033[3J", end="")
    sys.stdout.flush()


# ---------------------------------------------------------------------------
# Beispielprogramm
# ---------------------------------------------------------------------------

def main() -> None:
    run_self_tests()

    print("=== Nostr Key Generator ===")
    print("Läuft vollständig lokal, ohne externe Bibliotheken.")
    print()

    abort_if_internet_reachable()

    input("Drücke [Enter], um einen neuen Schlüssel zu erzeugen und anzuzeigen ...")
    print()

    private_key = createPrivateKey()
    public_key = createPublicKey(private_key)

    print("Private Key")
    print("  hex: ", private_key.to_hex())
    print("  nsec:", toString(private_key))
    print()

    print("Public Key")
    print("  hex: ", public_key.to_hex())
    print("  npub:", toString(public_key))
    print()

    input("Drücke [Enter], um den Bildschirm zu löschen und zu beenden ...")
    clear_terminal()


if __name__ == "__main__":
    main()
