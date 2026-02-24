#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import String, Int32, Bool, Float64MultiArray
from geometry_msgs.msg import Twist

class ImreKontrolMerkezi(Node):
    def __init__(self):
        super().__init__('imre_kontrol_merkezi')
        
        # --- AYARLAR ---
        # Tablet slider'ı kaç ile kaç arası sayı yolluyor? (Tahminen 0-100 arası)
        self.SLIDER_MIN = 0
        self.SLIDER_MAX = 100
        
        # Robotun kamerasının fiziksel limitleri (Radyan cinsinden)
        # 0.5 radyan yaklaşık 30 derece eder.
        self.ROBOT_MIN_RAD = -0.5  # Aşağı bakma limiti
        self.ROBOT_MAX_RAD = 0.5   # Yukarı bakma limiti

        # --- ABONELİKLER (Tabletten Gelenler) ---
        self.create_subscription(String, '/otonom_mod_secimi', self.mod_callback, 10)
        self.create_subscription(Int32, '/kamera_aci', self.servo_callback, 10)
        self.create_subscription(Bool, '/lazer_tetik', self.lazer_callback, 10)

        # --- YAYINCILAR (Robota Gidenler) ---
        # 1. Tekerlekler için
        self.cmd_vel_pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # 2. [EKLENEN KISIM] Kamera Motoru için
        # Burayı eklemezsen robot hareket etmez!
        self.camera_pub = self.create_publisher(Float64MultiArray, '/camera_controller/commands', 10)

        # --- Durumlar ---
        self.aktif_mod = "MANUEL"
        self.get_logger().info('IMRE KONTROL MERKEZI: Sistem Aktif, Kamera Motoru Bağlandı! 🚀')

    def mod_callback(self, msg):
        yeni_mod = msg.data
        if self.aktif_mod != yeni_mod:
            self.aktif_mod = yeni_mod
            self.get_logger().warn(f'MOD DEĞİŞTİ: {self.aktif_mod}')
            # Mod değişince robotu durdur
            self.cmd_vel_pub.publish(Twist())

    def servo_callback(self, msg):
        # 1. Tabletten gelen sayıyı al (Örn: 0 ile 100 arası)
        gelen_veri = msg.data
        
        # 2. Sayıyı sınırlara hapset (Ne olur ne olmaz, 0'dan küçük 100'den büyük olmasın)
        gelen_veri = max(self.SLIDER_MIN, min(self.SLIDER_MAX, gelen_veri))

        # 3. MATEMATİK: Slider (0-100) -> Radyan (-0.5 ile +0.5) dönüşümü
        # Bu formül slider'ın ortasını (50) robotun ortası (0 radyan) yapar.
        hedef_radyan = (gelen_veri - self.SLIDER_MIN) * (self.ROBOT_MAX_RAD - self.ROBOT_MIN_RAD) / (self.SLIDER_MAX - self.SLIDER_MIN) + self.ROBOT_MIN_RAD

        # 4. [EKLENEN KISIM] Komutu hazırla ve gönder
        komut = Float64MultiArray()
        komut.data = [float(hedef_radyan)]  # Listeye çeviriyoruz çünkü kontrolcü liste ister
        
        self.camera_pub.publish(komut)
        
        # Konsola basıp kontrol et (Çok hızlı akarsa başına # koyup kapatabilirsin)
        # self.get_logger().info(f'Kamera: {gelen_veri} -> {hedef_radyan:.2f} rad')

    def lazer_callback(self, msg):
        if msg.data:
            self.get_logger().error('🔥 LAZER ATEŞ! 🔥')
            # Buraya ilerde GPIO kodlarını ekleyeceğiz
        else:
            self.get_logger().info('Lazer Pasif.')

def main(args=None):
    rclpy.init(args=args)
    node = ImreKontrolMerkezi()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
