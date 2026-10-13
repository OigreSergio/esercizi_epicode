while True: #       avvio il ciclo wile True
    try: 
        #Per ottenere un valore in imput che sia un numero 
        
        exemple0_1 = int(input("Chose a Number, and i will tell you if is odd or not    ")) 
        #Inizzializzo la variabile 
        #così da poter ricevere un imput da verificare
        
        break 
    
    except ValueError: 
            # Per gestire eventuali input non validi 
            
            print("I can't rate it if it's not a number")
            #Risposta ad eventuali errori

if exemple0_1 % 2 == 0 : #      controllo che sia effettivamente pari
    print ("Is Even")#      print informativo se effettivamente è pari
else:
    print("Is odd") #       nel else metto l'opzione da stampare in caso il numero sia non pari

