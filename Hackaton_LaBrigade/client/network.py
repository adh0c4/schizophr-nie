"""
╔══════════════════════════════════════════════════════════════════╗
║   BOÎTE À OUTILS HACKATHON — network.py                          ║
╠══════════════════════════════════════════════════════════════════╣
║   CE FICHIER EST À MODIFIER une seule fois au démarrage.         ║
║   Étape 1 : sur la machine serveur, lancer :                     ║
║               python check_network.py                            ║
║             → note l'IP affichée, ex. 192.168.12.47             ║
║   Étape 2 : sur CHAQUE machine cliente, modifier SERVER_IP       ║
║             ci-dessous avec cette IP.                            ║
║             OU lancer directement :                              ║
║               python check_network.py --set-ip 192.168.12.47    ║
║   Étape 3 : lancer server.py, puis client_j1.py, client_j2.py   ║
╚══════════════════════════════════════════════════════════════════╝
"""
import socket
import pickle


# ✏️  MODIFIER CETTE LIGNE avec l'IP de la machine qui fait tourner server.py
# → Pour trouver cette IP : lancer  python check_network.py  sur cette machine
# → Laisser "localhost" si tout tourne sur une seule machine (mode test)
SERVER_IP   = "localhost"
SERVER_PORT = 5555
BUFFER_SIZE = 8192


class Network:
    """
    Gère la connexion TCP vers le serveur.
    Usage dans les clients :
        net = Network()                        # connexion avec SERVER_IP ci-dessus
        net = Network(server_ip="192.168.x.x") # override ponctuel (argument CLI)
        state = net.send({"action": "get"})    # envoyer une action, recevoir le snapshot
        net.disconnect()                       # fermer proprement
    """

    def __init__(self, server_ip: str = None):
        ip = server_ip if server_ip else SERVER_IP
        self.client    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.player_id = None
        try:
            self.client.connect((ip, SERVER_PORT))
        except ConnectionRefusedError:
            print(f"[Network] ❌ Impossible de joindre {ip}:{SERVER_PORT}")
            print("          → server.py est-il lancé sur cette machine ?")
            print("          → L'IP dans network.py est-elle correcte ?")
            print("          → Pare-feu Windows ? → python check_network.py --fix")
            raise
        self.player_id = pickle.loads(self._recv_all())
        print(f"[Network] ✅ Connecté à {ip}:{SERVER_PORT} — Joueur {self.player_id}")

    def get_p(self):
        return self.player_id

    def send(self, action: dict):
        """
        Envoie une action au serveur et retourne le snapshot mis à jour.
        action : dict avec au minimum {"action": "nom_action"}
        Retourne : dict (snapshot) ou None si erreur réseau
        """
        try:
            raw = pickle.dumps(action)
            self.client.sendall(len(raw).to_bytes(4, "big") + raw)
            return pickle.loads(self._recv_all())
        except Exception as e:
            print(f"[Network] Erreur : {e}")
            return None

    def _recv_all(self):
        raw_len = b""
        while len(raw_len) < 4:
            c = self.client.recv(4 - len(raw_len))
            if not c:
                raise EOFError("Connexion fermée par le serveur")
            raw_len += c
        n = int.from_bytes(raw_len, "big")
        data = b""
        while len(data) < n:
            c = self.client.recv(min(BUFFER_SIZE, n - len(data)))
            if not c:
                raise EOFError("Connexion fermée par le serveur")
            data += c
        return data

    def disconnect(self):
        try:
            self.client.close()
        except Exception:
            pass
