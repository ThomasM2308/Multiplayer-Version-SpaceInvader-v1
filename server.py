import socket
import pickle
import threading
import time

# Server-Einstellungen
HOST = '192.168.178.40'   # Lauschen auf allen Schnittstellen
PORT = 55201        # Port, auf dem der Server hört
MAX_PLAYERS = 2     # Maximal 2 Spieler

# Liste für die verbundenen Clients
clients = []
player_positions = [(0, 0), (0, 0)]  # Anfangspositionen der Spieler
game_started = False

def handle_client(client_socket, player_id):
    global game_started
    try:
        # Begrüßungsnachricht
        client_socket.sendall(pickle.dumps("Warte auf den zweiten Spieler..."))

        # Warte auf die Bestätigung des zweiten Spielers
        while len(clients) < MAX_PLAYERS:
            time.sleep(1)

        if len(clients) == MAX_PLAYERS and not game_started:
            # Starte den Countdown
            for i in range(3, 0, -1):
                message = f"Start in {i}..."
                for client in clients:
                    client.sendall(pickle.dumps(message))
                time.sleep(1)

            # Das Spiel beginnt
            game_started = True
            for client in clients:
                client.sendall(pickle.dumps("Spiel gestartet!"))

        # Das Spiel läuft jetzt, empfange Daten von den Spielern
        while game_started:
            data = client_socket.recv(2048)
            if not data:
                break  # Client hat sich getrennt
            # Empfange die Position und sende sie an alle Clients
            player_positions[player_id] = pickle.loads(data)
            for client in clients:
                client.sendall(pickle.dumps(player_positions))
    except Exception as e:
        print(f"Fehler: {e}")
    finally:
        client_socket.close()
        clients.remove(client_socket)
        print(f"Spieler {player_id + 1} hat das Spiel verlassen.")

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(MAX_PLAYERS)
    
    print(f"Server läuft auf {HOST}:{PORT}...")  # Textnachricht beim Start des Servers
    print("Warte auf Spieler, um sich zu verbinden...")  # Nachricht, dass der Server auf Verbindungen wartet

    while len(clients) < MAX_PLAYERS:
        client_socket, addr = server.accept()
        print(f"Verbindung von {addr} hergestellt.")
        
        # Füge den Client zur Liste hinzu
        clients.append(client_socket)
        
        # Starte einen Thread für den jeweiligen Client
        player_id = len(clients) - 1
        threading.Thread(target=handle_client, args=(client_socket, player_id)).start()

    server.close()

if __name__ == "__main__":
    start_server()
    print("Server wurde beendet.")  # Nachricht, dass der Server beendet wurde