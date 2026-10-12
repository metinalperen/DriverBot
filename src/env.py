import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
import math
from src.track import Track
from src.car import Car

class CarRacingEnv(gym.Env):
    metadata = {"render_modes": ["human", "none"], "render_fps": 60}

    def __init__(self, render_mode=None):
        super().__init__()
        self.width = 1200
        self.height = 800
        self.render_mode = render_mode
        
        # Action Space: Sürekli değerler (İki işi aynı anda yapabilmesi için)
        # [0]: Direksiyon (-1 tam sol, 1 tam sağ)
        # [1]: Gaz/Fren (-1 tam fren, 1 tam gaz)
        self.action_space = spaces.Box(
            low=np.array([-1.0, -1.0]), 
            high=np.array([1.0, 1.0]), 
            dtype=np.float32
        )
        
        # Observation Space: 7 sensör + 1 hız = 8 değer
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(8,), dtype=np.float32
        )
        
        self.screen = None
        self.clock = None
        if self.render_mode == "human":
            pygame.init()
            pygame.display.init()
            self.screen = pygame.display.set_mode((self.width, self.height))
            self.clock = pygame.time.Clock()
            
        self.track = Track(self.width, self.height)
        self.car = None
        
        self.current_step = 0
        self.max_steps = 3000
        
        # Pisti 50 adet geniş "dilime" (checkpoint) bölüyoruz. 
        # Bunlar arabanın yolda ilerlediğini anlaması için (ekmek kırıntısı).
        self.checkpoints = self.track.path[::5]
        self.current_checkpoint_idx = 0
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        start_x, start_y, start_angle = self.track.get_start_position()
        self.car = Car(start_x, start_y, self.track)
        self.car.angle = start_angle
        self.car.speed = 0
        
        self.current_step = 0
        self.current_checkpoint_idx = 0
        
        self.car.sensor.update()
        return self._get_obs(), {}
        
    def _get_obs(self):
        # 7 sensör mesafesi ve hız.
        # AI'ın daha iyi öğrenmesi için değerleri 0 ile 1 arasına sıkıştırıyoruz (Normalize).
        obs = [d / 500.0 for d in self.car.sensor.distances]
        obs.append(self.car.speed / self.car.max_speed)
        return np.array(obs, dtype=np.float32)
        
    def step(self, action):
        self.current_step += 1
        
        steering = action[0] # -1 ile 1 arası
        acceleration = action[1] # -1 ile 1 arası
        
        # Gaz ve fren
        if acceleration > 0:
            self.car.speed += self.car.acceleration * acceleration
        elif acceleration < 0:
            self.car.speed += self.car.acceleration * acceleration
            
        # Sadece hareket ederken dönebilir
        if abs(self.car.speed) > 0.5:
            # Pygame'de açılar saat yönünün tersine artar
            self.car.angle -= self.car.turn_speed * steering

        self.car.update()
        
        reward = 0.0
        terminated = False
        truncated = False
        
        # 1. Zaman Cezası (Hızlı bitirmeye zorlar)
        reward -= 0.005
        
        # 2. Çimlere Çarpma 
        if self.track.is_off_track(self.car.x, self.car.y):
            reward -= 5.0
            terminated = True
            
        # 3. Geniş Checkpoint Kontrolü (İlerlemeyi Anlaması İçin)
        if not terminated:
            target_cp = self.checkpoints[self.current_checkpoint_idx]
            dist = math.hypot(self.car.x - target_cp[0], self.car.y - target_cp[1])
            
            # Yarıçapı 150 piksel yaptık! Yol zaten 130 piksel. 
            # Yani araba yolun en sağından da gitse, en solundan da gitse bu noktayı geçmiş sayılacak! (Özgür Rota)
            if dist < 150:
                reward += 0.2 # İlerlediği için ufak ödül
                self.current_checkpoint_idx += 1
                
                # Bütün checkpointleri bitirip turu tamamlarsa
                if self.current_checkpoint_idx >= len(self.checkpoints):
                    self.current_checkpoint_idx = 0
                    reward += 10.0 # Tur tamamlama ödülü
                    # Sonsuz tur atması için terminated yapmıyoruz
                # Böylece yapay zeka durmadan arka arkaya yüzlerce tur atabilir!
                    
        # 4. Zaman Aşımı
        if self.current_step >= self.max_steps:
            truncated = True
            
        if self.render_mode == "human":
            self.render()
            
        return self._get_obs(), float(reward), bool(terminated), bool(truncated), {}
        
    def render(self):
        if self.screen is None:
            return
            
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                import sys
                sys.exit()
                
        self.track.draw(self.screen)
        
        # Başlangıç/Bitiş ve Yarıyol noktalarını (çok hafif şeffaf veya ufak) çizebiliriz ama şimdilik gerek yok
        
        self.car.draw(self.screen)
        
        pygame.display.flip()
        self.clock.tick(self.metadata["render_fps"])

    def close(self):
        if self.screen is not None:
            pygame.quit()
            self.screen = None
