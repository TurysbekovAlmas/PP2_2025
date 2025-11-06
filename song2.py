import pygame
from pygame import mixer
import time 
pygame.init()
mixer.init()

w, h = 800, 600
screen = pygame.display.set_mode((w, h))
pygame.display.set_caption("Pygame Music Player (Enter, Space, Left/Right)")
player = pygame.image.load(r"C:\Users\Almas\pp2_2025\TSIS7\2ndtask\musicplayer.jpg")
mic = pygame.transform.scale(player, (w, h))

music = mixer.music.load(r"C:\Users\Almas\pp2_2025\TSIS7\2ndtask\music3.mp3")


pause = False

current_position_s = 0.0 
SEEK_AMOUNT = 5.0 


while True:
   
    screen.blit(mic, (0, 0))
    pygame.display.update()

    for event in pygame.event.get():    
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()
            
        if event.type == pygame.KEYDOWN:
            
            
            if event.key == pygame.K_RETURN:
                
                mixer.music.play(-1, start=current_position_s) 
                pause = False
            
      
            elif event.key == pygame.K_SPACE:
                pause = not pause
                if pause:
                   
                    current_position_s = mixer.music.get_pos() / 1000.0 
                    mixer.music.pause()
                else:
                    
                    mixer.music.unpause()
            
            elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                
                if mixer.music.get_busy() or pause:
                    
                    if not pause:
                         
                         current_position_s += mixer.music.get_pos() / 1000.0 
                         
                    if event.key == pygame.K_LEFT:
                        current_position_s -= SEEK_AMOUNT 
                        
                    elif event.key == pygame.K_RIGHT:
                        current_position_s += SEEK_AMOUNT 
                     
                    current_position_s = max(0.0, current_position_s)

                    mixer.music.stop()
                    
                  
                    mixer.music.play(-1, start=current_position_s)
                   
                    if pause:
                        mixer.music.pause()