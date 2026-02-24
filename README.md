---

### 3. `imre_robotics_ws` İçin Güncel README.md

```markdown
# İmre Robotics - Otonom Sistemler ve Simülasyon Çalışmaları

> ⚠️ **Durum: Aktif Geliştirme Aşamasında (In Development)**
> *Kişisel projelerimi, simülasyon testlerimi ve donanım entegrasyonlarımı barındıran bu çalışma alanı sürekli olarak güncellenmektedir.*

Bu repo, otonom araçlar ve robotik sistemler üzerine geliştirdiğim bireysel projeleri barındırmaktadır. Hem fiziksel donanımlar (Raspberry Pi) hem de simülasyon ortamları (Gazebo) için oluşturulmuş ROS2 paketlerini içerir.

## 🤖 Projeler
1. **Web Kontrollü Araç Simülasyonu:** - Ackermann direksiyon sistemine sahip bir aracın Gazebo üzerinde modellenmesi.
   - Rosbridge ve WebSockets kullanılarak aracın internet tarayıcısı üzerinden kontrol edilmesi.
2. **Raspberry Pi Tabanlı Otonom Rover:** - 4 tekerlekli (diferansiyel sürüş) mobil robotun ROS2 entegrasyonu.
   - Kamera ve sensör (Lidar) verilerinin işlenerek otonom sürüş yeteneği kazandırılması.

## 🛠️ Kullanılan Teknolojiler ve Beceriler
- ROS2 (Humble/Iron)
- C++ & Python
- OpenCV (Görüntü İşleme)
- Gazebo & RViz
- Rosbridge Suite (Web tabanlı kontrol için)
- Gömülü Sistemler (Raspberry Pi)

## ⚙️ Kurulum
```bash
cd ~/imre_robotics_ws
colcon build --symlink-install
source install/setup.bash
