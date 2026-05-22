"""
╔══════════════════════════════════════════════════════════════════╗
║   BOÎTE À OUTILS HACKATHON — server.py                           ║
║   Lancer en PREMIER, avant les clients.                          ║
║   N'importe quelle machine du studio peut faire tourner ce       ║
║   fichier — ce sera "la machine serveur".                        ║
║                                                                  ║
║   Ce fichier n'est pas à modifier.                               ║
╚══════════════════════════════════════════════════════════════════╝
"""

import socket
import pickle
import threading
import time
from gamestate import GameState

HOST = "0.0.0.0"   # écoute sur toutes les interfaces réseau
PORT = 5555


def send_msg(conn, data):
    raw = pickle.dumps(data)
    conn.sendall(len(raw).to_bytes(4, "big") + raw)


def recv_msg(conn):
    raw_len = b""
    while len(raw_len) < 4:
        chunk = conn.recv(4 - len(raw_len))
        if not chunk:
            raise ConnectionResetError
        raw_len += chunk
    n = int.from_bytes(raw_len, "big")
    data = b""
    while len(data) < n:
        chunk = conn.recv(min(4096, n - len(data)))
        if not chunk:
            raise ConnectionResetError
        data += chunk
    return pickle.loads(data)


def handle_client(conn, player_id, game, lock):
    """Thread dédié à un client. Reçoit ses actions, renvoie le snapshot."""
    send_msg(conn, player_id)
    try:
        while True:
            action = recv_msg(conn)
            with lock:
                game.apply_action(player_id, action)
                snap = game.get_snapshot()
            send_msg(conn, snap)
            if snap["game_won"] or snap["game_lost"]:
                break
    except Exception:
        pass
    finally:
        conn.close()


def update_loop(game, lock):
    """Boucle ~60 fps indépendante des actions — met à jour le timer et les effets temporels."""
    while not (game.game_won or game.game_lost):
        with lock:
            game.update()
        time.sleep(1 / 60)


def main():
    game = GameState()
    lock = threading.Lock()
    threading.Thread(target=update_loop, args=(game, lock), daemon=True).start()

    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    srv.bind((HOST, PORT))
    srv.listen(2)
    print(f"[Serveur] En attente de 2 joueurs sur le port {PORT}...")
    print(f"[Serveur] Trouver l'IP de cette machine : python check_network.py")

    threads, n = [], 0
    while n < 2:
        conn, addr = srv.accept()
        n += 1
        print(f"[Serveur] Joueur {n} connecté depuis {addr}")
        t = threading.Thread(
            target=handle_client,
            args=(conn, n, game, lock),
            daemon=True
        )
        t.start()
        threads.append(t)

    print("[Serveur] 🚀 Partie lancée !")
    for t in threads:
        t.join()
    print("[Serveur] Partie terminée.")


if __name__ == "__main__":
    main()
