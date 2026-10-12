import pygame

def catmull_rom_spline(p0, p1, p2, p3, num_points=20):
    points = []
    for i in range(num_points):
        t = i / num_points
        t2 = t * t
        t3 = t2 * t
        
        x = 0.5 * ((2 * p1[0]) +
                   (-p0[0] + p2[0]) * t +
                   (2 * p0[0] - 5 * p1[0] + 4 * p2[0] - p3[0]) * t2 +
                   (-p0[0] + 3 * p1[0] - 3 * p2[0] + p3[0]) * t3)
                   
        y = 0.5 * ((2 * p1[1]) +
                   (-p0[1] + p2[1]) * t +
                   (2 * p0[1] - 5 * p1[1] + 4 * p2[1] - p3[1]) * t2 +
                   (-p0[1] + 3 * p1[1] - 3 * p2[1] + p3[1]) * t3)
        points.append((x, y))
    return points

class Track:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((width, height))
        
        # Kontrol noktaları (Pistin temel iskeleti)
        self.control_points = [
            (200, 200), (450, 150), (600, 350), 
            (850, 200), (1050, 350), (950, 650), 
            (700, 500), (450, 700), (200, 600), (100, 400)
        ]
        
        # Eğrileri hesaplayarak pürüzsüz noktaları oluştur
        self.path = []
        n = len(self.control_points)
        for i in range(n):
            self.path.extend(catmull_rom_spline(
                self.control_points[(i - 1) % n], 
                self.control_points[i], 
                self.control_points[(i + 1) % n], 
                self.control_points[(i + 2) % n], 
                25
            ))
            
        self.draw_track()

    def draw_track(self):
        # Arka plan çimleri (Yeşil)
        self.surface.fill((34, 139, 34)) 
        
        road_width = 130
        
        # Yolu kalın çizgilerle çiz
        pygame.draw.lines(self.surface, (80, 80, 80), True, self.path, road_width)
        
        # Keskinlikleri yok etmek için her noktaya daire çiz (Çok daha pürüzsüz yapar)
        for p in self.path:
            pygame.draw.circle(self.surface, (80, 80, 80), (int(p[0]), int(p[1])), road_width // 2)
            
        # Başlangıç çizgisi
        start_x, start_y = self.path[0]
        # Yönü hesaplamak için sonraki noktaya bak
        next_x, next_y = self.path[1]
        import math
        angle = math.atan2(next_y - start_y, next_x - start_x)
        # Çizgiyi yola dik çizeceğiz
        perp_angle = angle + math.pi / 2
        p1 = (start_x + math.cos(perp_angle) * (road_width//2), start_y + math.sin(perp_angle) * (road_width//2))
        p2 = (start_x - math.cos(perp_angle) * (road_width//2), start_y - math.sin(perp_angle) * (road_width//2))
        pygame.draw.line(self.surface, (255, 255, 255), p1, p2, 10)

    def get_start_position(self):
        # Arabayı ilk noktanın üzerine ve yolun yönüne doğru yerleştir
        start_x, start_y = self.path[0]
        next_x, next_y = self.path[1]
        import math
        # math.atan2 radyan döner, bunu dereceye çeviriyoruz
        angle = math.degrees(math.atan2(start_y - next_y, next_x - start_x)) 
        return start_x, start_y, angle


    def is_off_track(self, x, y):
        # Ekranın dışına çıkıldıysa
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return True
            
        # x ve y koordinatındaki piksel rengine bakıyoruz
        color = self.surface.get_at((int(x), int(y)))
        
        # Eğer renk yeşil ise (34, 139, 34) araba çimlerdedir
        if color[0] == 34 and color[1] == 139 and color[2] == 34:
            return True
            
        return False
        
    def draw(self, screen):
        screen.blit(self.surface, (0, 0))
