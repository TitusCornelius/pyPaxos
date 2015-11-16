import gevent, socket, struct
from gevent import monkey
import utils
monkey.patch_socket()

class Entity(object):
    def __init_socket(self, group):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 
            struct.pack('b', 1)) #Only live in the LAN
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP,
            struct.pack('4sL', socket.inet_aton(group),
            socket.INADDR_ANY))
        return sock
        
    def __init__(self, pid, role, config_path):
        self.__config = utils.read_config(config_path)
        for r in self.__config:
            self.__config[r][1] = int(self.__config[r][1])
        self.__role = role
        self.__multicast_group = tuple(self.__config[self.__role])

        self._id = pid
        self.__recv_socket = self.__init_socket(self.__multicast_group[0])
        self.__recv_socket.bind(self.__multicast_group)
    
    def send(self, msg, dst_role):
        if dst_role == self.__role: 
            return self.__recv_socket.sendto(msg.encode(), self.__multicast_group)
        send_socket = self.__init_socket(self.__config[dst_role][0])
        send_socket.sendto(msg.encode(), tuple(self.__config[dst_role]))
        send_socket.close()

    def recv(self):
        print('Receiving...')
        msg, addr = self.__recv_socket.recvfrom(1024) #TODO: Adjust buffer size?!
        return (msg, addr)