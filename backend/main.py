from encodings import utf_8
from http.server import HTTPServer, BaseHTTPRequestHandler
from multiprocessing.sharedctypes import Value
from urllib.parse import urlparse, parse_qs
import const
import requests
import json
from random import randint

def to_string(dict):
    return str(dict).replace("'", '"')

def response(server, code, response):
    server.send_response(code)
    server.send_header("content-type", "application/json")
    server.end_headers()
    server.wfile.write(bytes(to_string(response), 'utf-8'))  

def get_path(server):
    url = urlparse(server.path)
    path = url.path
    path = path[:-1] if path[-1] == '/' else path
    return path


class BackendServer(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        path = url.path
        query = parse_qs(url.query)

        for k in query.keys(): # Query string values can be lists. We get the first value only
            query[k] = query[k][0]


        if (path == '/phones/show'):
            # Check parameters
            if not 'key' in query:
                res = { "error": { "code": 400, "message": "Missing [key] in query" } }
                response(self, 400, res)
                return
            
            else:
                # Get parameters
                key = query['key']

                # Requests for DB Server
                try:

                    for ip in const.DB_URL:
                        r = requests.get(
                            f'{ip}/phones/show?key={key}'
                        )

                    res = { "data": json.loads(r.text)['data'] }
                    response(self, 202, res) 
                except requests.exceptions.RequestException as e:
                    res = { "error": { "code": 500, "message": "Internal Error: DB Server Connection Refused" } }
                    response(self, 500, res)


    def do_POST(self):
        path = get_path(self)
        
        #
        # code: 400
        # For any missing parameter.
        #
        # code: 202
        # Data to add sent to DB Server.
        #
        # code: 500
        # DB Server Connection refused.
        #
        if (path == '/phones/create'):
            # Get body
            length = int(self.headers.get('content-length'))
            field_data = self.rfile.read(length)
            
            # Get body JSON
            try:
                body = json.loads(field_data.decode('utf-8'))
            except:
                res = { "error": { "code": 400, "message": "Bad format for JSON" } }
                response(self, 400, res)
                return

            # Check parameters
            if not 'key' in body:
                res = { "error": { "code": 400, "message": "Missing [key] in body" } }
                response(self, 400, res)
                return
            
            elif not 'value' in body:
                res = { "error": { "code": 400, "message": "Missing [value] in body" } }
                response(self, 400, res)
                return
            
            else:
                # Get parameters
                key = body['key']
                value = body['value']

                # Requests for DB Server
                try:
                    random = 0
                    url = const.DB_URL[random]
                    
                    data = json.dumps({ 'key': key, 'value': value })

                    r = requests.post(
                        f'{url}/phones/create',
                        data=data,
                        headers={ 'content-type': 'application/json' }
                    )

                    res = { "status": { "code": 202, "message": "Accepted" } }
                    response(self, 202, res) 
                except requests.exceptions.RequestException as e:
                    res = { "error": { "code": 500, "message": "Internal Error: DB Server Connection Refused" } }
                    response(self, 500, res)


        elif (path == '/phones/delete'):
            # Get body
            length = int(self.headers.get('content-length'))
            field_data = self.rfile.read(length)
            
            # Get body JSON
            try:
                body = json.loads(field_data.decode('utf-8'))
            except:
                res = { "error": { "code": 400, "message": "Bad format for JSON" } }
                response(self, 400, res)
                return

            # Check parameters
            if not 'key' in body:
                res = { "error": { "code": 400, "message": "Missing [key] in body" } }
                response(self, 400, res)
                return
            
            else:
                # Get parameters
                key = body['key']

                # Requests for DB Server
                try:
                    
                    data = json.dumps({ 'key': key })

                    for ip in const.DB_URL:
                        r = requests.post(
                            f'{ip}/phones/delete',
                            data=data,
                            headers={ 'content-type': 'application/json' }
                        )

                    res = { "status": { "code": 202, "message": "Accepted" } }
                    response(self, 202, res) 
                except requests.exceptions.RequestException as e:
                    res = { "error": { "code": 500, "message": "Internal Error: DB Server Connection Refused" } }
                    response(self, 500, res)       
        #
        # code: 404
        # Resource not found.
        #
        else:
            res = { "error": { "code": 404, "message": "Resource not found" } }
            response(self, 404, res)


    
    


if __name__ == "__main__":
    webServer = HTTPServer((const.HOST, const.PORT), BackendServer)
    print("Server started http://%s:%s" % (const.HOST, const.PORT))
    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")