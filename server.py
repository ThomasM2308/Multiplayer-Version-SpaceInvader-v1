import pygame
import sys
import socket
import pickle
import settings as s
from entities.player import Player

pygame.init()
window = pygame.display.set_mode((s.SCREEN_WIDTH, s.SCREEN_HEIGHT))
pygame.display.set_caption("Multiplayer Space Invader")
clock = pygame.time.Clock()

# Verbindung zum Server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('192.168.178.40', 55201))  # Server-IP hier

# Spielerobjekte
spieler = Player((0, 0), color=s.GREEN)
gegner = Player((0, 0), color=s.BLUE)

# Spielstatus und Countdown
game_started = False
countdown_message = "Warte auf den zweiten Spieler..."

# Funktion zur Steuerung
def steuerung(keys):
    richtung = {"x": 0, "y": 0}  
    if keys[pygame.K_LEFT]:
        richtung["x"] = -1
    elif keys[pygame.K_RIGHT]:
        richtung["x"] = 1
    if keys[pygame.K_UP]:
        richtung["y"] = -1
    elif keys[pygame.K_DOWN]:
        richtung["y"] = 1
    return richtung

running = True
while running:
    clock.tick(s.FPS)
    window.fill(s.BLACK)

    # Nachrichten vom Server empfangen
    try:
        message = pickle.loads(sock.recv(2048))
        if message:
            if isinstance(message, str):
                countdown_message = message  # Text für den Countdown
            elif isinstance(message, list):
                spieler.rect.topleft = message[0]
                gegner.rect.topleft = message[1]
    except:
        pass  # Wenn keine Nachricht verfügbar, einfach weitermachen

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    richtung = steuerung(keys)

    # Sende die Eingabedaten an den Server
    nachricht = {"richtung": richtung}
    sock.sendall(pickle.dumps(nachricht))

    # Countdown anzeigen
    font = pygame.font.SysFont(None, 30)
    countdown_text = font.render(countdown_message, True, (255, 255, 255))
    window.blit(countdown_text, (s.SCREEN_WIDTH // 2 - countdown_text.get_width() // 2, s.SCREEN_HEIGHT // 2))

    # Wenn das Spiel startet, das eigentliche Spiel starten
    if game_started:
        spieler.zeichnen(window)
        gegner.zeichnen(window)

    pygame.display.update()

pygame.quit()
sys.exit()
