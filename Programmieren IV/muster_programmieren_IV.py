#Funktionen
#def begruessung():
#	print("Hallo!")

#begruessung()

#def begruessung(name):
#	print("Hallo", name)

#begruessung("Anna")

#Übung
#Schreibe eine Funktion namens vorstellung, die einen Namen als Eingabe (Parameter) bekommt
#und den Satz „Mein Name ist ...“ ausgibt.
#Rufe die Funktion mindestens zweimal auf, mit unterschiedlichen Namen.

#def vorstellung(name):
#	print(f"Mein Name ist {name}.")

#vorstellung("Patrick")
#vorstellung("Constance")

#Bonusaufgabe:
#Ergänze einen zweiten Parameter rolle und gib z.B. aus:
#Mein Name ist Constance. Ich war Aktivistin.

#def vorstellung(name, rolle):
#	print(f"Mein Name ist {name}. ich war {rolle}.")

#vorstellung("Constance","Aktivistin")

#ÜBUNG API
#import requests

#response = requests.get("https://catfact.ninja/fact")
#data = response.json()

#print("Katzenfakt:", data["fact"])

#Wiederholung
#Aufgabe zu time:
#Schreibe ein Programm, das so tut, als würde es eine Webseite laden.
#Gib zuerst aus: "Starte Webabfrage..."
#Warte 2 Sekunden, um eine „Ladezeit“ zu simulieren
#Gib danach aus: "Antwort erhalten."
#(Bonus) Miss die tatsächliche vergangene Zeit und gib sie in Sekunden aus

#import time

#print("Starte Webabfrage...")
#time.sleep(2)
#print("Antwort erhalten.")

#Bonus:
#start = time.time()  # Startzeit

#print("Starte Webabfrage...")
#time.sleep(2)
#print("Antwort erhalten.")

#end = time.time()  # Endzeit
#dauer = end - start
#print(f"Dauer: {dauer:.2f} Sekunden")


#Übung Liste bearbeiten mit Funktionen
#Erstelle eine Liste mit mindestens 3 historischen Namen (z.B. "Constance Markievicz", "James Connolly", "Patrick Pearse")
#Schreibe eine Funktion namens vorstellen(name), die zu einem Namen den Satz ausgibt: "Mein Name ist NAME. Ich war am Osteraufstand beteiligt."
#Verwende eine for-Schleife, um die Funktion für jeden Namen in der Liste aufzurufen.

#namen = ["Constance Markievicz", "James Connolly", "Patrick Pearse"]

#def vorstellen(name):
#    print(f"Mein Name ist {name}. Ich war am Osteraufstand beteiligt.")

#for name in namen:
#    vorstellen(name)

#Bonusaufgabe:
#Speichere alle Sätze in einer Liste texte (beginne mit einer leeren Liste texte = [])
#Schreibe sie anschließend zeilenweise in eine Datei personen.txt.

#texte = []

#def vorstellen(name):
#    satz = f"Mein Name ist {name}. Ich war am Osteraufstand beteiligt."
#    texte.append(satz)

#for name in namen:
#    vorstellen(name)

#with open("personen.txt", "w", encoding="utf-8") as f:
#    for zeile in texte:
#        f.write(zeile + "\n")

#Übung BeautifulSoup und Project Guttenberg
#Wir arbeiten mit folgender Website:
#url = “https://www.gutenberg.org/files/12871/12871-h/12871-h.htm”
#Unser Ziel ist es alle Wörter zu extrahieren, die großgeschrieben sind (DUBLIN, VOLUNTEERS, etc)..
#Und in einer Liste zu speichern (ohne Doppelungen!).
#Die Liste soll anschließend in einer alphabetisch sortierten Liste (begriffe.txt, ein Begriff pro Zeile) gespeichert werden.
#Wo sinnvoll, definiere eigene Funktionen (etwa für das Finden von großgeschriebenen Wörtern.)


#import requests
#from bs4 import BeautifulSoup

# Schritt 1: Webseite abrufen
#url = "https://www.gutenberg.org/files/12871/12871-h/12871-h.htm"
#response = requests.get(url)
#soup = BeautifulSoup(response.text, "html.parser")

# Schritt 2: Nur Textinhalt extrahieren
#text = soup.get_text()

# Schritt 3: Text in Wörter zerlegen
#woerter = text.split()

# Funktion zur Prüfung auf GROSSWORT
#def ist_grosswort(wort):
#    return wort.isupper() and len(wort) > 2 and wort.isalpha()

# Schritt 4: Wörter filtern
#begriffe = set()
#for wort in woerter:
#    if ist_grosswort(wort):
#        begriffe.add(wort)

# Schritt 5: Alphabetisch sortieren und in Datei schreiben
#with open("begriffe.txt", "w", encoding="utf-8") as f:
#    for wort in sorted(begriffe):
#        f.write(wort + "\n")

#print(f"{len(begriffe)} Begriffe gespeichert.")
