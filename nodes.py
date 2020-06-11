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

class Cell:
    def __init__(self,idnum,i,j,w=10):
        self.id = idnum
        self.i = i
        self.j = j
        self.w = w
        self.visited = False
        self.obstacle = False
        self.walls = {"top":True,"bottom":True,"left":True,"right":True}
        self.neighbors = {"top":None,"bottom":None,"left":None,"right":None}
        self.color = None
        self.parent = None
        self.localgoal = None
        self.globalgoal = None


    def draw(self):
        x = self.i*self.w
        y = self.j*self.w
        if self.color:
            game.draw.rect(gameDisplay,self.color,(x,y,self.w,self.w))
        if self.walls["top"]:
            game.draw.line(gameDisplay,white,(x,y),(x+self.w,y))#top
        if self.walls["right"]:
            game.draw.line(gameDisplay,white,(x+self.w,y),(x+self.w,y+self.w))#right
        if self.walls["bottom"]:
            game.draw.line(gameDisplay,white,(x+self.w,y+self.w),(x,y+self.w))#bottom
        if self.walls["left"]:
            game.draw.line(gameDisplay,white,(x,y+self.w),(x,y))#left

    def makevisited(self,val):
        self.visited = val

    def getid(self):
        return self.id

    def checkneighbors(self,c,r):
        if self.i != 1:
            self.neighbors["left"]=(self.i-1,self.j)
        if self.i != c:
            self.neighbors["right"]=(self.i+1,self.j)
        if self.j != 1:
            self.neighbors["top"]=(self.i,self.j-1)
        if self.j != r:
            self.neighbors["bottom"]=(self.i,self.j+1)
        return self.neighbors

    def setobscolor(self):
        if self.obstacle:
            self.color = yellow
        else:
            self.color = None

    def setvisitedcolor(self):
        if self.visited:
            self.color = blue
        else:
            self.color = None


##class Node:
##    def __init__(self,idnum,i,j,w=10,color = red):
##        self.id = idnum
##        self.obstacle = False
##        self.visited = False
##        self.i = i
##        self.j = j
##        self.w = w
##        self.color = color
##
##    def draw(self):
##        x = self.i*self.w
##        y = self.j*self.w
##        game.draw.rect(gameDisplay,self.color,(x,y,self.w,self.w))



def findcellclicked(point,container):
    for c in container:
        if point[0] >= c.i*c.w and point[0] <= (c.i*c.w)+c.w and point[1] >= c.j*c.w and point[1] <= (c.j*c.w)+c.w:
            return c.id

def manhattan(a,b):
    return abs(a.i-b.i)+abs(a.j-b.j)

def cleangrid(grid,start,end):
    for a in grid:
        if a != start and a != end and a.obstacle==False:
            a.color = None

def A_star(grid,start,end,cols,rows):
    for x in grid:
        x.visited = False
        x.parent = None
        x.localgoal = float("inf")
        x.globalgoal = float("inf")

    currnode = start
    start.localgoal = 0
    start.globalgoal = manhattan(start,end)
    opennodes= []
    opennodes.append(start)

    while len(opennodes) != 0 and currnode != end:
        sorted(opennodes, key=lambda node: node.globalgoal)
        while len(opennodes) != 0 and opennodes[0].visited:
            opennodes[0].color = blue
            del opennodes[0]
        if len(opennodes) == 0:
            break
        currnode = opennodes[0]
        currnode.visited = True
        cn = currnode.checkneighbors(cols,rows)
        for n in cn:
            if cn[n]:
                if grid[(cn[n][1]-1)+((cn[n][0]-1)*rows)].visited == False and grid[(cn[n][1]-1)+((cn[n][0]-1)*rows)].obstacle == False:
                    opennodes.append(grid[(cn[n][1]-1)+((cn[n][0]-1)*rows)])
                lowergoal = currnode.localgoal + manhattan(currnode,grid[(cn[n][1]-1)+((cn[n][0]-1)*rows)])
                if lowergoal < grid[(cn[n][1]-1)+((cn[n][0]-1)*rows)].localgoal:
                    grid[(cn[n][1]-1)+((cn[n][0]-1)*rows)].parent = currnode
                    grid[(cn[n][1]-1)+((cn[n][0]-1)*rows)].localgoal = lowergoal
                    grid[(cn[n][1]-1)+((cn[n][0]-1)*rows)].globalgoal = grid[(cn[n][1]-1)+((cn[n][0]-1)*rows)].localgoal + manhattan(grid[(cn[n][1]-1)+((cn[n][0]-1)*rows)],end)
    return True
                
                
            
            
        
    
    
            



#mazewidth = None
#mazeheight = None


def gameLoop():
    startalg = False
    start = None
    end = None
    startpointset = False
    endpointset = False
    clicking = False
    released = False
    opposites = {"top":"bottom","bottom":"top","left":"right","right":"left"}
    current=None
    cn = None
    w = 20
    rows = 20
    cols = 40
    grid = []
    opennodes = {}
    closed = []
    #mazewidth = 500
    #mazeheight = 250
    visitedcells = None
##    maze = [0]*(mazewidth*mazeheight)
##    stack.append([0,0])
##    maze[0] = 1
##    visitedcells = 1
    cellnum = 0
    for x in range(1,cols+1):
        for y in range(1,rows+1):
            grid.append(Cell(cellnum,x,y,w))
            cellnum += 1
##    stack.append((1,1))
##    current=maze[0]
##    current.makevisited(True)
##    #maze[1].makevisited(True)
##    #maze[10].makevisited(True)
##    visitedcells = 1

##    while visitedcells < rows*cols:
##        cn = current.checkneighbors(cols,rows)
##        choice = random.choice([x for x in cn if cn[x] != None and maze[(cn[x][1]-1)+((cn[x][0]-1)*cols)].visited == False])
##        print(choice,cn[choice])
##        current.walls[choice]= False
##        stack.append(cn[choice])
##        current= maze[(cn[choice][1]-1)+((cn[choice][0]-1)*cols)]
##        current.makevisited(True)
##        toremove = opposites[choice]
##        current.walls[toremove] = False
##        visitedcells+=1

#grid[(currnode[1]-1)+((currnode[0]-1)*rows)]
##    start = grid[15]
##    start.color = red
##    end = grid[85]
##    end.color = green
##    opennodes[0]= (start.i,start.j)
##    came_from = {}
##    cost_so_far = {}
##    came_from[(start.i,start.j)] = None
##    cost_so_far[(start.i,start.j)] = 0

##    while len(opennodes) != 0:
##        lowestcost = min(opennodes)
##        currnode = opennodes[lowestcost]
##        del opennodes[lowestcost]
##        closed.append(currnode)
##
##        if grid[(currnode[1]-1)+((currnode[0]-1)*rows)] == end:
##            break
##        cn = grid[(currnode[1]-1)+((currnode[0]-1)*rows)].checkneighbors(cols,rows).values()
##        for x in cn:
##            if x and grid[(x[1]-1)+((x[0]-1)*rows)].obstacle == False:
##                new_cost = cost_so_far[currnode] + manhattan(grid[(currnode[1]-1)+((currnode[0]-1)*rows)],grid[(x[1]-1)+((x[0]-1)*rows)])
##                if x not in cost_so_far or new_cost < cost_so_far[x]:
##                    cost_so_far[x] = new_cost
##                    priority = new_cost + manhattan(grid[(x[1]-1)+((x[0]-1)*rows)],end)
##                    opennodes[priority] = x
##                    came_from[x]= currnode
##    #print(cost_so_far)
##    #print(opennodes)
##    before = came_from[(end.i,end.j)]
##    while before != (start.i,start.j):
##        print(before)
##        grid[(before[1]-1)+((before[0]-1)*rows)].color=green
##        before = came_from[before]
    
    
    
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
                if event.key == game.K_c:
                    startalg = True
                    cleangrid(grid,start,end)
                    A_star(grid,start,end,cols,rows)
                if event.key == game.K_LSHIFT:
                    startpointset = True
                if event.key == game.K_LCTRL:
                    endpointset = True
            if event.type == game.KEYUP:
                if event.key == game.K_LSHIFT:
                    startpointset = False
                if event.key == game.K_LCTRL:
                    endpointset = False
            if event.type == game.MOUSEBUTTONDOWN:
                clicking = True
            if event.type == game.MOUSEBUTTONUP:
                clickpoint = event.pos
                if startpointset:
                    if clickpoint[0] >= w and clickpoint[0] <= (cols*w)+w and clickpoint[1] >= w and clickpoint[1] <= (rows*w)+w:
                        newstart = findcellclicked(clickpoint,grid)
                        if start:
                            start.color = None
                        start = grid[newstart]
                        start.color = red
                        if startalg:
                            cleangrid(grid,start,end)
                            A_star(grid,start,end,cols,rows)
                elif endpointset:
                    if clickpoint[0] >= w and clickpoint[0] <= (cols*w)+w and clickpoint[1] >= w and clickpoint[1] <= (rows*w)+w:
                        newend = findcellclicked(clickpoint,grid)
                        if end:
                            end.color = None
                        end = grid[newend]
                        end.color = peach
                        if startalg:
                            cleangrid(grid,start,end)
                            A_star(grid,start,end,cols,rows)
                else:
                    if clickpoint[0] >= w and clickpoint[0] <= (cols*w)+w and clickpoint[1] >= w and clickpoint[1] <= (rows*w)+w:
                        newobs = findcellclicked(clickpoint,grid)
                        grid[newobs].obstacle = not grid[newobs].obstacle
                        grid[newobs].setobscolor()
                        if startalg:
                            cleangrid(grid,start,end)
                            A_star(grid,start,end,cols,rows)
                    
        gameDisplay.fill(black)


##        while len(opennodes) != 0 and startalg:
##            lowestcost = min(opennodes)
##            currnode = opennodes[lowestcost]
##            del opennodes[lowestcost]
##            closed.append(currnode)
##
##            if grid[(currnode[1]-1)+((currnode[0]-1)*rows)] == end:
##                break
##            cn = grid[(currnode[1]-1)+((currnode[0]-1)*rows)].checkneighbors(cols,rows).values()
##            for x in cn:
##                if x and grid[(x[1]-1)+((x[0]-1)*rows)].obstacle == False:
##                    new_cost = cost_so_far[currnode] + manhattan(grid[(currnode[1]-1)+((currnode[0]-1)*rows)],grid[(x[1]-1)+((x[0]-1)*rows)])
##                    if x not in cost_so_far or new_cost < cost_so_far[x]:
##                        cost_so_far[x] = new_cost
##                        priority = new_cost + manhattan(grid[(x[1]-1)+((x[0]-1)*rows)],end)
##                        opennodes[priority] = x
##                        came_from[x]= currnode
                    
        #print(cost_so_far)
        #print(opennodes)
##        if startalg:
##            before = came_from[(end.i,end.j)]
##            while before != (start.i,start.j):
##                grid[(before[1]-1)+((before[0]-1)*rows)].color=green
##                before = came_from[before]



        if end != None:
            p = end
            while p.parent != None:
                if p.parent != start:
                    p.parent.color = green
                p = p.parent
                
        for a in range(0,len(grid)):
            grid[a].draw()


        

        game.display.update()
                
        clock.tick(fps)
    
    game.quit()
    quit()
        
game_start()







