# Deine Nostr-Identität sicher erstellen

Diese Anleitung zeigt dir Schritt für Schritt, wie du dir auf deinem eigenen
Computer eine eigene Nostr-Identität erzeugst — ganz ohne Vorwissen über
Nostr, Computer oder Programmierung. Du brauchst dafür nur etwas Geduld und
diese Anleitung.

Nostr ist ein soziales Netzwerk, bei dem du dich nicht bei einer Firma
registrierst. Stattdessen bekommst du zwei zusammengehörende Zeichenketten,
die zusammen deine Identität bilden. Genau die erzeugen wir jetzt für dich.

## Die Bankkonto-Analogie

Damit du verstehst, was du gleich in den Händen hältst, hilft ein Vergleich
mit etwas, das du bereits kennst: deine Bankkarte.

| Bankenwelt | Nostr |
|---|---|
| IBAN / Kartennummer — darf jeder wissen | **Public Key** — beginnt mit `npub1...` |
| PIN / CVC — bleibt geheim | **Private Key** — beginnt mit `nsec1...` |

- Deinen **Public Key** (`npub...`) kannst du bedenkenlos herausgeben, genau
  wie deine IBAN. Andere Menschen erkennen dich daran und können mit dir in
  Kontakt treten.
- Deinen **Private Key** (`nsec...`) musst du absolut geheim halten, genau
  wie deine PIN. Mit ihm "unterschreibst" du alles, was du auf Nostr
  veröffentlichst — so wie du an der Kasse deine PIN eingibst, um eine
  Zahlung zu bestätigen. Nur durch diese Unterschrift wissen andere, dass
  ein Beitrag wirklich von dir stammt und nicht gefälscht ist.

**Der entscheidende Unterschied zur Bank:** Bei einer Bank gibt es eine
Zentrale — die Bank selbst —, die dir IBAN und PIN ausstellt und im
Ernstfall hilft, wenn etwas verloren geht oder gestohlen wird. Bei Nostr
gibt es diese Zentrale nicht. Dein Schlüsselpaar wird stattdessen rein
mathematisch erzeugt, ohne dass irgendjemand darüber wacht.

Das bedeutet: **Du selbst bist ab dem Moment der Erzeugung ganz allein dafür
verantwortlich, deinen Private Key zu schützen.** Niemand kann ihn dir
ersetzen, niemand kann dir helfen, falls er verloren geht oder in falsche
Hände gerät. Genau deshalb gehen wir bei der Erzeugung besonders vorsichtig
vor:

- Wir trennen die Internetverbindung, bevor der Schlüssel erzeugt wird —
  damit er auf keinem Weg von irgendjemandem "mitgelesen" werden kann.
- Sobald deine Schlüssel auf dem Bildschirm erscheinen, musst du deinen
  Private Key **sofort** sicher notieren. Das Programm löscht die Anzeige
  danach absichtlich wieder — es gibt keine zweite Chance, ihn sich noch
  einmal anzeigen zu lassen.

## Was du vorbereiten solltest

- Die Datei `nostrkeygen.py` liegt bereits auf deinem Computer (z. B. auf
  deinem Schreibtisch/Desktop). Falls nicht, lege sie dort ab, bevor du
  weitermachst.
- Eine Internetverbindung brauchst du nur einmalig, falls auf deinem
  Computer noch keine "Python"-Software installiert ist (siehe unten).
  Danach wird kein Internet mehr benötigt.
- Etwas zum sicheren Notieren deines Private Keys: Stift und Papier (das du
  anschließend an einem sicheren Ort aufbewahrst, z. B. einem Safe) oder ein
  vertrauenswürdiger Passwort-Manager. Wie genau du ihn aufbewahrst, ist dir
  überlassen — wichtig ist nur, dass es sofort geschieht und dauerhaft
  sicher bleibt.

Wähle nun den Abschnitt für dein Betriebssystem:

---

## Anleitung für Mac

### Schritt 1: Prüfen, ob Python vorhanden ist

Dieses Programm ist in der Sprache "Python" geschrieben. Dein Mac braucht
das, um es auszuführen.

1. Öffne das **Terminal**: Drücke gleichzeitig `Cmd` und `Leertaste`, tippe
   `Terminal` ein und drücke `Enter`.
2. Es öffnet sich ein schwarzes/weißes Fenster mit Text — das ist das
   Terminal. Hier tippst du Befehle ein statt mit der Maus zu klicken.
3. Tippe folgendes ein und drücke `Enter`:

   ```
   python3 --version
   ```

4. Erscheint eine Versionsnummer (z. B. `Python 3.11.4`), ist alles bereit —
   weiter mit Schritt 2.
5. Erscheint stattdessen ein Fenster, das die Installation der
   "Command Line Developer Tools" anbietet, klicke auf **Installieren** und
   warte, bis es fertig ist (das kann einige Minuten dauern). Tippe danach
   den Befehl aus Punkt 3 erneut ein, um es zu prüfen.
6. Passiert gar nichts oder gibt es eine Fehlermeldung, lade Python von
   `https://www.python.org/downloads/` herunter und installiere es wie eine
   normale Mac-Anwendung.

### Schritt 2: Zum richtigen Ordner wechseln

Im Terminal tippst du jetzt `cd ` — **mit einem Leerzeichen danach, aber
noch nicht `Enter` drücken.** Ziehe nun den Ordner, in dem `nostrkeygen.py`
liegt (z. B. deinen Desktop-Ordner), mit der Maus aus dem Finder direkt in
das Terminal-Fenster. Der Pfad wird automatisch eingefügt. Jetzt `Enter`
drücken.

### Schritt 3: Internetverbindung trennen

Klicke oben rechts in der Menüleiste auf das WLAN-Symbol und schalte WLAN
aus. Falls dein Mac per Kabel verbunden ist, ziehe das Netzwerkkabel ab.

### Schritt 4: Das Programm starten

Tippe im Terminal ein:

```
python3 nostrkeygen.py
```

und drücke `Enter`.

Weiter geht es bei [Was jetzt passiert](#was-jetzt-passiert) weiter unten.

---

## Anleitung für Windows

### Schritt 1: Python installieren (falls noch nicht vorhanden)

1. Öffne den **Microsoft Store** (über das Startmenü suchen).
2. Suche dort nach `Python 3` und installiere die oberste, offizielle
   Python-App.
3. Öffne danach **PowerShell**: Klicke auf das Startmenü/Windows-Symbol,
   tippe `PowerShell` ein und drücke `Enter`.
4. Es öffnet sich ein blaues Fenster mit Text — das ist die
   Kommandozeile/PowerShell. Hier tippst du Befehle ein statt mit der Maus
   zu klicken.
5. Prüfe die Installation, indem du eingibst:

   ```
   python --version
   ```

   Erscheint eine Versionsnummer (z. B. `Python 3.12.1`), ist alles bereit.

### Schritt 2: Zum richtigen Ordner wechseln

Tippe in PowerShell `cd ` ein — **mit einem Leerzeichen danach, aber noch
nicht `Enter` drücken.** Ziehe nun den Ordner, in dem `nostrkeygen.py`
liegt (z. B. deinen Desktop-Ordner), mit der Maus aus dem Explorer direkt in
das PowerShell-Fenster. Der Pfad wird automatisch eingefügt. Jetzt `Enter`
drücken.

### Schritt 3: Internetverbindung trennen

Klicke unten rechts in der Taskleiste auf das Netzwerksymbol und schalte
WLAN aus, oder aktiviere den Flugmodus. Falls dein PC per Kabel verbunden
ist, ziehe das Netzwerkkabel ab.

### Schritt 4: Das Programm starten

Tippe in PowerShell ein:

```
python nostrkeygen.py
```

und drücke `Enter`.

Falls eine Fehlermeldung wie `'python' wird nicht erkannt` erscheint,
versuche stattdessen:

```
py nostrkeygen.py
```

---

## Was jetzt passiert

Das Programm meldet sich mit ein paar Zeilen Text. Falls es sich sofort mit
einer Warnung beendet, weil es noch eine Internetverbindung erkennt, trenne
die Verbindung wie in Schritt 3 beschrieben und starte das Programm einfach
erneut.

Danach wirst du gebeten, `Enter` zu drücken, um deinen Schlüssel zu
erzeugen und anzuzeigen. Es erscheinen vier Werte:

```
Private Key
  hex:  ...
  nsec: nsec1...

Public Key
  hex:  ...
  npub: npub1...
```

<img width="679" height="339" alt="image" src="https://github.com/user-attachments/assets/ebe14b51-44bb-4d42-abb0-d34eae85b73d" />


**Jetzt zählt jede Sekunde:** Notiere dir sofort — bevor du irgendetwas
anderes tust — die beiden Zeilen `nsec:` und `npub:` an deinem sicheren Ort
(Papier im Safe oder Passwort-Manager). Die `hex:`-Werte sind nur eine
technische Alternativschreibweise derselben Schlüssel und werden für die
normale Nutzung nicht gebraucht.

Zur Erinnerung: Der `nsec`-Wert ist deine geheime PIN — er darf niemals mit
jemand anderem geteilt werden. Der `npub`-Wert ist deine öffentliche
IBAN — den kannst du bedenkenlos weitergeben.

Erst wenn du beides sicher notiert hast, drücke die zweite Aufforderung mit
`Enter`. Der Bildschirm wird danach bewusst gelöscht, damit dein Private Key
nirgends im Terminal-Verlauf stehen bleibt.

Das war's — du hast jetzt deine eigene Nostr-Identität.

## Wichtig: Wie du deinen nsec später verwendest

Sobald du Nostr tatsächlich nutzt, wirst du irgendwann auf Webseiten oder
Apps treffen, die dich zur "Anmeldung" nach deinem privaten Schlüssel
fragen. **Tippe deinen nsec dort nach Möglichkeit nicht direkt ein.**

Genau wie du deine Bank-PIN nicht bei jedem Online-Shop eintippst, sondern
nur in das Gerät deiner eigenen Bank vertraust, gibt es für Nostr eigene,
dafür gemachte Erweiterungen für deinen Browser — oft "Wallet" oder
"Signer" genannt (bekannte Beispiele sind ["Alby"](https://chromewebstore.google.com/detail/alby-bitcoin-wallet-for-l/iokeahhehimjnekafflcihljlcjccdbe) oder ["nos2x"](https://chromewebstore.google.com/detail/nos2x/kpgefcfmnafjgpblomihpgmejjdanjjp)). Dort trägst
du deinen nsec einmalig sicher ein. Alle Nostr-Webseiten und -Apps sprechen
danach nur noch mit dieser Erweiterung, wenn sie eine Unterschrift von dir
brauchen — deinen nsec selbst bekommen sie dabei nie zu Gesicht.

Wenn eine Webseite oder App dich zwingt, deinen nsec direkt in ein
Eingabefeld einzutippen, ist das ein Warnsignal: Sei besonders vorsichtig,
oder nutze lieber eine App, die stattdessen mit einer solchen
Wallet-Erweiterung zusammenarbeitet.

## Wenn etwas nicht funktioniert

- **"python3: command not found" / "'python' wird nicht erkannt"**: Python
  ist nicht (richtig) installiert. Gehe zurück zu Schritt 1 deiner
  Plattform.
- **Das Programm bricht sofort mit einer Warnung zu Internetzugriff ab**:
  Trenne WLAN/Netzwerkkabel vollständig (auch andere Verbindungen wie
  Mobilfunk-Hotspots) und starte das Programm erneut.
- **Ich habe aus Versehen `Enter` gedrückt, bevor ich den nsec notiert
  habe**: Kein Problem — starte das Programm einfach erneut, es erzeugt
  dann ein komplett neues, ebenso gültiges Schlüsselpaar. Verwende nur das
  Schlüsselpaar, das du dir tatsächlich notiert hast.

## Ist dieser Code sicher?

Wenn du willst, lass ChatGPT oder eine andere KI den Code für die Schlüsselgenerierung vor Nutung prüfen.
Kopiere dazu den Inhalt der Datei `nostrkeygen.py` in einen KI-Chat und bitte um einen Sicherheitscheck.

<img width="604" height="237" alt="image" src="https://github.com/user-attachments/assets/4621e354-25c7-47c5-a398-6e0787a628b3" />

Das Ergebnis wird recht technisch sein und nicht einfach "Ja, alles sicher lauten". Irgendetwas findet KI immer zum Kritisieren. Das bedeutet, du musst auch hier selbst entscheiden, wieviel Risiko du noch eingehen willst. Wie wichtig ist die Nostr Identität für dein Leben wirklich, wirklich? Lohnt sich die extra Meile, die die KI dir aufzeigt? Oder bist du mit der Sicherheit zufrieden, die ansonsten überprüfter Code, der ohne Internetverbindung läuft, bietet?

## Für technisch Interessierte (optional)

Wer möchte, kann die erzeugten Schlüssel zusätzlich mit `test_nostrkeygen.py`
gegen unabhängige Referenz-Software prüfen. Das erfordert etwas technisches
Vorwissen und zusätzliche Software-Installation und ist für die normale
Nutzung **nicht notwendig**.
