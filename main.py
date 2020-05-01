import pygame
import map 
from settings import *
import simulation

pygame.init()

# move para os settings
display_width = 1100
display_height = 650
gameDisplay = pygame.display.set_mode((display_width,display_height))
pygame.display.set_caption('Vehicle Smart Grid based on a Multi-Agent System')

map1 = map.map()
#map1.reload_frame()

Globallastcount, Globalbenfetched = -1, False
counter, text = simulation_time, "time to end: "+str(simulation_time).rjust(3)
text_nr_vehicles = str(nr_vehicles).rjust(3)
text_nr_stations = str(nr_stations).rjust(3)
text_nr_priority_vehicles = str(nr_priority_vehicles).rjust(3)
text_nr_disasters = str(nr_disasters).rjust(3)
pygame.time.set_timer(pygame.USEREVENT, 1000)
font = pygame.font.SysFont('Consolas', 30)
smallText = pygame.font.Font("freesansbold.ttf",20)

crashed = False
Globalstart = False
black = (0,0,0)
white = (245,245,245)
red = (200,0,0)
green = (0,200,0)
bright_red = (255,0,0)
bright_green = (0,255,0)

# add save the las image 
mapImg = pygame.image.load(place+'.png')

def text_objects(text, font):
    textSurface = font.render(text, True, black)
    return textSurface, textSurface.get_rect()

def dummymap():
    resultout = map1.reload_frame()
    #maybe add if active simulation
    mapImg1 = pygame.image.fromstring(resultout[0],resultout[1], "RGB")

    x =  (display_width * 0.25)
    y = 14 #(display_height * 0.0)
    gameDisplay.blit(mapImg, (x,y))


def map():
    resultout = map1.reload_frame()
    #maybe add if active simulation
    mapImg1 = pygame.image.fromstring(resultout[0],resultout[1], "RGB")
    x =  (display_width * 0.25)
    y = 14 #(display_height * 0.0)
    gameDisplay.blit(mapImg1, (x,y))

def simulation_info():

    gameDisplay.blit(font.render(text, 
    True, (0, 0, 0)), (display_width * 0.03, display_height * 0.03))

    gameDisplay.blit(font.render("Vehicles: "+ text_nr_vehicles, 
    True, (0, 0, 0)), (display_width * 0.03, display_height * 0.15))

    gameDisplay.blit(font.render("Stations: "+ text_nr_stations, 
    True, (0, 0, 0)), (display_width * 0.03, display_height * 0.2))

    gameDisplay.blit(font.render("Priority vehicles: "+ text_nr_priority_vehicles, 
    True, (0, 0, 0)), (display_width * 0.03, display_height * 0.25))

    gameDisplay.blit(font.render("Power outages: "+ text_nr_disasters, 
    True, (0, 0, 0)), (display_width * 0.03, display_height * 0.3))

def check_start_stop(start, count, lastcount):
    global Globallastcount, Globalstart

    x = display_width * 0.03
    x1 = x +100
    y =  display_height * 0.35

    if(start and lastcount != count):
        if x1+100 > mouse[0] > x1 and y+50 > mouse[1] > y:
            pygame.draw.rect(gameDisplay, bright_red,(x1,y,100,50))
            Globalstart = False
            Globallastcount = count
        else:
            pygame.draw.rect(gameDisplay, red,(x1,y,100,50))
        textSurf, textRect = text_objects("Stop", smallText)
        textRect.center = ( (x1+(100/2)), (y+(50/2)) )
        gameDisplay.blit(textSurf, textRect)
    else:
        if x+100 > mouse[0] > x and y+50 > mouse[1] > y:
            pygame.draw.rect(gameDisplay, bright_green,(x,y,100,50))
            Globalstart = True
        else:
            pygame.draw.rect(gameDisplay, green,(x,y,100,50))
        textSurf, textRect = text_objects("Start", smallText)
        textRect.center = ( (x+(100/2)), (y+(50/2)) )
        gameDisplay.blit(textSurf, textRect)
    
""" 
    if 550+100 > mouse[0] > 550 and 450+50 > mouse[1] > 450:
        pygame.draw.rect(gameDisplay, bright_red,(550,450,100,50))
        start = False
    else:
        pygame.draw.rect(gameDisplay, red,(550,450,100,50)) """



clock = pygame.time.Clock()

gameDisplay.fill(white)
while not crashed:
    for event in pygame.event.get():
        mouse = pygame.mouse.get_pos()

        #if event.type == pygame.MOUSEBUTTONUP:
        #print(Globalstart)
        
        if event.type == pygame.USEREVENT:
            
              
            if counter >=0 and Globalstart: 
                gameDisplay.fill(white)
                counter -= 1
                text = "time to end: "+str(counter).rjust(3) if counter > 0 else 'Simulation ended' 
                #map1.reload_frame()
                map()
                Globalbenfetched = False
            else:
                if not Globalbenfetched:
                    map()
                    Globalbenfetched = True
            simulation_info()
            
            pygame.display.flip()
            #simulate
            #if (counter == 0):
                #Show graph results


        
            

        
        #if ended restart simulation todo
        

        

        check_start_stop(Globalstart,counter,Globallastcount)
        if event.type == pygame.QUIT:
            crashed = True

    pygame.display.update()
    clock.tick(60)

pygame.quit()
quit()