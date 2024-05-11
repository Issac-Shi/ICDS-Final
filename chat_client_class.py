import time
import socket
import select
import sys
import json
from chat_utils import *
from GUI import *
import client_state_machine as csm
from cryptography.hazmat.primitives.asymmetric import dh
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import threading

class Client:
    def __init__(self, args):
        self.peer = ''
        self.console_input = []
        self.state = S_OFFLINE
        self.system_msg = ''
        self.local_msg = ''
        self.peer_msg = ''
        self.args = args
        self.dh_params = dh.generate_parameters(generator=2, key_size=2048, backend=default_backend())
        self.private_key = self.dh_params.generate_private_key()
        self.public_key = self.private_key.public_key()
        self.server_public_key = None
        self.shared_key = None

    def quit(self):
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()

    def send_public_key(self):
        public_key_bytes = self.public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
        msg = json.dumps({"action":"public_key", "public_key":public_key_bytes.decode()})
        self.send(msg)

    def recv_public_key(self):
        response = json.loads(self.recv())
        self.server_public_key = serialization.load_pem_public_key(response["public_key"].encode(), default_backend())

    def generate_shared_key(self):
        shared_key = self.private_key.exchange(self.server_public_key)
        self.shared_key = shared_key
    
    def get_name(self):
        return self.name

    def init_chat(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM )
        svr = SERVER if self.args.d == None else (self.args.d, CHAT_PORT)
        self.socket.connect(svr)
        self.sm = csm.ClientSM(self.socket)
        self.gui = GUI(self.send, self.recv, self.sm, self.socket)
        reading_thread = threading.Thread(target=self.read_input)
        reading_thread.daemon = True
        reading_thread.start()

    def shutdown_chat(self):
        return

    def send(self, msg):
        mysend(self.socket, msg)

    def recv(self):
        return myrecv(self.socket)

    def get_msgs(self):
        read, write, error = select.select([self.socket], [], [], 0)
        my_msg = ''
        peer_msg = []
        if len(self.console_input) > 0:
            my_msg = self.console_input.pop(0)
        if self.socket in read:
            peer_msg = self.recv()
        return my_msg, peer_msg

    def output(self):
        if len(self.system_msg) > 0:
            print(self.system_msg)
            self.system_msg = ''

    def login(self):
        my_msg, peer_msg = self.get_msgs()
        if len(my_msg) > 0:
            self.name = my_msg
            msg = json.dumps({"action":"login", "name":self.name})
            self.send(msg)
            response = json.loads(self.recv())
            if response["status"] == 'ok':
                self.state = S_LOGGEDIN
                self.sm.set_state(S_LOGGEDIN)
                self.sm.set_myname(self.name)
                self.print_instructions()
                return (True)
            elif response["status"] == 'duplicate':
                self.system_msg += 'Duplicate username, try again'
                return False
        else:
           return(False)

    def read_input(self):
        while True:
            text = sys.stdin.readline()[:-1]
            self.console_input.append(text)

    def print_instructions(self):
        self.system_msg += menu

    def run_chat(self):
        self.init_chat()
        self.gui.run()
        self.quit()

    def proc(self):
        my_msg, peer_msg = self.get_msgs()
        self.system_msg += self.sm.proc(my_msg, peer_msg)
