import os
import sys

# src modülünü bulabilmesi için
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from src.env import CarRacingEnv

import json
import numpy as np
from stable_baselines3.common.callbacks import BaseCallback

class TrajectoryLoggerCallback(BaseCallback):
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.episode_count = 0
        self.trajectories = []
        self.current_trajectory = []

    def _on_step(self) -> bool:
        # PPO arka planda ortamı bir Array (Vector) içine aldığı için envs[0] ile asıl oyuna erişiyoruz
        env = self.training_env.envs[0].unwrapped
        
        # RAM tasarrufu ve JSON uyumluluğu için numpy tiplerini standart float'a çeviriyoruz
        self.current_trajectory.append((
            float(round(env.car.x, 1)), 
            float(round(env.car.y, 1)), 
            float(round(env.car.angle, 1))
        ))
        
        # Araba çarptığında veya süre bittiğinde (done = True)
        if self.locals["dones"][0]:
            self.episode_count += 1
            # Her bölümü kaydederek hafızayı çok doldurmamak için her 3 bölümde bir kaydedelim
            if self.episode_count % 3 == 0:
                self.trajectories.append(self.current_trajectory)
            self.current_trajectory = []
            
        return True

    def _on_training_end(self) -> None:
        total_saved = len(self.trajectories)
        num_ghosts = min(100, total_saved)
        
        if num_ghosts > 0:
            # Baştan (kötü sürüş), ortadan (öğrenme aşaması) ve sondan (iyi sürüş) 
            # homojen olarak 100 adet bölüm seçiyoruz
            indices = np.linspace(0, total_saved - 1, num_ghosts, dtype=int)
            final_trajectories = [self.trajectories[i] for i in indices]
        else:
            final_trajectories = []
            
        with open("ghost_trajectories.json", "w") as f:
            json.dump(final_trajectories, f)
        print(f"\n👻 Gelişimi izlemek için {len(final_trajectories)} adet hayalet arabanın (ghost car) rotası kaydedildi!")

def main():
    print("Ortam (Environment) yapısı kontrol ediliyor...")
    # Eğitim sırasında hızı artırmak için ekranı çizdirmiyoruz (render_mode=None)
    env = CarRacingEnv(render_mode=None)
    check_env(env)
    print("Ortam başarıyla doğrulandı!\n")

    # Şampiyon botumuzu kaybetmemek için arkada yedeğini aldım! (driverbot_champion.zip)
    model_path = "driverbot_model.zip"
    if os.path.exists(model_path):
        print(f"🧠 Şampiyon beyin ({model_path}) yükleniyor...")
        # ent_coef (Entropi) = Yapay zekanın "merak" ve "risk alma" içgüdüsü. 
        # Normalde 0'a yakındır, bunu artırarak onu yeni ve tehlikeli (ama daha hızlı) yollar bulmaya zorluyoruz!
        custom_objects = {
            "ent_coef": 0.05, 
            "learning_rate": 0.0001 # Daha ince ayarlar yapabilmesi için öğrenme hızını biraz düşürdük
        }
        model = PPO.load(model_path, env=env, device="auto", custom_objects=custom_objects)
    else:
        print("🧠 Yeni ve daha gelişmiş bir yapay zeka beyni (PPO) oluşturuluyor...")
        model = PPO(
            "MlpPolicy",
            env,
            verbose=1,
            learning_rate=0.0003,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            ent_coef=0.05,
            device="auto"
        )

    print("🏁 Yüksek Riskli/Meraklı Eğitim başlıyor... (Toplam 1,000,000 adım sürecek)")
    print("Not: Eğitim sırasında oyun ekranı açılmaz, tamamen arka planda ultra hızlı gerçekleşir.")
    print("Ağır log dosyaları tutmuyoruz, eğitim bitince tek bir zip dosyası alacaksın.\n")
    
    # Eğitimi başlat (Callback'i ekledik)
    model.learn(total_timesteps=1_000_000, progress_bar=True, callback=TrajectoryLoggerCallback())

    print("\n✅ Eğitim bitti! Model diske kaydediliyor...")
    model.save("driverbot_model")
    print("Model 'driverbot_model.zip' olarak kaydedildi. (Boyutu sadece 1-2 MB)")

if __name__ == "__main__":
    main()
