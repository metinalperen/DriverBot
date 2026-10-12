import pygame
import sys
import os
import json
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.track import Track

def main():
    if not os.path.exists("ghost_trajectories.json"):
        print("Hata: 'ghost_trajectories.json' bulunamadı. Lütfen önce modeli eğitin (python train.py)")
        return
        
    with open("ghost_trajectories.json", "r") as f:
        trajectories = json.load(f)
        
    pygame.init()
    width, height = 1200, 800
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("DriverBot - AI Evolution (100 Ghost Cars)")
    clock = pygame.time.Clock()

    track = Track(width, height)
    
    # Arabanın görüntüsünü yükle (Daha şeffaf çizeceğiz)
    car_image = pygame.Surface((40, 20), pygame.SRCALPHA)
    
    # Öğrenme sürecindeki aşamasına göre arabaları renklendireceğiz:
    # Baştakiler (kötüler) : Kırmızımsı/Şeffaf
    # Ortadakiler (orta)   : Sarimsi/Şeffaf
    # Sondakiler (iyiler)  : Yeşimsi/Şeffaf ve daha belirgin
    
    ghosts = []
    total_ghosts = len(trajectories)
    
    for idx, traj in enumerate(trajectories):
        progress = idx / max(1, (total_ghosts - 1))
        
        # Renk skalası: Kırmızıdan (başlangıç) Yeşile (bitiş)
        r = int((1 - progress) * 255)
        g = int(progress * 255)
        b = 0
        # Gittikçe daha belirgin (alpha) olsunlar
        alpha = int(50 + progress * 150)
        
        img = car_image.copy()
        img.fill((r, g, b, alpha))
        
        # Farlar
        pygame.draw.rect(img, (255, 255, 0, alpha), (35, 0, 5, 5))
        pygame.draw.rect(img, (255, 255, 0, alpha), (35, 15, 5, 5))
        
        ghosts.append({
            "trajectory": traj,
            "image": img,
            "frame": 0,
            "done": False
        })
        
    running = True
    frame_index = 0
    
    print("Hayalet arabalar pistte! (Kırmızı: Eğitimin başları, Sarı: Ortaları, Yeşil: Sonları)")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
        track.draw(screen)
        
        all_done = True
        
        for ghost in ghosts:
            traj = ghost["trajectory"]
            current_frame = ghost["frame"]
            
            if current_frame < len(traj):
                all_done = False
                x, y, angle = traj[current_frame]
                
                rotated_image = pygame.transform.rotate(ghost["image"], angle)
                rect = rotated_image.get_rect(center=(int(x), int(y)))
                screen.blit(rotated_image, rect.topleft)
                
                ghost["frame"] += 1
                
        pygame.display.flip()
        clock.tick(60) # 60 FPS Hızında oynat
        
        # Tüm arabalar çarptıysa/gittiyse başa sar
        if all_done:
            for ghost in ghosts:
                ghost["frame"] = 0

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
