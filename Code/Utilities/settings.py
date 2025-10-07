# game setup
WIDTH    = 1280	
HEIGTH   = 720
FPS      = 60
TILESIZE = 64

# ui
BAR_HEIGHT = 20
HEALTH_BAR_WIDTH = 200
ITEM_BOX_SIZE = 80
UI_FONT = "Assets/Fonts/joystix.ttf"
UI_FONTSIZE = 25

# enemies
tanks_data =  {
   'enemyTankType1':{'health': 2, 'resistance': 3, 'damage':1,'attack_sound':'Assets/Audio/attack/slash.wav', 'speed': 3, 'bullet_speed': 4, 'attack_cooldown': 1300, 'attack_radius': 400, 'notice_radius': 600},
   'enemyTankType2':{'health': 3, 'resistance': 3, 'damage':1,'attack_sound':'Assets/Audio/attack/slash.wav', 'speed': 3, 'bullet_speed': 6, 'attack_cooldown': 1300, 'attack_radius': 400, 'notice_radius': 600},
   'enemyTankType3':{'health': 4, 'resistance': 3, 'damage':1,'attack_sound':'Assets/Audio/attack/slash.wav', 'speed': 6, 'bullet_speed': 6, 'attack_cooldown': 1300, 'attack_radius': 400, 'notice_radius': 600},
   'enemyTankType4':{'health': 5, 'resistance': 3, 'damage':1,'attack_sound':'Assets/Audio/attack/slash.wav', 'speed': 3, 'bullet_speed': 4, 'attack_cooldown': 1300, 'attack_radius': 400, 'notice_radius': 600},
   'enemyTankType5':{'health': 10, 'resistance': 3, 'damage':1,'attack_sound':'Assets/Audio/attack/slash.wav', 'speed': 3, 'bullet_speed': 6, 'attack_cooldown': 1300, 'attack_radius': 400, 'notice_radius': 600}
}

# power ups
power_up_data =  {
   'shield':{'duration_time': 30, 'effect': 0, 'sound':'Assets/Audio/Fire.wav'},
   'shoot_upgrade':{'duration_time': 20, 'effect': 2, 'sound':'Assets/Audio/Fire.wav'},
   'clock':{'duration_time': 10, 'effect': 10, 'sound':'Assets/Audio/Fire.wav'},
}

# bonuses
bonus_data =  {
   'wrench':{'sound':'Assets/Audio/Fire.wav'},
   'machine_gun':{'duration_time': 20, 'sound':'Assets/Audio/Fire.wav'},
   'fortress_shield':{'duration_time': 10, 'sound':'Assets/Audio/Fire.wav'},
   'bomb':{'duration_time': 1,'sound':'Assets/Audio/Fire.wav'}
}

# structures
estructure_data =  {
   'fortress':{'health': 10},
}