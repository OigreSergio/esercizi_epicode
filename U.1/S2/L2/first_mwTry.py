import socket 
#importo libreria socket

SRV_ADDR = "0.0.0.0"
SRV_PORT= 44442

#   Creare connessione ipv4 (AF_INET) in tcp (SOCK_STREAM)
s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)

#   Istruzzioni all'avvio del programma , così che il sistema operativo usi SRV_ADDR & SRV_PORT 
s.bind((SRV_ADDR , SRV_PORT))

#   quando ti avvierai dovrai metterti in ascolto si una connessione 
s.listen(1)

#   prima di avviare va avvertito l'utente 
print("Sono in attesa")

#   ora mi metto effettivamente in attesa 
connection , adress = s.accept()

#   connessione avvenuta
print("Conected by : " , adress)

#   creazione ciclo infinito per gestire connessione 
while True:
    
    #   numero massimo di byte per volta (a meno che non prema invio)
    data = connection.recv(1024)

    #   se non ci sono dati interromi la connesione 
    if not data : break

    #se si vuole trasformare in una chat dando la possibilità di risposta 
    risp = input("Risposta : " )
    risp += "\n Sta a te :"
    
    connection.sendall(risp.encode())
    connection.sendall(b"Paket ricev")
    #   stampa l'input ricevuto convertendolo da byte a caratteri
    print(data.decode('utf-8'))

#   chiudo la connessione , fuori dal ciclo wile 
connection.close
