from http.server import HTTPServer, BaseHTTPRequestHandler
import sys


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)

        print("Received POST request:")
        print(post_data.decode('utf-8'))

        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b"{\"message\": \"Message Received\"}")


def run_server(port=9888):
    server_address = ('', port)
    httpd = HTTPServer(server_address, RequestHandler)
    print(f"Server running on port {port}")
    httpd.serve_forever()


if __name__ == '__main__':
    port = 9888
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    run_server(port)
