import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, RegisterEventHandler
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node
from launch.event_handlers import OnProcessExit

def generate_launch_description():
    pkg_name = 'imre_description'

    # 1. DÜNYA DOSYASI GÜNCELLEMESİ (Yeni sahan burada)
    world_path = os.path.join(get_package_share_directory(pkg_name), 'worlds', 'imre_world.world')

    # 2. Robot State Publisher (RSP)
    rsp = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory(pkg_name),'launch','rsp.launch.py'
        )]), launch_arguments={'use_sim_time': 'true'}.items()
    )

    # 3. Gazebo'yu Başlat
    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource([os.path.join(
            get_package_share_directory('gazebo_ros'), 'launch', 'gazebo.launch.py')]),
        launch_arguments={'world': world_path}.items()
    )

    # 4. Robotu Sahneye At (Spawn)
    spawn_entity = Node(package='gazebo_ros', executable='spawn_entity.py',
                        arguments=['-topic', 'robot_description', '-entity', 'imre_robot', '-z', '0.1'],
                        output='screen')

    # 5. [YENİ] Kontrolcüleri Otomatik Başlat (Spawner)
    # Bu olmazsa kamera motoru çalışmaz!
    
    joint_broad_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster"],
    )

    camera_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["camera_controller"],
    )

    # 6. Sıralama: Robot doğduktan SONRA kontrolcüleri başlat (Hata almamak için)
    # Bu mekanizma, robotun spawn olmasını bekler, sonra motorları açar.
    delayed_camera_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[camera_spawner],
        )
    )
    
    delayed_joint_broad_spawner = RegisterEventHandler(
        event_handler=OnProcessExit(
            target_action=spawn_entity,
            on_exit=[joint_broad_spawner],
        )
    )

    return LaunchDescription([
        rsp,
        gazebo,
        spawn_entity,
        delayed_joint_broad_spawner,
        delayed_camera_spawner
    ])
