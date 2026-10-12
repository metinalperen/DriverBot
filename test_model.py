import os
import sys
import time

# src modülünü bulabilmesi için
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stable_baselines3 import PPO
from src.env import CarRacingEnv

def main():
    if not os.path.exists("driverbot_model.zip"):
        print("Hata: 'driverbot_model.zip' bulunamadı.")
        print("Lütfen önce 'python train.py' çalıştırarak modeli eğitin!")
        return

    # İzlemek istediğimiz için render_mode="human"
    env = CarRacingEnv(render_mode="human")
    model = PPO.load("driverbot_model")

    print("✅ Model başarıyla yüklendi! Yapay zeka piste çıkıyor...")
    
    obs, info = env.reset()
    
    while True:
        # deterministic=True, modelin rastgele hareketler yapmasını engeller
        # Her zaman o durum için bildiği en iyi hamleyi yapar.
        action, _states = model.predict(obs, deterministic=True)
        
        obs, reward, terminated, truncated, info = env.step(action)
        
        if terminated:
            print("💥 Araba çimlere çıktı (Kaza)! Yeniden başlıyor...")
            obs, info = env.reset()
            time.sleep(1)
        elif truncated:
            print("🏁 Süre doldu (3000 adım). Yeniden başlıyor...")
            obs, info = env.reset()

if __name__ == "__main__":
    main()
