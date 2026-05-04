#Musterlösungen Sitzung Programmieren II
#Zum Aktivieren des gewünschten Codeteils, diesen einkommentieren (# vor der Zeile entfernen).
#Übung Listen:

#leaders_1916 = ["Pearse", "Connolly", "Markievicz"]


#print(leaders_1916[1])
#print(len(leaders_1916))

#leaders_1916.append("MacBride")

#print(f"In der Liste sind {len(leaders_1916)} Einträge und die Einträge lauten nun: {leaders_1916}")

#Übung Bedingungen:
#rollen = ["Aktivistin", "Lehrer", "Poet", "Aktivistin"]

#if rollen[0] == "Aktivistin":
#    print("Politisch engagiert.")
#else:
#    print("Andere Rolle.")

#if rollen[1] == "Aktivistin":
#    print("Politisch engagiert.")
#else:
#    print("Andere Rolle.")

#if rollen[2] == "Aktivistin":
#    print("Politisch engagiert.")
#else:
#    print("Andere Rolle.")

#if rollen[3] == "Aktivistin":
#    print("Politisch engagiert.")
#else:
#    print("Andere Rolle.")

#Bonus: "Aktivist"
#rollen = ["Aktivistin", "Lehrer", "Poet", "Aktivist"]

#if rollen[0] == "Aktivistin" or rollen[0] == "Aktivist":
#    print("Politisch engagiert.")
#else:
#    print("Andere Rolle.")

#if rollen[1] == "Aktivistin" or rollen[1] == "Aktivist":
#    print("Politisch engagiert.")
#else:
#    print("Andere Rolle.")

#if rollen[2] == "Aktivistin" or rollen[2] == "Aktivist":
#    print("Politisch engagiert.")
#else:
#    print("Andere Rolle.")

#if rollen[3] == "Aktivistin" or rollen[3] == "Aktivist":
#    print("Politisch engagiert.")
#else:
#    print("Andere Rolle.")

#Übung while
#leicht
#zahl = 1

#while zahl <= 5:
#    print(zahl)
#    zahl += 1

#input
#antwort = ""

#while antwort != "Patrick Pearse":
#    antwort = input("Wer war der Anführer beim Osteraufstand? ")
#print("Richtig!")


#error handling
#try:
#    zahl = int(input("Bitte eine Zahl eingeben: "))
#except ValueError:
#    print("Das war keine gültige Zahl.")
#    zahl = int(input("Bitte eine Zahl eingeben: "))

#Rebellenliste
#namen = []
#eingabe = ""

#while eingabe != "stop":
#    try:
#        eingabe = input("Nenne eine historische Person des Osteraufstands:")

#        if eingabe == "":
#            print("Die Eingabe war leer")
#            continue #Schleife überspringt den Rest. nochmals eingabe = input("Nenne eine historische Person des Osteraufstands:") wäre auch möglich.

#        if eingabe != "stop":
#            namen.append(eingabe)

#            if eingabe == "Constance Markievicz":
#                print("Politisch engagierte Frau erkannt.")

#    except Exception as e:
#        print("Es ist ein Fehler aufgetreten:", e)

#print(f"Es wurden {len(namen)} Personen eingetragen.")

#if "Patrick Pearse" in namen:
#    print("Patrick Pearse war dabei.")
#else:
#    print("Patrick Pearse wurde nicht genannt.")



