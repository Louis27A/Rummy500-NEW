import pygame
import sys
from ui import UIManager
from network import NetworkManager
from volumen import ControlVolumen
import os


def resource_path(relative_path):
    """ Obtiene la ruta absoluta para recursos, compatible con dev y PyInstaller """
    try:
        # PyInstaller crea una carpeta temporal y guarda la ruta en _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def main():
    pygame.init()
    
    SCREEN_WIDTH, SCREEN_HEIGHT = 1280, 720
    network_manager = NetworkManager()
    ui_manager = UIManager(SCREEN_WIDTH, SCREEN_HEIGHT, network_manager)

    pygame.mixer.init()  
    pygame.mixer.music.load(resource_path("assets/sonido/musica_fondo.mp3"))  
    pygame.mixer.music.play(-1)
    ctrl_volumen=ControlVolumen()

    running = True
    while running:
        result = ui_manager.handle_events()
        if result == "launch_ui2":
            if network_manager.is_host:
                jugadores = network_manager.connected_players
                print(f"Inicializando juego con {len(jugadores)}")
                # Para verificar que el network_manager siga ejecutándose
                network_manager.running = True

                import ui2
                # Pasa el objeto network_manager que contiene el estado de la conexión
                ui2.main(network_manager)
                ui_manager.current_screen = "main"
                
                # Resetear estado para próxima partida
                network_manager.game_started = False
                continue
            else:
                # Para verificar que el network_manager siga ejecutándose
                network_manager.running = True
                
                import ui2
                # Pasa el objeto network_manager que contiene el estado de la conexión
                ui2.main(network_manager)
                ui_manager.current_screen = "main"
                
                # Resetear estado para próxima partida
                network_manager.game_started = False
                continue
                
        elif result is False:
            running = False
        else:
            ui_manager.update()
            ctrl_volumen.actualizar_y_dibujar()             

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
{
    
}
