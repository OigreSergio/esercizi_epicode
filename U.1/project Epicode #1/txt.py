# socket è uno standard per le connessioni di rete a basso livello (socket TCP/UDP)
import socket# Questo modulo permette l'accesso alla rete https://docs.python.org/3/library/socket.html
# Modulo sys: fornisce accesso a funzioni e variabili dell'interprete (es. uscita dal programma)
import sys# Accesso al modulo sys per accedere alle variabili di sistema https://docs.python.org/3/library/sys.html
# Modulo per aprire URL e inviare richieste HTTP (usato per testare i metodi HTTP)
import urllib.request# Per operare con URL 'import urllib.' https://docs.python.org/3/library/urllib.request.html
# Per gestire eventuali errori HTTPError: (404, 405, 501, ...)
import urllib.error
# Import della classe datetime per misurare il tempo di esecuzione della scansione
from datetime import datetime #  https://docs.python.org/3/library/datetime.html
# Pool di thread: permette di eseguire più connessioni contemporaneamente
from concurrent.futures import ThreadPoolExecutor # https://docs.python.org/3/library/concurrent.futures.html


# Metodi HTTP : GET, POST, PUT, DELETE
# aggiungiamo HEAD, OPTIONS e PATCH per completezza
#GET - recupera dati 
#POST - invia o crea dati 
#PUT - sostituisce 
#DELETE - elimina 
#HEAD - recupera esclusivamente le intestazioni della risposta 
#OPTION - indica quali metodi supporta il server
# Lista dei metodi HTTP da testare su ogni porta aperta
METHODS = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"]



# Codici di risposta che indicano che il metodo NON è consentito dal server
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
        # connect_ex restituisce 0 se la connessione riesce, un codice di errore altrimenti
        result = s.connect_ex((target_ip, port))#Tentativo di connessione 
        s.close()#Chiude la connessione 
        # Se il risultato è 0 la connessione è riuscita, quindi la porta è aperta
        if result == 0:#Il primo if vorifica se la porta sia aperta 
            return port, True # Ritorna il numero della porta ed il fatto che sia aperta 
    except socket.error:#In caso di errore   
        # Errore di rete: si considera la porta chiusa e si prosegue
        pass#Passa alla prossima porta 
    # Porta chiusa o errore: restituisce la porta con esito False
    return port, False #Se la porta entrando nei ciclo if non risulta aperta verrà ritornata assieme al metodo in questo punto del codice 


def test_http_method(url: str, method: str) -> tuple[bool, int | str]:
    """Invia una richiesta HTTP con il metodo indicato."""

    # Crea la richiesta HTTP con l'URL e il metodo specificato 
    req = urllib.request.Request(url, method=method)
    try:
        # Invia la richiesta con il timeout impostato e restituisce (True, codice) se il server risponde con successo
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return True, resp.status
    except urllib.error.HTTPError as e:
        # Il server ha risposto con un errore
        return (e.code not in NOT_ALLOWED_CODES), e.code
    except urllib.error.URLError as e:
        # Errore di rete (host irraggiungibile, connessione rifiutata, timeout, ...)
        return False, f"errore di rete"
    except Exception as e:
        # Qualsiasi altro errore imprevisto
        return False, f"errore"

def check_http_on_port(target_ip, port):
    """Esegue il controllo dei metodi HTTP su una specifica porta aperta."""
    
    # Costruisce l'URL di base da testare sulla porta indicata
    url = f"http://{target_ip}:{port}/"
    print(f"\n[*] Analisi metodi HTTP su {url}...")
    
    # Lista che conterrà i metodi risultati abilitati
    allowed = []
    for method in METHODS:
        # Testa il singolo metodo e ottiene l'esito e il codice di risposta
        enabled, code = test_http_method(url, method)
        # Etichetta leggibile per l'output, con allineamento a colonne
        status = "ABILITATO" if enabled else "NON abilitato"
        print(f"    {method:<8} -> {status:<14} (risposta: {code})")
        if enabled:
            allowed.append(method)
    
    # Riepilogo finale: elenca i metodi abilitati oppure "nessuno"
    print(f"    -> Metodi HTTP abilitati: {', '.join(allowed) if allowed else 'nessuno'}")

def main():
    # Intestazione grafica del programma
    print("=" * 60)
    print("       NETWORK RECON: Port Scanner + HTTP Method Checker")
    print("=" * 60)

    # Input da utente
    # Richiede l'indirizzo IP da scansionare, rimuovendo eventuali spazi iniziali e finali
    target_ip = input("Inserisci l'indirizzo IP da scansionare (es. 192.168.50.1): ").strip()
    # Richiede il range di porte; se l'utente non inserisce numeri validi il programma termina
    try:
        start_port = int(input("Porta iniziale (es. 1): "))
        end_port = int(input("Porta finale (es. 1024): "))
    except ValueError:
        print("Errore: inserisci valori numerici validi per le porte.")
        return

    print("-" * 60)
    print(f"Scansione in corso sull'IP: {target_ip}")
    # Memorizza l'orario di inizio per calcolare la durata totale
    start_time = datetime.now()
    print(f"Orario di inizio: {start_time}")
    print("-" * 60)

    # Lista che conterrà le porte trovate aperte
    open_ports = []

    try:
        # Scansione porte con Multithreading (100 thread)
        max_threads = 100
        # Range delle porte da controllare (end_port è incluso grazie al +1)
        ports = range(start_port, end_port + 1)
        
        # Crea il pool di thread; alla fine del blocco "with" tutti i thread vengono chiusi
        with ThreadPoolExecutor(max_workers=max_threads) as executor:
            # Invia un task per ogni porta; il dizionario associa ogni future alla porta corrispondente
            futures = {executor.submit(scan_port, target_ip, port): port for port in ports}
            
            # Legge i risultati nell'ordine di invio; future.result() attende la fine del singolo task
            for future in futures:
                port, is_open = future.result()
                if is_open:
                    print(f"[+] Porta {port}: APERTA")
                    open_ports.append(port)

    except KeyboardInterrupt:
        # Gestisce l'interruzione da tastiera (Ctrl+C) uscendo in modo pulito
        print("\nScansione interrotta dall'utente.")
        sys.exit(0)
    except socket.gaierror:
        # Errore di risoluzione: l'IP o l'hostname inserito non è valido
        print("\nImpossibile risolvere l'hostname o l'IP.")
        sys.exit(1)

    # Memorizza l'orario di fine e calcola la durata della scansione
    end_time = datetime.now()
    print("-" * 60)
    print(f"Scansione porte completata in {end_time - start_time}")
    
    if open_ports:
        # Mostra le porte aperte in ordine crescente
        print(f"Porte aperte trovate: {sorted(open_ports)}")
        
        # Chiedi se analizzare i metodi HTTP sulle porte trovate
        # Accetta solo la risposta "s" (sì); qualsiasi altra risposta salta il test
        scelta = input("\nVuoi testare i metodi HTTP sulle porte aperte? (s/n): ").strip().lower()
        if scelta == 's':
            # Esegue il test dei metodi HTTP su ogni porta aperta, in ordine crescente
            for port in sorted(open_ports):
                # Filtriamo solitamente le porte web comuni o le testiamo tutte
                # (qui le testiamo tutte, il blocco try/except gestisce i servizi non HTTP)
                check_http_on_port(target_ip, port)
    else:
        print("Nessuna porta aperta trovata nel range specificato.")

    print("\nProcesso completato.")

# Esegue main() solo quando il file è lanciato direttamente
if __name__ == "__main__":
    main()