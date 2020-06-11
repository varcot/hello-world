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
windx=1200
windy=600


gameDisplay = game.display.set_mode((windx,windy))
game.display.set_caption('Circles') 
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
        screen_message('Welcome to Circles', red, -50)
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


@dataclass
class Ball:
    x: float
    y: float
    dx: float
    dy: float
    ax: float
    ay: float
    r: float
    mass: float
    iden: int
    color: tuple
    selected: bool

##modelcircle = []
##modelcircle.append([0.0,0.0])
##points = 20
##for i in range(0,points):
##    modelcircle.append([math.cos(i/float(points-1)*2.0*3.14159),math.sin(i/float(points-1)*2.0*3.14159)])
##                      


def addball(container,x,y,r=5.0):  
    b = Ball(x,y,0,0,0,0,r,r*10.0,len(container),white,False)
    container.append(b)

def updateballs(container):
    for x in container:
        updateball(x)

def updateball(obj):
    obj.x += obj.dx
    obj.y += obj.dy
    if obj.y >= windy or obj.y <= 0:
        obj.dy = -obj.dy
    if obj.x >= windx or obj.x <= 0:
        obj.dx = -obj.dx

def isoverlap(x,y,r,x2,y2,r2):
    if abs((x-x2)*(x-x2)+(y-y2)*(y-y2)) <= (r+r2)*(r+r2):
        return True

def clickinrange(pos,container):
    for x in container:
        if math.sqrt((pos[0]-x.x)*(pos[0]-x.x)+(pos[1]-x.y)*(pos[1]-x.y)) < x.r:
            return x
    return None

def showmouse(clickstatus):
    if clickstatus:
        return game.mouse.get_pos()
    else:
        return None
    

                       
def gameLoop():
    launch = None
    whichbutton = None
    currselect = None
    currpos = None
    prevpos = None
    posdx = None
    posdy = None
    bagofballs = []
    modelcircle = []
    modelcircle.append([0.0,0.0])
    points = 20
    for i in range(0,points):
        modelcircle.append([math.cos(i/float(points-1)*2.0*3.14159),math.sin(i/float(points-1)*2.0*3.14159)])
    defrad = 10
    addball(bagofballs,windx*.25,windy*.5,random.uniform(5,20))
    addball(bagofballs,windx*.75,windy*.5,random.uniform(5,20))
    addball(bagofballs,windx*.35,windy*.5,random.uniform(5,20))
    addball(bagofballs,windx*.65,windy*.5,random.uniform(5,20))
    addball(bagofballs,windx*.25,windy*.25,random.uniform(5,20))
    addball(bagofballs,windx*.75,windy*.25,random.uniform(5,20))
    addball(bagofballs,windx*.35,windy*.25,random.uniform(5,20))
    addball(bagofballs,windx*.65,windy*.25,random.uniform(5,20))
    addball(bagofballs,windx*.25,windy*.35,random.uniform(5,20))
    addball(bagofballs,windx*.75,windy*.35,random.uniform(5,20))
    addball(bagofballs,windx*.35,windy*.35,random.uniform(5,20))
    addball(bagofballs,windx*.65,windy*.35,random.uniform(5,20))
    addball(bagofballs,windx*.25,windy*.65,random.uniform(5,20))
    addball(bagofballs,windx*.75,windy*.65,random.uniform(5,20))
    addball(bagofballs,windx*.35,windy*.65,random.uniform(5,20))
    addball(bagofballs,windx*.65,windy*.65,random.uniform(5,20))
    
    gameExit = False
    gameOver = False
    clicking = False
    


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
            if event.type == game.MOUSEBUTTONDOWN:
                clicking = True
                currselect = clickinrange(event.pos,bagofballs)
            if event.type == game.MOUSEBUTTONUP:
                clicking = False
                #print(event.pos)
                    
        gameDisplay.fill(black)


        currpos = showmouse(clicking)
        if currpos:
            whichbutton = game.mouse.get_pressed()
        if currpos and currselect and whichbutton[0]:
            currselect.x = currpos[0]
            currselect.y = currpos[1]
        if currpos and currselect and whichbutton[2]:
            launch = 1
        elif not currpos and launch==1:
            currselect.dx = 0.5 * (currselect.x-float(game.mouse.get_pos()[0]))
            currselect.dy = 0.5 * (currselect.y-float(game.mouse.get_pos()[1]))
            launch = None
        elif not currpos:
            currselect = None
            

        for b in bagofballs:
            drawWireModel(modelcircle,b.x,b.y,math.atan2(b.dy,b.dx),b.r,b.color)
            b.ax = -b.dx * .15
            b.ay = -b.dy * .15
            b.dx += b.ax
            b.dy += b.ay
            b.x += b.dx
            b.y += b.dy
            if b.x < 0:
                b.x += float(windx)
            if b.x > windx:
                b.x -= float(windx)
            if b.y < 0:
                b.y += float(windy)
            if b.y > windy:
                b.y -= float(windy)

        collidingpairs = []
        for x in bagofballs:
            for y in bagofballs:
                if x.iden != y.iden:
                    if isoverlap(x.x,x.y,x.r,y.x,y.y,y.r):
                        #collidingpairs.append([x,y])
                        dist = math.sqrt((x.y-y.y)*(x.y-y.y)+(x.x-y.x)*(x.x-y.x))
                        overlap = .5*(dist-x.r-y.r)
                        x.x -= overlap *(x.x-y.x)/dist
                        x.y -= overlap *(x.y-y.y)/dist
                        y.x += overlap *(x.x-y.x)/dist
                        y.y += overlap *(x.y-y.y)/dist
##                    elif [x,y] in collidingpairs and not isoverlap(x.x,x.y,x.r,y.x,y.y,y.r):
##                        collidingpairs.remove([x,y])
                
        #updateballs(bagofballs)

        for p in collidingpairs:
            p1 = p[0]
            p2 = p[1]
            game.draw.line(gameDisplay,red,(p[0].x,p[0].y),(p[1].x,p[1].y))
            dist = math.sqrt((p1.y-p2.y)*(p1.y-p2.y)+(p1.x-p2.x)*(p1.x-p2.x))
            nx = (p2.x - p1.x)/dist
            ny = (p2.y - p1.y)/dist
            tx = -ny
            ty = nx
            dptan1 = p1.dx * tx +p1.dy *ty
            dptan2 = p2.dx * tx +p2.dy *ty
            dpnorm1 = p1.dx * nx + p1.dy * ny
            dpnorm2 = p2.dx * nx + p2.dy * ny
            m1 = (dpnorm1 * (p1.mass-p2.mass) + 2.0 * p2.mass * dpnorm2)/(p1.mass + p2.mass)
            m2 = (dpnorm2 * (p2.mass-p1.mass) + 2.0 * p1.mass * dpnorm1)/(p1.mass + p2.mass)
            p1.dx = tx * dptan1 + nx * m1
            p1.dy = ty * dptan1 + ny * m1
            p2.dx = tx * dptan2 + nx * m2
            p2.dy = ty * dptan2 + ny * m2
            
            
            
            
            
                
        
##        for b in bagofballs:
##            drawWireModel(modelcircle,b.x,b.y,math.atan2(b.dy,b.dx),b.r,b.color)

##        for a in collidingpairs:
####            if not isoverlap(a[0].x,a[0].y,a[0].r,a[1].x,a[1].y,a[1].r):
####                collidingpairs.remove(a)
##            game.draw.line(gameDisplay,red,(a[0].x,a[0].y),(a[1].x,a[1].y))

        if currselect:
            game.draw.line(gameDisplay,blue,(currselect.x,currselect.y),(game.mouse.get_pos()[0],game.mouse.get_pos()[1]))

        game.display.update()
                
        clock.tick(fps)
    
    game.quit()
    quit()




game_start()

    
