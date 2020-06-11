import pygame as game
import pygame.gfxdraw
from dataclasses import dataclass
import random
import math

game.init()

#GLOBALS
#color palette imported from pico-8
white = (255,241,232) #FFF1E8
black = (0,0,0) #000000
brown = (171, 82, 54) #AB5236
darkgray = (95, 87, 79) #5F574F
litegray = (194, 195, 199) #C2C3C7
red = (255,0,77) #FF004D
orange = (255, 163, 0) #FFA300
yellow = (255, 236, 39) #FFEC27
green = (0,228,54) #00E436
darkgreen = (0, 135, 81) #008751
blue = (41,173,255) #29ADFF
indigo = (131, 118, 156) #83769C
darkblue = (29,43,83) #1D2B53
darkpurp = (126, 37, 83) #7E2553
pink = (255, 119, 168) #FF77A8
peach = (255, 204, 170) #FFCCAA

#window size and various variables
windx=256
windy=256


gameDisplay = game.display.set_mode((windx,windy))
game.display.set_caption('Maze') 
clock=game.time.Clock() #clock variable
fps=20 #self explanatory

#fonts
font = game.font.SysFont(None, 25) #default font for now
smfont = game.font.SysFont("comicsansms", 25)
medfont = game.font.SysFont("comicsansms", 50)
lgfont = game.font.SysFont("comicsansms", 85)

def game_start():
    intro = True
    while intro:
        for event in game.event.get():
            if event.type == game.QUIT:
                game.quit()
                quit()
            if event.type == game.KEYDOWN:
                if event.key == game.K_q or event.key == game.K_ESCAPE:
                    game.quit()
                    quit()
                elif event.key == game.K_c:
                    gameLoop()
        gameDisplay.fill(white)
        screen_message('Welcome to the Maze', red, -50)
        screen_message('Press c to start playing or q to quit', black)
        screen_message('Use the arrow keys to move around', red, 50)
        game.display.update()
        clock.tick(5)

def pause():
    paused = True
    screen_message("Paused", black)
    screen_message("Press c to continue or q to quit.",black,50)
    game.display.update()
    while paused:
        for event in game.event.get():
            if event.type == game.QUIT:
                game.quit()
                quit()
            if event.type == game.KEYDOWN:
                if event.key == game.K_c:
                    paused = False
                elif event.key == game.K_q or event.key == game.K_ESCAPE:
                    game.quit()
                    quit()
        #gameDisplay.fill(white)
        clock.tick(5)

def text_objects(text,color):
    textsurface = font.render(text, True, color)
    return textsurface, textsurface.get_rect()

def screen_message(msg,color,y_displace=0):
    textsurf, textrect = text_objects(msg,color)
##    screen_text = font.render(msg,True,color)
##    gameDisplay.blit(screen_text,[windx/2, windy/2])
    textrect.center = (windx/2),(windy/2)+y_displace
    gameDisplay.blit(textsurf,textrect)

def drawWireModel(model,x,y,r,s,c):
    verts = len(model)
    tformed = [[None,None]]*verts

    for i in range(0,verts):
        xcord = model[i][0]*math.cos(r) - model[i][1]*math.sin(r)
        ycord = model[i][0]*math.sin(r) + model[i][1]*math.cos(r)
        tformed[i]=[xcord,ycord]

    for i in range(0,verts):
        tformed[i][0] = tformed[i][0]*s
        tformed[i][1] = tformed[i][1]*s

    for i in range(0,verts):
        tformed[i][0] = tformed[i][0]+x
        tformed[i][1] = tformed[i][1]+y

    for i in range(0,verts+1):
        j = i + 1
        game.draw.line(gameDisplay,c,(tformed[i%verts][0],tformed[i%verts][1]),(tformed[j%verts][0],tformed[j%verts][1]))


def PerlinNoise1D(count,seed,octaves,bias,out):
    for x in range(0,count):
        noise = 0.0
        scale = 1.0
        scaleacc = 0.0
        for y in range(0,octaves):
            pitch = count >> y
            sample = (x//pitch)*pitch
            sample2 = (sample+pitch) % count
            blend = float(x-sample)/float(pitch)
            samp = (1.0-blend)*seed[sample]+blend*seed[sample2]
            noise += samp*scale
            scaleacc += scale
            scale = scale/bias
        out[x] = noise/scaleacc
    return out
    

def gameLoop():
    outputsize = 256
    seedarray = [random.random() for x in range(0,outputsize)]
    perlinNoise = [0]*outputsize

    octavecount = 1
    scalebias = 2.0
    
    
    
    gameExit = False
    gameOver = False
    while not gameExit:
        while gameOver == True:
            gameDisplay.fill(white)
            screen_message('Game Over', red, -50)
            screen_message('You suck, press c to play again or q to quit, bitch', black)
            game.display.update()

            for event in game.event.get():
                if event.type == game.QUIT:
                    gameExit = True
                    gameOver = False
                if event.type == game.KEYDOWN:
                    if event.key == game.K_q or event.key == game.K_ESCAPE:
                        gameExit = True
                        gameOver = False
                    elif event.key == game.K_c:
                        gameLoop()

        for event in game.event.get():
            if event.type == game.QUIT:
                gameExit = True
            if event.type == game.KEYDOWN:
                if event.key == game.K_p:
                    pause()
            if event.type == game.KEYUP:
                if event.key == game.K_a:
                    scalebias -= .2
                if event.key == game.K_s:
                    scalebias += .2
                if event.key == game.K_ESCAPE:
                    seedarray = [random.random() for x in range(0,outputsize)]
                if event.key == game.K_SPACE:
                    octavecount += 1
                    if octavecount == 9:
                        octavecount = 1
                    PerlinNoise1D(outputsize,seedarray,octavecount,scalebias,perlinNoise)
                    

                    
        gameDisplay.fill(black)

        if scalebias < .2:
            scalebias = .2

        perlinNoise = PerlinNoise1D(outputsize,seedarray,octavecount,scalebias,perlinNoise)
        for x in range(0,outputsize):
            y = -(perlinNoise[x]* float(windy)/2.0)+float(windy)/2.0
            for f in range(int(y),int(windy/2)):
                game.gfxdraw.pixel(gameDisplay,x,f,green)


        game.display.update()
                
        clock.tick(fps)
    
    game.quit()
    quit()
        
game_start()
