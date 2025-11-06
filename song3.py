import pygame
from pygame import mixer
import os

PLAYER_IMAGE_PATH = r"C:\Users\Almas\pp2_2025\TSIS7\2ndtask\musicplayer.jpg"
MUSIC_FILES = [
    r"C:\Users\Almas\pp2_2025\TSIS7\2ndtask\music1.mp3", 
    r"C:\Users\Almas\pp2_2025\TSIS7\2ndtask\music2.mp3", 
    r"C:\Users\Almas\pp2_2025\TSIS7\2ndtask\music3.mp3"  
]

pygame.init()
mixer.init()

w, h = 800, 600
screen = pygame.display.set_mode((w, h))
pygame.display.set_caption("Pygame Music Player | Enter/Space/Left/Right/Up/Down")

current_track_index = 0
pause = True 
current_position_s = 0.0 
SEEK_AMOUNT = 5.0 


def load_and_play_track(index, start_pos=0.0):
    global current_track_index, current_position_s, pause
    
    if len(MUSIC_FILES) == 0:
        return
        
    if index < 0:
        index = len(MUSIC_FILES) - 1
    elif index >= len(MUSIC_FILES):
        index = 0
        
    current_track_index = index
    current_position_s = max(0.0, start_pos)
    
    mixer.music.stop() 
    
    try:
        mixer.music.load(MUSIC_FILES[current_track_index])
        mixer.music.play(-1, start=current_position_s)
        
        track_name = os.path.basename(MUSIC_FILES[current_track_index])
        pygame.display.set_caption(f"Pygame Music Player | Играет: {track_name}")
        pause = False
        
    except pygame.error as e:
        print(f"Error loading track: {e}")

def handle_seek(direction):
    global current_position_s, pause
    
    if mixer.music.get_busy() or pause:
        
        if not pause:
             current_position_s += mixer.music.get_pos() / 1000.0 
             
        if direction == 'BACK':
            current_position_s -= SEEK_AMOUNT
        elif direction == 'FORWARD':
            current_position_s += SEEK_AMOUNT
            
        current_position_s = max(0.0, current_position_s)

        mixer.music.stop()
        mixer.music.play(-1, start=current_position_s)
        
        if pause:
            mixer.music.pause()

try:
    player_img = pygame.image.load(PLAYER_IMAGE_PATH)
    mic = pygame.transform.scale(player_img, (w, h))
except pygame.error:
    mic = pygame.Surface((w, h))
    mic.fill((0, 0, 0))

if len(MUSIC_FILES) > 0:
    load_and_play_track(current_track_index, start_pos=0.0)
    mixer.music.pause() 

while True:
    screen.blit(mic, (0, 0))
    pygame.display.update()

    for event in pygame.event.get():    
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
            
        if event.type == pygame.KEYDOWN:
            
            
            if event.key == pygame.K_RETURN:
                if not mixer.music.get_busy() and not pause:
                    load_and_play_track(current_track_index)
                elif pause:
                    mixer.music.unpause()
                    pause = False
        
            elif event.key == pygame.K_SPACE:
                if mixer.music.get_busy() or pause:
                    pause = not pause
                    if pause:
                        current_position_s += mixer.music.get_pos() / 1000.0
                        mixer.music.pause()
                    else:
                        mixer.music.unpause()

            elif event.key == pygame.K_LEFT:
                handle_seek('BACK')

            elif event.key == pygame.K_RIGHT:
                handle_seek('FORWARD')
                
            elif event.key == pygame.K_DOWN:
                load_and_play_track(current_track_index - 1)

            elif event.key == pygame.K_UP:
                load_and_play_track(current_track_index + 1)