import math
import pygame

class Sensor:
    def __init__(self, car, track, num_rays=7, ray_length=500):
        self.car = car
        self.track = track
        self.num_rays = num_rays
        self.ray_length = ray_length
        # Arabanın açısına göre sensör açıları (derece)
        # Daha geniş ve hassas görüş için 7 sensör (-90'dan 90'a)
        self.angles = [-90, -60, -30, 0, 30, 60, 90] 
        self.distances = [ray_length] * num_rays
        self.points = []

    def update(self):
        self.distances = []
        self.points = []
        
        for angle in self.angles:
            # Arabanın mevcut açısı + sensörün açısı
            ray_angle = math.radians(self.car.angle + angle)
            distance = 0
            hit = False
            end_x, end_y = self.car.x, self.car.y
            
            # Lazer ışınını adım adım ileri götürüyoruz (Raycasting)
            for i in range(self.ray_length):
                test_x = self.car.x + math.cos(ray_angle) * i
                test_y = self.car.y - math.sin(ray_angle) * i # y ekseni pygame'de ters
                
                # Çime çarpıp çarpmadığını kontrol et
                if self.track.is_off_track(test_x, test_y):
                    distance = i
                    hit = True
                    end_x, end_y = test_x, test_y
                    break
            
            # Eğer hiçbir şeye çarpmadıysa menzil sonunu hedef kabul et
            if not hit:
                distance = self.ray_length
                end_x = self.car.x + math.cos(ray_angle) * self.ray_length
                end_y = self.car.y - math.sin(ray_angle) * self.ray_length
                
            self.distances.append(distance)
            self.points.append((end_x, end_y))

    def draw(self, screen):
        for point in self.points:
            # Lazer ışınını çiz (Cam göbeği renk)
            start_pos = (int(self.car.x), int(self.car.y))
            end_pos = (int(point[0]), int(point[1]))
            pygame.draw.line(screen, (0, 255, 255), start_pos, end_pos, 1)
            # Lazerin bittiği/çarptığı noktayı çiz (Kırmızı renk)
            pygame.draw.circle(screen, (255, 0, 0), end_pos, 4)
