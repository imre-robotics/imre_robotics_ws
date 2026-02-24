#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, Float64MultiArray
import numpy as np # interp fonksiyonu için kullanışlıdır

class KameraCevirici(Node):
    def __init__(self):
        super().__init__('kamera_cevirici')
        
        # Parametreler (Varsayılan değerler)
        self.declare_parameter('min_aci_rad', -1.0) # Örn: -57 derece
        self.declare_parameter('max_aci_rad', 1.0)  # Örn: +57 derece
        
        self.subscription = self.create_subscription(
            Int32,
            '/kamera_aci',
            self.listener_callback,
            10)
        
        self.publisher_ = self.create_publisher(
            Float64MultiArray,
            '/camera_controller/commands',
            10)
            
        self.get_logger().info('Kamera Çevirici Hazır. Beklenen Giriş: 0-100')

    def listener_callback(self, msg):
        gelen_sayi = msg.data
        
        # 1. Güvenlik: Gelen sayıyı 0 ile 100 arasına sabitle (Clamp)
        gelen_sayi = max(0, min(100, gelen_sayi))
        
        # Parametreleri oku
        min_rad = self.get_parameter('min_aci_rad').value
        max_rad = self.get_parameter('max_aci_rad').value
        
        # 2. Matematik: 0-100 aralığını -> min_rad ile max_rad arasına eşle
        # Formül: (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
        hedef_aci = (gelen_sayi - 0) * (max_rad - min_rad) / (100 - 0) + min_rad
        
        komut = Float64MultiArray()
        komut.data = [float(hedef_aci)] # Float dönüşümü garanti olsun
        
        self.publisher_.publish(komut)
        
        # Debug için log (İsteğe bağlı, çok hızlı akarsa yorum satırı yapın)
        # self.get_logger().info(f'Girdi: {gelen_sayi} -> Hedef Açı: {hedef_aci:.2f} rad')

def main(args=None):
    rclpy.init(args=args)
    node = KameraCevirici()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
