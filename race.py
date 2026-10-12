import os
import sys
import pygame
import numpy as np
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stable_baselines3 import PPO
from src.track import Track
from src.car import Car

def get_obs(car):
    # Yapay zekanın sensör verilerini hazırlayan ufak fonksiyon
    obs = [d / 500.0 for d in car.sensor.distances]
    obs.append(car.speed / car.max_speed)
    return np.array(obs, dtype=np.float32)

def main():
    if not os.path.exists("driverbot_model.zip"):
        print("Hata: 'driverbot_model.zip' bulunamadı.")
        return

    pygame.init()
    width, height = 1200, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Sen (Kırmızı) VS Yapay Zeka (Mavi)")
    clock = pygame.time.Clock()

    track = Track(width, height)
    
    # Başlangıç noktaları (Yanyana başlasınlar diye hesaplama yapıyoruz)
    start_x, start_y, start_angle = track.get_start_position()
    perp_angle = math.radians(start_angle - 90) # Yola dik açı
    
    # 1. OYUNCU ARABASI (Kırmızı)
    player_car = Car(start_x + math.cos(perp_angle) * 30, start_y - math.sin(perp_angle) * 30, track)
    player_car.angle = start_angle
    
    # 2. YAPAY ZEKA ARABASI (Mavi)
    ai_car = Car(start_x - math.cos(perp_angle) * 30, start_y + math.sin(perp_angle) * 30, track)
    ai_car.angle = start_angle
    # Mavi renge boyayalım
    ai_car.image.fill((0, 0, 255)) 
    # Farları ekleyelim
    pygame.draw.rect(ai_car.image, (255, 255, 0), (ai_car.width - 5, 0, 5, 5))
    pygame.draw.rect(ai_car.image, (255, 255, 0), (ai_car.width - 5, ai_car.height - 5, 5, 5))

    print("🧠 Model yükleniyor...")
    model = PPO.load("driverbot_model")
    print("🏎️ Yarış Başlıyor! OYNAMAK İÇİN YÖN TUŞLARINI (veya W A S D) KULLAN!")

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        # --- 1. Oyuncu Hareketi (Klavye) ---
        keys = pygame.key.get_pressed()
        player_car.handle_input(keys)
        player_car.update()
        
        # --- 2. Yapay Zeka Hareketi (Model) ---
        obs = get_obs(ai_car)
        action, _ = model.predict(obs, deterministic=True)
        
        steering = action[0]
        acceleration = action[1]
        
        if acceleration > 0:
            ai_car.speed += ai_car.acceleration * acceleration
        elif acceleration < 0:
            ai_car.speed += ai_car.acceleration * acceleration
            
        if abs(ai_car.speed) > 0.5:
            ai_car.angle -= ai_car.turn_speed * steering
            
        ai_car.update()
        
        # --- Kaza / Çime Çıkma Kontrolleri ---
        # Eğer birisi çime çıkarsa sadece o ceza olarak başa döner!
        if track.is_off_track(player_car.x, player_car.y):
            print("💥 Çime çıktın! (Kırmızı Başa Döndü)")
            player_car.x = start_x + math.cos(perp_angle) * 30
            player_car.y = start_y - math.sin(perp_angle) * 30
            player_car.angle = start_angle
            player_car.speed = 0
            
        if track.is_off_track(ai_car.x, ai_car.y):
            print("💥 Yapay Zeka kaza yaptı! (Mavi Başa Döndü)")
            ai_car.x = start_x - math.cos(perp_angle) * 30
            ai_car.y = start_y + math.sin(perp_angle) * 30
            ai_car.angle = start_angle
            ai_car.speed = 0

        # --- Çizim İşlemleri ---
        track.draw(screen)
        
        # Not: Yarışın sade görünmesi için arabaların üzerindeki lazer sensörlerini gizledik
        
        # Oyuncu Arabasını Çiz
        rot_player = pygame.transform.rotate(player_car.image, player_car.angle)
        rect_player = rot_player.get_rect(center=(int(player_car.x), int(player_car.y)))
        screen.blit(rot_player, rect_player.topleft)
        
        # AI Arabasını Çiz
        rot_ai = pygame.transform.rotate(ai_car.image, ai_car.angle)
        rect_ai = rot_ai.get_rect(center=(int(ai_car.x), int(ai_car.y)))
        screen.blit(rot_ai, rect_ai.topleft)
        
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
