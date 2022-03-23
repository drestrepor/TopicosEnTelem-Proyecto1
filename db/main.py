from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import const
import os.path
import json

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

class DBServer(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        path = url.path
        query = parse_qs(url.query)

        for k in query.keys(): # Query string values can be lists. We get the first value only
            query[k] = query[k][0]

        #
        # code: 200
        # Connection stablished.
        #
        if (path == ''):
            res = { "response": { "code": 200, "message": "Connected" } }
            response(self, 200, res)

        #
        # code: 200
        # Data from file (also []).
        #
        elif (path == '/phones/show'):
            if len(query) < 1 or not ('key' in query):
                res = { "error": { "code": 400, "message": "Missing [key] in query" } }
                response(self,400,res)
                return

            # Open file to read
            f = open('db.txt', 'r')
            
            # List keys
            database = json.load(f) 
            values = [d['value'] for d in database if d['key'] == query['key']]
            
            # Send response
            res = { "data": values }
            response(self, 200, res)

        #
        # code: 404
        # Resource not found.
        #
        else:
            res = { "error": { "code": 404, "message": "Resource not found" } }
            response(self, 404, res)

    def do_POST(self):
        path = get_path(self)
        
        #
        # code: 201
        # Data added.
        #
        # code: 404
        # Bad format for JSON.
        #
        if (path == '/phones/create'):
            # Get body
            length = int(self.headers.get('content-length'))
            field_data = self.rfile.read(length)
            try:
                entry = json.loads(field_data.decode('utf-8'))
            except:
                res = { "error": { "code": 404, "message": "Bad format for JSON" } }
                response(self, 404, res)
                return

            # Create db.txt if it is not exists
            if not os.path.exists('./db.txt'):
                f = open('db.txt', 'x')
                f.write('[]')
                f.close()
            
            # Get JSON in file to append entries
            f = open('db.txt', 'r')
            data = json.load(f)
            if isinstance(entry, list):
                data.append([e for e in entry])
            else:
                data.append(entry)
            
            # Set JSON
            f = open('db.txt', 'w')
            json.dump(data, f)
            f.close()

            res = { "data": data }
            response(self, 201, res)

        elif (path == '/phones/delete'):
            # Get body
            length = int(self.headers.get('content-length'))
            field_data = self.rfile.read(length)
            try:
                entry = json.loads(field_data.decode('utf-8'))
            except:
                res = { "error": { "code": 404, "message": "Bad format for JSON" } }
                response(self, 404, res)
                return

            # Create db.txt if it is not exists
            if not os.path.exists('./db.txt'):
                f = open('db.txt', 'x')
                f.write('[]')
                f.close()
            
            # Get JSON in file to append entries
            f = open('db.txt', 'r')
            database = json.load(f)
            deleted = [d for d in database if d['key'] == entry['key']]
            data = [d for d in database if d['key'] != entry['key']]
            
            # Set JSON
            f = open('db.txt', 'w')
            json.dump(data, f)
            f.close()

            if len(deleted) == 0:
                res = { "error": { "code": 404, "message": "Key not found" } }
                response(self, 404, res)
                return

            res = { "data": deleted }
            response(self, 200, res)
        
        #
        # code: 404
        # Resource not found.
        #
        else:
            res = { "error": { "code": 404, "message": "Resource not found" } }
            response(self, 404, res)


if __name__ == "__main__":
    webServer = HTTPServer((const.IP_SERVER, const.PORT), DBServer)
    print("Server started http://%s:%s" % (const.IP_SERVER, const.PORT))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.\n")