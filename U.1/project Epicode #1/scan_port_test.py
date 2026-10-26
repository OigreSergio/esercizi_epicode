import socket
import errno
from datetime import datetime

# Input da utente
target_ip = input("Inserisci l'indirizzo IP da scansionare (es. 192.168.1.1): ")
start_port = int(input("Porta iniziale (es. 1): "))
end_port = int(input("Porta finale (es. 1024): ")) # Consigliato iniziare con un range più piccolo per i test

if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535) or start_port > end_port:
    print("Range di porte non valido: le porte devono essere tra 1 e 65535 e la iniziale non può superare la finale.")
    raise SystemExit(1)


def method(code: int) -> str:
    """Traduce il codice restituito da connect_ex nello stato della porta."""
    if code == 0:
        return "APERTA"
    if code == errno.ECONNREFUSED:
        return "CHIUSA"
    if code in (errno.ETIMEDOUT, errno.EAGAIN, errno.EWOULDBLOCK, errno.EINPROGRESS):
        return "FILTRATA"
    if code in (errno.EHOSTUNREACH, errno.ENETUNREACH):
        return "HOST NON RAGGIUNGIBILE"
    return f"ERRORE ({code})"


print("-" * 50)
print(f"Scansione in corso sull'IP: {target_ip}")
print(f"Orario di inizio: {datetime.now()}")
print("-" * 50)

# Risoluzione dell'hostname una sola volta, prima del ciclo
try:
    ip = socket.gethostbyname(target_ip)
except socket.gaierror:
    print("\nImpossibile risolvere l'hostname o l'IP.")
    raise SystemExit(1)

porte_aperte = []
porte_filtrate = []

try:
    for port in range(start_port, end_port + 1):
        # Creazione del socket TCP, chiuso automaticamente a fine blocco
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.3)  # Timeout ridotto per velocizzare

            # Tentativo di connessione alla porta
            result = s.connect_ex((ip, port))
            stato = method(result)

        if stato == "APERTA":
            print(f"[+] Porta {port}: APERTA")
            porte_aperte.append(port)
        else:
            print(f"[-] Porta {port}: {stato}")
            if stato == "FILTRATA":
                porte_filtrate.append(port)

except KeyboardInterrupt:
    print("\nScansione interrotta dall'utente.")

print("-" * 50)
print(f"Porte aperte:    {porte_aperte if porte_aperte else 'nessuna'}")
print(f"Porte filtrate:  {len(porte_filtrate)}")
print("-" * 50)
print("\nScansione completata.")