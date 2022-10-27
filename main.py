from socket import *

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


if __name__ == "__main__":
    serverSocket = socket(AF_INET, SOCK_STREAM)

    serverSocket.bind(('', 8080))
    serverSocket.listen(1)

    while True:
        print("Server is running")
        clientSocket, addr = serverSocket.accept()
        print(clientSocket)
        print(addr)
        try:
            message = clientSocket.recv(1024)
            # check if client suddenly disconnected
            if message.decode('utf-8') == '':
                clientSocket.close()
                continue

            method = message.split()[0].decode('utf-8').strip("/")
            er401Data = "<!DOCTYPE html><html><head><title> 401 Unauthorized </title></head><body><h1>401 Unauthorized</h1><p>This is a private area. </p></body></html>"
            er404Data = "<!DOCTYPE html><html><head><title> 404 Not Found </title></head><body><h1>404</h1><p> The requested file cannot be found. </p></body></html>"
            sendData=""
            # The path
            path = message.split()[1].decode('utf-8').strip("/")
            contentType=''
            if(method == "GET"):
                # Turn to index.html
                if(path == '' or path == "index" or path == "index.html"):
                    path = ".html"
                # Return error 401 for image.html if client send GET method which means there are not username password
                elif(path == "images.html"):
                    clientSocket.send(('HTTP/1.0 401 Unauthorized\r\nContent-Type: text/html\r\nContent-Length:' + str(len(er401Data)) + '\r\n\r\n' + er401Data).encode())
                    clientSocket.close()
                    continue  
                #Get date and send to server, do if the path is right, return error if the path is wrong
                try:
                    if(path.endswith(".png") or path.endswith(".jpg")):
                        f = open("src/"+path, 'rb')
                    else:
                        f = open("src/"+path, errors="ignore")
                    sendData = f.read()
                    f.close()
                    contentType = getType(path)
                    rpHeader='HTTP/1.0 200 OK\r\nContent-Type: '+ contentType +'\r\nContent-Length:' + str(len(sendData)) + '\r\n\r\n'
                    clientSocket.send(rpHeader.encode())
                    if(path.endswith(".png") or path.endswith(".jpg")):
                        clientSocket.sendall(sendData)
                    else:
                        clientSocket.sendall(sendData.encode())
                    clientSocket.close()
                except IOError: # which means no such file in server
                    clientSocket.send(('HTTP/1.0 404 Not Found\r\nContent-Type: text/html\r\nContent-Length:' + str(len(er404Data)) + '\r\n\r\n' + er404Data).encode())
                    clientSocket.close()
            elif (method == "POST"):
                userName = message.split()[-1].decode('utf-8').split("&")[0].split("=")[1]
                password = message.split()[-1].decode('utf-8').split("&")[1].split("=")[1]

                if (userName != "admin" or password !="123456"):
                    clientSocket.send(('HTTP/1.0 401 Unauthorized\r\nContent-Type: text/html\r\nContent-Length:' + str(len(er401Data)) + '\r\n\r\n' + er401Data).encode())
                    clientSocket.close() 
                    continue

                if(path.endswith(".png") or path.endswith(".jpg")):
                    f = open("src/"+path, 'rb')
                else:
                    f = open("src/"+path, errors="ignore")
                sendData = f.read()
                f.close()

                contentType = getType(path)

                rpHeader='HTTP/1.0 200 OK\r\nContent-Type: '+ contentType +'\r\nContent-Length:' + str(len(sendData)) + '\r\n\r\n'
                clientSocket.send(rpHeader.encode())
                if(path.endswith(".png") or path.endswith(".jpg")):
                    clientSocket.sendall(sendData)
                else:
                    clientSocket.sendall(sendData.encode())
                clientSocket.close()
        except Exception:
            er503Data = "<!DOCTYPE html><html><head><title> 503 Service Unavailabl </title></head><body><h1>503 Service Unavailable</h1><p>Something wrong at host server. </p></body></html>"
            clientSocket.send(('HTTP/1.0 503 Service Unavailable\r\nContent-Type: text/html\r\nContent-Length:' + str(len(er503Data)) + '\r\n\r\n' + er503Data).encode())
            serverSocket.close() 
    
    
