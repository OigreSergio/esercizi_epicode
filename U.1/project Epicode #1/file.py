import socket# Questo modulo permette l'accesso alla rete https://docs.python.org/3/library/socket.html
import sys# Accesso al modulo sys per accedere alle variabili di sistema https://docs.python.org/3/library/sys.html
import urllib.request # Per operare con URL 'import urllib.' https://docs.python.org/3/library/urllib.request.html
# HTTPError: il server ha risposto ma con un codice di errore (404, 405, 501, ...)
import urllib.error
from datetime import datetime # Import della classe datetime per gestire date e orari https://docs.python.org/3/library/datetime.html
from concurrent.futures import ThreadPoolExecutor # Per gestire l'esecuzione parallela dei task https://docs.python.org/3/library/concurrent.futures.html
# Senza questo, testare 1024 porte una alla volta richiederebbe molto più tempo.

# Metodi HTTP : GET, POST, PUT, DELETE
# aggiungiamo HEAD, OPTIONS e PATCH per completezza
#GET - recupera dati 
#POST - invia o crea dati 
#PUT - sostituisce 
#DELETE - elimina 
#HEAD - recupera esclusivamente le intestazioni della risposta 
#OPTION - indica quali metodi supporta il server
METHODS = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"]
NOT_ALLOWED_CODES = {405, 501}
TIMEOUT = 3  # Timeout ridotto per velocità

 
#Metodo per eseguire la scansione delle porte
def scan_port(target_ip, port):
    """Verifica se una singola porta TCP è aperta."""
    # Metodo try , che va sempre gestito con almeno un exept 
    try:
        # Si crea l'oggetto s e gli si affida la connessione TCP/IP
        # AF_INET = IPV4
        # SOCKET_STREAM = TCP (connessione affidabile/con handshake)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.3)# Imposta il Timeout del Socket a 3 secondi 
        result = s.connect_ex((target_ip, port))#Tentativo di connessione 
        s.close()#Chiude la connessione 
        if result == 0:#Il primo if vorifica se la porta sia aperta 
            return port, True # Ritorna il numero della porta ed il fatto che sia aperta 
    except socket.error:#In caso di errore   
        pass#Passa alla prossima porta 
    return port, False #Se la porta entrando nei ciclo if non risulta aperta verrà ritornata assieme al metodo in questo punto del codice 
#Metodo che testa 
#def test_http_method(url: str, method: str) -> tuple[bool, int | str]:
#    """Invia una richiesta HTTP con il metodo indicato."""
#    req = urllib.request.Request(url, method=method)
#    try:
#        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
#            return True, resp.status
#    except urllib.error.HTTPError as e:
#    return (e.code not in NOT_ALLOWED_CODES), e.code
# except urllib.error.URLError as e:
#      return False, f"errore di rete"
#   except Exception as e:
#        return False, f"errore"
    
def test_method(url: str, method: str) -> tuple[bool, int | str]:
    """
    Invia una richiesta con il metodo indicato.
    Ritorna (abilitato, codice_risposta_o_errore).
    """
    req = urllib.request.Request(url, method=method)
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return True, resp.status
    except urllib.error.HTTPError as e:
        # 405 Method Not Allowed / 501 Not Implemented => metodo non abilitato
        return (e.code not in NOT_ALLOWED_CODES), e.code
    except urllib.error.URLError as e:
        return False, f"errore di rete: {e.reason}"
    except Exception as e:  # difesa finale per timeout o altri errori
        return False, f"errore: {e}"
 

def check_http_on_port(target_ip, port):
    """Esegue il controllo dei metodi HTTP su una specifica porta aperta."""
    # Proviamo prima con HTTP standard (se serve HTTPS si può estendere)
    url = f"http://{target_ip}:{port}/"
    test_http_method = url.index
    print(f"\n[*] Analisi metodi HTTP su {url}...")
    
    allowed = []
    for method in METHODS:
        enabled, code = test_http_method(url, method)
        status = "ABILITATO" if enabled else "NON abilitato"
        print(f"    {method:<8} -> {status:<14} (risposta: {code})")
        if enabled:
            allowed.append(method)
    
    print(f"    -> Metodi HTTP abilitati: {', '.join(allowed) if allowed else 'nessuno'}")

def main():
    print("=" * 60)
    print("       NETWORK RECON: Port Scanner + HTTP Method Checker")
    print("=" * 60)

    # Input da utente
    target_ip = input("Inserisci l'indirizzo IP da scansionare (es. 192.168.50.1): ").strip()
    try:
        start_port = int(input("Porta iniziale (es. 1): "))
        end_port = int(input("Porta finale (es. 1024): "))
    except ValueError:
        print("Errore: inserisci valori numerici validi per le porte.")
        return

    print("-" * 60)
    print(f"Scansione in corso sull'IP: {target_ip}")
    start_time = datetime.now()
    print(f"Orario di inizio: {start_time}")
    print("-" * 60)

    open_ports = []

    try:
        # Scansione porte con Multithreading (100 thread)
        max_threads = 100
        ports = range(start_port, end_port + 1)
        
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            futures = {executor.submit(scan_port, target_ip, port): port for port in ports}
            
            for future in futures:
                port, is_open = future.result()
                if is_open:
                    print(f"[+] Porta {port}: APERTA")
                    open_ports.append(port)

    except KeyboardInterrupt:
        print("\nScansione interrotta dall'utente.")
        sys.exit(0)
    except socket.gaierror:
        print("\nImpossibile risolvere l'hostname o l'IP.")
        sys.exit(1)

    end_time = datetime.now()
    print("-" * 60)
    print(f"Scansione porte completata in {end_time - start_time}")
    
    if open_ports:
        print(f"Porte aperte trovate: {sorted(open_ports)}")
        
        # Chiedi se analizzare i metodi HTTP sulle porte trovate
        scelta = input("\nVuoi testare i metodi HTTP sulle porte aperte? (s/n): ").strip().lower()
        if scelta == 's':
            for port in sorted(open_ports):
                # Filtriamo solitamente le porte web comuni o le testiamo tutte
                # (qui le testiamo tutte, il blocco try/except gestisce i servizi non HTTP)
                check_http_on_port(target_ip, port)
    else:
        print("Nessuna porta aperta trovata nel range specificato.")

    print("\nProcesso completato.")

if __name__ == "__main__":
    main()