import socket 

#   per riceve l'indirizzo da scansionare
target = input("IP ds scsnnrrizzare : ")
#   inizio e fine delle porte 
porta = input("forniscimi la porte da scansire : ")

#stampo le porte
#print(porta.split('-'))

#   mi ricavo le porte della risposta utente 
lowport , highport = porta.split('-') 

#   sfrutto il functional per printare i risultati 
print(f"Sto scansendo il {target} dalla porta {lowport} alla porta {highport}")

fallite = []
for port in range(int(lowport) ,int(highport)+1):
    #   configuarazione connessione ipv4 tcp
    s = socket.socket(socket.AF_INET , socket.SOCK_STREAM)
    status = s.connect_ex((target , port))
    if status == 0 : 
        print (f"Connessione alla {port} ha avuto sucesso")
    else :
        fallite.append(port)
        
        #chiusura socet 
        s.close()

print(f"Connessione non riuscita con la port : {port}")
    