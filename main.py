from socket import *
from threading import Thread

def getType(path):
    contentType=""
    if(path.endswith(".jpg")):
        contentType = 'image/jpg'
    elif(path.endswith(".css")):
        contentType = 'text/css'
    elif(path.endswith(".png")):
        contentType = 'image/png'
    else:
        contentType = 'text/html'
    return contentType
   

def acceptConnections():
    while True:
        clientSocket, addr = server.accept()
        print("Connected to a client")
        Thread(target=handleClient, args=(clientSocket,addr)).start()

def handleClient(clientSocket, addr):
    er401Data = "<!DOCTYPE html><html><head><title> 401 Unauthorized </title></head><body><h1>401 Unauthorized</h1><p>This is a private area. </p></body></html>"
    er404Data = "<!DOCTYPE html><html><head><title> 404 Not Found </title></head><body><h1>404</h1><p> The requested file cannot be found. </p></body></html>"
    sendData=""
    while True:
        message = clientSocket.recv(1024)
        # check if client suddenly disconnected
        if message.decode('utf-8') == '':
            print("Disconnected to a client")
            clientSocket.close()
            break
        try:
            method = message.split()[0].decode('utf-8').strip("/")
            # The path
            path = message.split()[1].decode('utf-8').strip("/")
            contentType=''
            # Turn to index.html
            if(path == '' or path == "index" or path == "index.html"):
                path = ".html"
            if(method == "GET"):
                # Return error 401 for image.html if client send GET method which means there are not username password
                if(path == "images.html"):
                    clientSocket.send(('HTTP/1.0 401 Unauthorized\r\nConnection: keep-alive\r\nContent-Type: text/html\r\nContent-Length:' + str(len(er401Data)) + '\r\n\r\n' + er401Data).encode())
                    continue  
                #Read data
                try:
                    if(path.endswith(".png") or path.endswith(".jpg")):
                        f = open("src/"+path, 'rb')
                    else:
                        f = open("src/"+path, errors="ignore")
                    sendData = f.read()
                    f.close()
                    
                    contentType = getType(path)
                    rpHeader='HTTP/1.0 200 OK\r\nConnection: keep-alive\r\nContent-Type: '+ contentType +'\r\nContent-Length:' + str(len(sendData)) + '\r\n\r\n'
                    clientSocket.send(rpHeader.encode())
                    if(path.endswith(".png") or path.endswith(".jpg")):
                        clientSocket.send(sendData)
                    else:
                        clientSocket.send(sendData.encode())
                except IOError: # which means no such file in server
                    clientSocket.send(('HTTP/1.0 404 Not Found\r\nConnection: keep-alive\r\nContent-Type:  '+ contentType +'\r\nContent-Length:' + str(len(er404Data)) + '\r\n\r\n' + er404Data).encode())
            elif (method == "POST"):
                userName = message.split()[-1].decode('utf-8').split("&")[0].split("=")[1]
                password = message.split()[-1].decode('utf-8').split("&")[1].split("=")[1]
                if (userName != "admin" or password !="123456"):
                    clientSocket.send(('HTTP/1.0 401 Unauthorized\r\nConnection: keep-alive\r\nContent-Type: text/html\r\nContent-Length:' + str(len(er401Data)) + '\r\n\r\n' + er401Data).encode())
                    continue
                try:
                    f = open("src/"+path, errors="ignore")
                    sendData = f.read()
                    f.close()
                    contentType = getType(path)
                    rpHeader='HTTP/1.0 200 OK\r\nConnection: keep-alive\r\nContent-Type: '+ contentType +'\r\nContent-Length:' + str(len(sendData)) + '\r\n\r\n'
                    clientSocket.send((rpHeader+sendData).encode())
                except IOError: # which means no such file in server
                    clientSocket.send(('HTTP/1.0 404 Not Found\r\nConnection: keep-alive\r\nContent-Type: text/html\r\nContent-Length:' + str(len(er404Data)) + '\r\n\r\n' + er404Data).encode())
            
            print(addr)
            print("Method: " + method, "\t Type: " +contentType, "\t Path: "+ path)
        except Exception:
            continue


if __name__ == "__main__":
    server = socket(AF_INET, SOCK_STREAM)

    server.bind(('', 8080))
    
    print("Server started")
    print("Waiting for client request...")
    server.listen()
    ACCEPT_THREAD = Thread(target=acceptConnections)
    
    ACCEPT_THREAD.start()
    ACCEPT_THREAD.join()
    server.close()
