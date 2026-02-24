import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from std_msgs.msg import String, Int32
from sensor_msgs.msg import Image, LaserScan
# 👇 Sadece Trajectory kullanacağız, Float64'e gerek yok
from trajectory_msgs.msg import JointTrajectory, JointTrajectoryPoint 
from cv_bridge import CvBridge
import cv2
import numpy as np

class CokModluOtonom(Node):
    def __init__(self):
        super().__init__('imre_hibrit_pilot')
        
        # --- YAYINCILAR ---
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        
        # KAMERA KONTROL YAYINCISI (Gazebo Plugin'i bunu dinliyor)
        self.camera_pub = self.create_publisher(JointTrajectory, '/set_joint_trajectory', 10)
        
        # --- ABONELİKLER ---
        self.mode_sub = self.create_subscription(String, '/otonom_mod_secimi', self.mod_callback, 10)
        self.slider_sub = self.create_subscription(Int32, '/kamera_aci', self.slider_callback, 10) # TABLET
        
        self.sub_sonar_sol = self.create_subscription(LaserScan, '/sonar/left', self.sonar_sol_cb, 10)
        self.sub_sonar_sag = self.create_subscription(LaserScan, '/sonar/right', self.sonar_sag_cb, 10)
        self.sub_kamera = self.create_subscription(Image, '/camera/image_raw', self.kamera_cb, 10)
        
        self.bridge = CvBridge()
        self.aktif_mod = "MANUEL"
        
        # Değişkenler
        self.sol_mesafe = 10.0
        self.sag_mesafe = 10.0
        self.son_kamera_goruntusu = None
        
        self.timer = self.create_timer(0.1, self.ana_kontrol_dongusu)
        self.get_logger().info('SİSTEM HAZIR: KAMERA KONTROLÜ AKTİF! 🎥')

    # ==========================================
    # 👇 KAMERA KONTROLÜ (Tabletten Gelen Veri) 👇
    # ==========================================
    # ==========================================
    # 👇 GÜNCELLENMİŞ FONKSİYON 👇
    # ==========================================
    def slider_callback(self, msg):
        derece = msg.data
        # Derece -> Radyan dönüşümü
        radyan = (derece - 90.0) * (0.6 / 90.0)
        
        # Mesajı Hazırla
        traj_msg = JointTrajectory()
        
        # 🚨 İŞTE EKSİK OLAN PARÇA BURASIYDI! 🚨
        # Robotun hangi parçasına göre hareket edeceğini söylemeliyiz.
        # Senin ana gövdenin adı "chassis" olduğu için buraya onu yazıyoruz.
        traj_msg.header.frame_id = "chassis"  
        
        traj_msg.joint_names = ['camera_joint'] 
        
        point = JointTrajectoryPoint()
        point.positions = [float(radyan)]
        point.time_from_start.sec = 0
        point.time_from_start.nanosec = 500000000 
        
        traj_msg.points = [point]
        self.camera_pub.publish(traj_msg)

    # --- DİĞER FONKSİYONLAR ---
    def mod_callback(self, msg):
        self.aktif_mod = msg.data
        self.get_logger().info(f'YENİ GÖREV: {self.aktif_mod}')
        if self.aktif_mod == "MANUEL": self.durdur()

    def sonar_sol_cb(self, msg):
        if msg.ranges: self.sol_mesafe = min(msg.ranges)
    def sonar_sag_cb(self, msg):
        if msg.ranges: self.sag_mesafe = min(msg.ranges)
    def kamera_cb(self, msg):
        self.son_kamera_goruntusu = msg
    def durdur(self):
        self.pub.publish(Twist())

    # --- MOD 1: ENGELDEN KAÇ (GÜNCELLENMİŞ VERSİYON) ---
    def engelden_kac(self):
        cmd = Twist()
        limit = 0.40 
        
        if self.sol_mesafe < limit and self.sag_mesafe < limit:
            self.get_logger().warn('ÇIKMAZ SOKAK! Dönülüyor... 🔄')
            cmd.linear.x = -0.15 
            cmd.angular.z = 2.5 
        elif self.sol_mesafe < limit:
            cmd.linear.x = 0.0
            cmd.angular.z = -1.5
        elif self.sag_mesafe < limit:
            cmd.linear.x = 0.0
            cmd.angular.z = 1.5
        else:
            cmd.linear.x = 0.4 
            cmd.angular.z = 0.0
        self.pub.publish(cmd)

    # --- MOD 2: ÇİZGİ İZLE ---
    def cizgi_izle(self):
        if self.son_kamera_goruntusu is None: return
        try: cv_img = self.bridge.imgmsg_to_cv2(self.son_kamera_goruntusu, "bgr8")
        except: return
        
        h, w, _ = cv_img.shape
        crop = cv_img[int(h*1/2):h, 0:w]
        gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 130, 255, cv2.THRESH_BINARY_INV)
        M = cv2.moments(thresh)
        
        cmd = Twist()
        if M['m00'] > 0:
            cx = int(M['m10']/M['m00'])
            hata = cx - (w/2)
            cmd.linear.x = 0.2
            cmd.angular.z = -float(hata) * 0.005
        else:
            cmd.angular.z = 0.3
        self.pub.publish(cmd)

    # --- MOD 3: NİŞANCI ---
    def nisan_al(self):
        if self.son_kamera_goruntusu is None: return
        try: cv_img = self.bridge.imgmsg_to_cv2(self.son_kamera_goruntusu, "bgr8")
        except: return

        hsv = cv2.cvtColor(cv_img, cv2.COLOR_BGR2HSV)
        
        # Kırmızı Renk Maskesi
        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])
        
        mask = cv2.inRange(hsv, lower_red1, upper_red1) + cv2.inRange(hsv, lower_red2, upper_red2)
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        cmd = Twist()
        if contours:
            c = max(contours, key=cv2.contourArea)
            M = cv2.moments(c)
            if M['m00'] > 0:
                cx = int(M['m10']/M['m00'])
                h, w, _ = cv_img.shape
                hata = cx - (w/2)
                
                if abs(hata) < 20: 
                    self.get_logger().info('KİLİTLENDİ! ATEŞ SERBEST! 🔥')
                    cmd.angular.z = 0.0
                    cmd.linear.x = 0.0 
                else:
                    cmd.angular.z = -float(hata) * 0.005
        else:
            cmd.angular.z = 0.5
        self.pub.publish(cmd)

    def ana_kontrol_dongusu(self):
        if self.aktif_mod == "ENGEL": self.engelden_kac()
        elif self.aktif_mod == "CIZGI": self.cizgi_izle()
        elif self.aktif_mod == "HEDEF": self.nisan_al()
        else: pass

def main():
    rclpy.init()
    node = CokModluOtonom()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
