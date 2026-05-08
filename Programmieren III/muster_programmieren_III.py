#Musterlösungen Sitzung Programmieren III
#Zum Aktivieren des gewünschten Codeteils, diesen einkommentieren (# vor der Zeile entfernen).
#Dateien
#with open("beispiel.txt", "w") as f:
#    f.write("Hallo Welt!")

#with open("namen.txt", "w") as f:
#    f.write("Anna\n")
#    f.write("Ben\n")

#with open("namen.txt", "r") as f:
#    zeilen = f.readlines()   # Liste aller Zeilen
#print(zeilen)

#with open("namen.txt", "r") as f:
#    inhalt = f.read()        # Ganze Datei als ein String
#print(inhalt)


#Übung Datei öffnen, lesen, schreiben
#Erstelle drei Variablen mit Namen von Personen aus dem Osteraufstand.
#Schreibe alle drei Namen in eine Datei namens namen.txt, jeweils in eine neue Zeile.
#Lies die Datei wieder ein und gib die ersten beiden Zeilen mit print() aus.
#Tipps:
#Verwende zum Schreiben: open("namen.txt", "w")
#Zum Lesen: open("namen.txt", "r")
#Zum Ausgeben: print() mit direktem Zugriff über zeilen[0], zeilen[1]

#Lösung:
# Schritt 1: Drei Namen als Variablen
#name1 = "Patrick Pearse"
#name2 = "James Connolly"
#name3 = "Constance Markievicz"

# Schritt 2: In Datei schreiben
#with open("namen.txt", "w") as f:
#    f.write(name1 + "\n")
#    f.write(name2 + "\n")
#    f.write(name3 + "\n")

# Schritt 3: Datei lesen
#with open("namen.txt", "r") as f:
#    zeilen = f.readlines()

# Schritt 4: Zwei Zeilen ausgeben
#print("Erste Zeile:", zeilen[0].strip())
#print("Zweite Zeile:", zeilen[1].strip())




#Übungen & Beispiele for Schleife
#namen = ["Patrick", "Constance", "James"]

#for name in namen:
#    print("Name:", name)

#for i in range(5):
#    print(i)

#Übung for Schleife und Liste
#Gegeben ist eine Liste mit historischen Namen aus dem Osteraufstand 1916.
#Schreibt ein Programm, das jeden Namen in der Liste ausgibt – zusammen mit der Ausgabe "war am Aufstand beteiligt".

#personen = ["Patrick Pearse", "Constance Markievicz", "James Connolly"]

#for person in personen:
#   print(f"{person} war am Aufstand beteiligt.")
    #alternativ:
    #print(person, "war am Aufstand beteiligt.")

#Übung for Schleife und range
#Schreibe ein Programm, das die Jahre von 1913 bis 1916 mit for und range() durchläuft und jeweils ausgibt: "Jahr: XXXX".
#Tipp: Die range()-Funktion schließt das Ende standardmäßig nicht ein – also range(1913, 1917)
#for Jahr in range(1913, 1917):
#    print("Jahr:", Jahr)
    #alternativ:
    #print(f"Jahr: {Jahr}")

#Bibliotheken
#Beispiel import statement
#import math
#wurzel = math.sqrt(16)
#print(f"Die Wurzel aus 16 ist {wurzel}.")

#requests Webseiten aufrufen
#import requests
#response = requests.get("https://www.uni-heidelberg.de/fakultaeten/philosophie/zegk/histsem/index.html")
#print(response.status_code) #200 heißt OK. Der Server hat die Anfrage verstanden
#print(response.text[:200])     # zeigt die ersten 200 Zeichen HTML

#BeautifulSoup HTML auslesen
#from bs4 import BeautifulSoup

#einfaches HTML-Beispiel (normalerweise werden Webseiten verwendet)
#html = "<html><body><h1>Hallo</h1></body></html>"
#Verarbeitung mit BeautifulSoup
#soup = BeautifulSoup(html, "html.parser")
#Ausgabe
#print(soup.h1.text)  # gibt "Hallo" aus

#übung requests
#Teil 1
#import requests
#response = requests.get("https://www.hist.uni-heidelberg.de/de/seminarbibliothek")
#print(response.status_code)

#Teil 2
#import requests
#Der Fehler in der URL, der zum Code 404 fehlt, ist der fehlende - .
#response = requests.get("https://www.hist.uni-heidelberg.de/de/seminar-bibliothek")
#print(response.status_code)
#content_HistSem = response.text[:500]     # Speichert die ersten 500 Zeichen HTML in einer Variabel
#print(content_HistSem)

#with open("HistSem.txt", "w") as f: # Schreibt die 500 Zeichen in eine txt-Datei
#    f.write(content_HistSem)

#übung BeautifulSoup
#Verwende BeautifulSoup, um den ersten Eintrag um aus dem <div class="Description_s73Mi">
#den Text zur “Geschichte des Seminars” zu scrapen.
#url = "https://www.hist.uni-heidelberg.de/de/seminar-bibliothek"
#Bonus: Schreibe das Gefundene in eine Datei (Geschichte.txt)

#import requests
#from bs4 import BeautifulSoup

# Schritt 1: Webseite abrufen
#url = "https://www.hist.uni-heidelberg.de/de/seminar-bibliothek"
#response = requests.get(url)
#soup = BeautifulSoup(response.text, "html.parser")

# Schritt 2: Relevanten Bereich finden
#eintrag = soup.find("div", class_="Description_s73Mi")

# Schritt 3: Text ausgeben oder Fehlermeldung anzeigen
#if eintrag:
#    text = eintrag.get_text(" ", strip=True)
#    print(text)
    #Bonus:
#    with open("Geschichte.txt", "a") as f:
#        f.write(text)
#else:
#    print("Text nicht gefunden.")

#Aufgabe BeautifulSoup Mitteilungen
#URL: https://www.hist.uni-heidelberg.de/de
#Verwende BeautifulSoup, um die Überschriften
#dieser Reihe an Mitteilungen einzusammeln:
#Tipp: Die “Links” befinden sich in einem nichtsichtbaren H2-Element
#soup.find() kann auch mit string=”” filtern

#import requests
#from bs4 import BeautifulSoup

#url = "https://www.uni-heidelberg.de/fakultaeten/philosophie/zegk/histsem/index.html"

#response = requests.get(url)
#soup = BeautifulSoup(response.text, "html.parser")

# Section finden, die die Überschrift "Links" enthält
#links_heading = soup.find("h2", string="Links")

#if links_heading:
#    section = links_heading.find_parent("div")

#    h3_elements = section.find_all("h3")

#    if h3_elements:
#        print("Gefundene Überschriften:")
#        for h3 in h3_elements:
#            print(h3.get_text(strip=True))
#    else:
#        print("Keine h3-Elemente in der Links-Sektion gefunden.")
#else:
#    print("Links-Sektion nicht gefunden.")