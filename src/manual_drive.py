import pygame
import sys
import os

# src klasörünü bulabilmesi için
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.track import Track
from src.car import Car

def main():
    pygame.init()
    width, height = 1200, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("DriverBot - Manuel Test")
    clock = pygame.time.Clock()

    track = Track(width, height)
    # Arabayı yeni kıvrımlı pistin başlangıç noktasına koyuyoruz
    start_x, start_y, start_angle = track.get_start_position()
    car = Car(start_x, start_y, track)
    car.angle = start_angle

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Klavye girdilerini al
        keys = pygame.key.get_pressed()
        car.handle_input(keys)
        
        # Arabanın fiziğini güncelle
        car.update()

        # Çime çarpıp çarpmadığını kontrol et (Oyun sonu koşulu)
        if track.is_off_track(car.x, car.y):
            # Çarparsa arabayı başa döndür
            print("Çime çarptın! Başa dönülüyor...")
            car.x, car.y, car.angle = track.get_start_position()
            car.speed = 0
            car.sensor.update()

        # Çizim işlemleri
        track.draw(screen)
        car.draw(screen)

        pygame.display.flip()
        clock.tick(60) # 60 FPS

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
