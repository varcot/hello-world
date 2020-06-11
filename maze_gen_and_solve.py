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
        self.walls = {"top":True,"bottom":True,"left":True,"right":True}
        self.neighbors = {"top":None,"bottom":None,"left":None,"right":None}
        self.color = None
        self.parent = None
        self.localgoal = None
        self.globalgoal = None
        self.explored = False

    def declare_self(self):
        print("my id is: " + str(self.id))
        print("my col number is: " + str(self.i))
        print("my row number is: " + str(self.j))
        print("my width is: " + str(self.w))
        print("Visited? should be true once maze is done: " + str(self.visited))
        print("my wall statuses are: " + str(self.walls))
        print("my neighbors are: " + str(self.neighbors))
        print("my color is: " + str(self.color))
        if self.parent:
            print("my parent is: " + str(self.parent.i)+","+str(self.parent.j))
        print("the astar has looked at me: " + str(self.explored))

    def draw(self):
        x = self.i*self.w
        y = self.j*self.w
        if self.color and self.visited:
            game.draw.rect(gameDisplay,self.color,(x,y,self.w,self.w))
        if self.visited and not self.color:
            game.draw.rect(gameDisplay,litegray,(x,y,self.w,self.w))
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

def findcellclicked(point,container):
    for c in container:
        if point[0] >= c.i*c.w and point[0] <= (c.i*c.w)+c.w and point[1] >= c.j*c.w and point[1] <= (c.j*c.w)+c.w:
            return c.id

def manhattan(a,b):
    return abs(a.i-b.i)+abs(a.j-b.j)

def cleangrid(grid,start,end):
    for a in grid:
        if a != start and a != end:
            a.color = None

def A_star(grid,start,end,cols,rows):
    opposites = {"top":"bottom","bottom":"top","left":"right","right":"left"}
    for x in grid:
        x.explored = False
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
        while len(opennodes) != 0 and opennodes[0].explored:
            #opennodes[0].color = blue
            del opennodes[0]
        if len(opennodes) == 0:
            break
        currnode = opennodes[0]
        currnode.explored = True
        cn = currnode.checkneighbors(cols,rows)
        for n in cn:
            if cn[n]:
                if currnode.walls[n] == False and grid[(cn[n][1]-1)+((cn[n][0]-1)*rows)].explored == False:
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
    mazedone = False
    opposites = {"top":"bottom","bottom":"top","left":"right","right":"left"}
    current=None
    cn = None
    w = 20
    rows = 25
    cols = 50
    maze = []
    #mazewidth = 500
    #mazeheight = 250
    visitedcells = None
    stack = []
##    maze = [0]*(mazewidth*mazeheight)
##    stack.append([0,0])
##    maze[0] = 1
##    visitedcells = 1
    cellnum = 0
    for x in range(1,cols+1):
        for y in range(1,rows+1):
            cell = Cell(cellnum,x,y,w)
            maze.append(cell)
            cellnum += 1
    stack.append((1,1))
    current=maze[0]
    current.makevisited(True)
    #maze[1].makevisited(True)
    #maze[10].makevisited(True)
    visitedcells = 1

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
                    cleangrid(maze,start,end)
                    A_star(maze,start,end,cols,rows)
                if event.key == game.K_LSHIFT:
                    startpointset = True
                if event.key == game.K_LCTRL:
                    endpointset = True
            if event.type == game.KEYUP:
                if event.key == game.K_LSHIFT:
                    startpointset = False
                if event.key == game.K_LCTRL:
                    endpointset = False
            if event.type == game.MOUSEBUTTONUP:
                clickpoint = event.pos
##                if clickpoint[0] >= w and clickpoint[0] <= (cols*w)+w and clickpoint[1] >= w and clickpoint[1] <= (rows*w)+w:
##                    cell_loc = findcellclicked(clickpoint,maze)
##                    maze[cell_loc].declare_self()
                if startpointset and mazedone:
                    if clickpoint[0] >= w and clickpoint[0] <= (cols*w)+w and clickpoint[1] >= w and clickpoint[1] <= (rows*w)+w:
                        newstart = findcellclicked(clickpoint,maze)
                        if start:
                            start.color = None
                        start = maze[newstart]
                        start.color = red
                        if startalg:
                            cleangrid(maze,start,end)
                            A_star(maze,start,end,cols,rows)
                elif endpointset and mazedone:
                    if clickpoint[0] >= w and clickpoint[0] <= (cols*w)+w and clickpoint[1] >= w and clickpoint[1] <= (rows*w)+w:
                        newend = findcellclicked(clickpoint,maze)
                        if end:
                            end.color = None
                        end = maze[newend]
                        end.color = peach
                        if startalg:
                            cleangrid(maze,start,end)
                            A_star(maze,start,end,cols,rows)
                    
        gameDisplay.fill(black)

##        cn = current.checkneighbors(cols,rows)
##        choice = random.choice([x for x in cn if cn[x] != None and maze[(cn[x][1]-1)+((cn[x][0]-1)*rows)].visited == False])
##        current.walls[choice]= False
##        stack.append(cn[choice])
##        current= maze[(cn[choice][1]-1)+((cn[choice][0]-1)*rows)]
##        current.makevisited(True)
##        toremove = opposites[choice]
##        current.walls[toremove] = False
##        visitedcells+=1

        if visitedcells < rows*cols:
            cn = current.checkneighbors(cols,rows)
            while len([x for x in cn if cn[x] != None and maze[(cn[x][1]-1)+((cn[x][0]-1)*rows)].visited == False]) == 0:
                stack.pop()
                current = maze[(stack[-1][1]-1)+((stack[-1][0]-1)*rows)]
                cn = current.checkneighbors(cols,rows)
            choice = random.choice([x for x in cn if cn[x] != None and maze[(cn[x][1]-1)+((cn[x][0]-1)*rows)].visited == False])
            current.walls[choice]= False
            stack.append(cn[choice])
            current= maze[(cn[choice][1]-1)+((cn[choice][0]-1)*rows)]
            current.makevisited(True)
            toremove = opposites[choice]
            current.walls[toremove] = False
            visitedcells+=1
            #game.time.delay(500)
        elif visitedcells == rows*cols:
            mazedone = True

        if mazedone:
            if end != None:
                p = end
                while p.parent != None:
                    if p.parent != start:
                        p.parent.color = green
                    p = p.parent

        for a in range(0,len(maze)):
            maze[a].draw()


        game.display.update()
                
        clock.tick(fps)
    
    game.quit()
    quit()
        
game_start()







