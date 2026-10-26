import socket
from datetime import datetime

# Input da utente
target_ip = input("Inserisci l'indirizzo IP da scansionare (es. 192.168.50.101): ")
start_port = int(input("Porta iniziale (es. 1): "))
end_port = int(input("Porta finale (es. 1024): "))

print("-" * 50)
print(f"Scansione in corso sull'IP: {target_ip}")
print(f"Orario di inizio: {datetime.now()}")
print("-" * 50)

try:
    for port in range(start_port, end_port + 1):
        # Creazione del socket TCP
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)  # Imposta un timeout breve per velocizzare la scansione
        
        # Tentativo di connessione alla porta
        result = s.connect_ex((target_ip, port))
        
        if result == 0:
            print(f"[+] Porta {port}: APERTA")
            
        s.close()

except KeyboardInterrupt:
    print("\nScansione interrotta dall'utente.")
except socket.gaierror:
    print("\nImpossibile risolvere l'hostname o l'IP.")
except socket.error:
    print("\nImpossibile connettersi al server.")

print("\nScansione completata.")