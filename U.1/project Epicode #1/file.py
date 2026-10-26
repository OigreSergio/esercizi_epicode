 
import sys
import urllib.request
import urllib.error
 
# Metodi da testare (come richiesto dalla traccia: GET, POST, PUT, DELETE;
# aggiungiamo HEAD, OPTIONS e PATCH per completezza)
METHODS = ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS", "PATCH"]
 
# Codici che indicano che il metodo NON è abilitato
NOT_ALLOWED_CODES = {405, 501}
 
TIMEOUT = 5  # secondi
 
 
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
 
 
def enabled_methods(url: str) -> dict[str, int | str]:
    """Ritorna un dizionario metodo -> codice/errore, per tutti i metodi testati."""
    results = {}
    for method in METHODS:
        enabled, code = test_method(url, method)
        results[method] = code
        results[f"{method}_enabled"] = enabled
    return results
 
 
def main() -> None:
    if len(sys.argv) != 2:
        print("Uso: python3 http_methods.py <url>")
        print("Esempio: python3 http_methods.py http://192.168.50.101/phpmyadmin/")
        sys.exit(1)
 
    url = sys.argv[1]
    print(f"Verifica dei metodi HTTP su: {url}\n")
 
    allowed = []
    for method in METHODS:
        enabled, code = test_method(url, method)
        status = "ABILITATO" if enabled else "NON abilitato"
        print(f"  {method:<8} -> {status:<14} (risposta: {code})")
        if enabled:
            allowed.append(method)
 
    print("\nMetodi abilitati:", ", ".join(allowed) if allowed else "nessuno")
 
 
if __name__ == "__main__":
    main()