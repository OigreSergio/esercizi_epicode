import http.client

host = input("Inserire host oppure ip :")
port = input("inserire porta http : ")

if port == "":
    port = 80

try : 
    connection = http.client.HTTPConnection(host , port)

    connection.request('OPTIONS','/')

    response = connection.getresponse()

    print(response.getheaders())

except ConnectionAbortedError : 
    
    print ("Connessione rifiutata")