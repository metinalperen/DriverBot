import pygame
import math
from src.sensor import Sensor

class Car:
    def __init__(self, x, y, track):
        self.x = x
        self.y = y
        self.angle = 0  # 0 derece sağa bakar
        self.speed = 0
        
        # Fizik limitleri
        self.max_speed = 6
        self.acceleration = 0.2
        self.friction = 0.05
        self.turn_speed = 4
        
        # Boyutlar
        self.width = 40
        self.height = 20
        self.track = track
        
        # Sensörleri arabaya ekle
        self.sensor = Sensor(self, track)
        
        # Arabanın görseli
        self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.image.fill((200, 0, 0)) # Kırmızı araba
        
        # Arabanın ön tarafını belli etmek için far ekleyelim (Sarı)
        pygame.draw.rect(self.image, (255, 255, 0), (self.width - 5, 0, 5, 5))
        pygame.draw.rect(self.image, (255, 255, 0), (self.width - 5, self.height - 5, 5, 5))
        
    def handle_input(self, keys):
        # İleri ve geri gitme
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.speed += self.acceleration
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.speed -= self.acceleration
            
        # Sağa ve sola dönme (Sadece hareket ederken dönebiliriz)
        if abs(self.speed) > 0.5:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.angle += self.turn_speed
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.angle -= self.turn_speed

    def update(self):
        # Sürtünme kuvveti (Hızı yavaşça düşürür)
        if self.speed > 0:
            self.speed -= self.friction
        elif self.speed < 0:
            self.speed += self.friction
            
        # Çok düşük hızlarda arabayı tamamen durdur
        if abs(self.speed) < self.friction:
            self.speed = 0
            
        # Hız sınırını aşmasını engelle
        self.speed = max(-self.max_speed / 2, min(self.speed, self.max_speed))
        
        # X ve Y koordinatlarını hıza ve açıya göre güncelle
        self.x += math.cos(math.radians(self.angle)) * self.speed
        self.y -= math.sin(math.radians(self.angle)) * self.speed
        
        # Açıyı 0-360 arasında tut
        self.angle %= 360
        
        # Sensörleri güncelle
        self.sensor.update()
        
    def draw(self, screen):
        # Arabanın görüntüsünü mevcut açısına göre döndür
        rotated_image = pygame.transform.rotate(self.image, self.angle)
        rect = rotated_image.get_rect(center=(int(self.x), int(self.y)))
        
        # Ekrana çiz
        screen.blit(rotated_image, rect.topleft)
        
        # Sensörleri çiz
        self.sensor.draw(screen)
