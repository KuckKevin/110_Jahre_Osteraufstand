is_it_raining = False				        #Deklaration einer Boolean
is_it_warm = False 					        #Deklaration einer zweiten Boolean
Weather = ""						        #Deklaration eines leeren Strings
Temp = "Temperatur: "					    #Deklaration eines Strings mit Inhalt
Temp_Soll = 20						        #Deklaration eines Integers
Temp_Ist = 34.5						        #Deklaration eines Floats
Temp_Diff = 0						        #Deklaration einer weiteren Zahl (Int.)

if is_it_raining == False:                  #Abfrage zum Zustand der Boolean
    Weather = "Es regnet nicht"             #Regnet es nicht, bekommt Weather Inhalt
    print(Weather)                          #Inhalt der Variable wird ausgegeben

if Temp_Ist > Temp_Soll:                    #Vergleich, ob Variable 1 größer als Var. 2 ist
    is_it_warm = True                       #Falls ja, bekommt ist die boolean Var “True”

if is_it_warm == True:						#Abfrage zum Zustand der Boolean
    print(str(Temp) + str(Temp_Ist))		#Ausgabe eines kombinierten Strings
    Temp_Diff = float (Temp_Ist - Temp_Soll)#Unterschied ausrechnen als Float
    print(Temp_Diff)						#Ausgabe des Unterschieds
else:										#Alternative falls “False”
    print(str(Temp) + str(Temp_Ist))		#Ausgabe eines kombinierten Strings
