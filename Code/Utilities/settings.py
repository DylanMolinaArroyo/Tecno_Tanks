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

# enemy
tanks_data =  {
   'enemyTankType1':{'health': 2, 'damage':1,'attack_sound':'Assets/Audio/attack/slash.wav', 'speed': 3, 'bullet_speed': 4, 'resistance': 3, 'attack_radius': 400, 'notice_radius': 1500},
   'enemyTankType2':{'health': 3, 'damage':1,'attack_sound':'Assets/Audio/attack/slash.wav', 'speed': 3, 'bullet_speed': 6, 'resistance': 3, 'attack_radius': 400, 'notice_radius': 1500},
   'enemyTankType3':{'health': 4, 'damage':1,'attack_sound':'Assets/Audio/attack/slash.wav', 'speed': 6, 'bullet_speed': 6, 'resistance': 3, 'attack_radius': 400, 'notice_radius': 1500},
   'enemyTankType4':{'health': 5, 'damage':1,'attack_sound':'Assets/Audio/attack/slash.wav', 'speed': 3, 'bullet_speed': 4, 'resistance': 3, 'attack_radius': 400, 'notice_radius': 1500},
   'enemyTankType5':{'health': 10, 'damage':1,'attack_sound':'Assets/Audio/attack/slash.wav', 'speed': 3, 'bullet_speed': 6, 'resistance': 3, 'attack_radius': 400, 'notice_radius': 1500}
}

"""
Tipo 1: lento, disparo lento, 20 HP.
o Tipo 2: lento, disparo rápido, 30 HP.
o Tipo 3: rápido, disparo rápido, 40 HP.
o Tipo 4: lento, disparo lento, 50 HP.
o Definitivo: lento, disparo rápido, 100 HP, requiere daño combinado
"""

power_up_data =  {
   'shield':{'duration_time': 30, 'effect': 0, 'sound':'Assets/Audio/Fire.wav'},
   'shoot_upgrade':{'duration_time': 20, 'effect': 2, 'sound':'Assets/Audio/Fire.wav'},
   'clock':{'duration_time': 10, 'effect': 10, 'sound':'Assets/Audio/Fire.wav'},
}

bonus_data =  {
   'wrench':{'sound':'Assets/Audio/Fire.wav'},
   'machine_gun':{'duration_time': 20, 'sound':'Assets/Audio/Fire.wav'},
   'fortress_shield':{'duration_time': 10, 'sound':'Assets/Audio/Fire.wav'},
   'bomb':{'sound':'Assets/Audio/Fire.wav'}
}

estructure_data =  {
   'wall':{'health': 10, 'sound':'Assets/Audio/attack/slash.wav'},
   'fortress':{'health': 3, 'sound':'Assets/Audio/attack/slash.wav'},
}