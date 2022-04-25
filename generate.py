from PIL import Image
from random import choices, randint

from matplotlib.style import available

# helper class, really just stores data
class Tile():
    def __init__(this, number, image, rules=None, priority=1, self_priority=1):
        this.number = number
        this.image = Image.open(image)
        this.rules = rules
        this.size = this.image.size
        this.priority = priority
        this.self_priority = self_priority

        if rules is None:
            this.rules = {"North":[], "South": [], "East": [], "West": []}


# main wave function collapse class
class WFC():
    def __init__(this,width,height,tiles):
        """
        WFC()  | A random map generator utilizing Wave Function Collapse\n
        width  | (int) number of tiles in the x direction\n
        height | (int) number of tiles in the y direction\n
        tiles  | (list( Tile ))\n
        """
        this.width = width
        this.height = height
        this.tiles = tiles

        grid = []
        for y in range(height):
            row = []
            for x in range(width):
                row.append(tiles)
            grid.append(row)
        
        this.grid = grid
        this.lastCollapsed = None

    def printOptions(this):
        """
        printOptions() | prints the current state of the collapse\n
        """
        print("==================")
        for y in this.grid:
            out = ""
            for x in y:
                if len(x) < 10:
                    out += "0"
                out += str(len(x)) + " "
            print(out)
        print("==================")

    def _collapsePoint(this):
        """
        _collapsePoint() | picks the highest priority point to collapse next ranked as follows\n
            1. point with the lowest choices that hasnt been collapsed\n
            2. uncollapsed point closest to the last collapsed point\n
            3. random point\n
        
        returns | (x,y) of collapsed point\n
        """
        # find point with least options to collapse next
        lowest = (-1,-1,len(this.tiles))
        for y in range(len(this.grid)):
            for x in range(len(this.grid[y])):
                a = len(this.grid[y][x])
                if a < lowest[2] and a > 1:
                    lowest = (x,y,a)
        
        x,y=lowest[0:2]

        # if each point has equal options
        if x == -1:
            # if its the first occurance pick a random point
            if this.lastCollapsed == None:
                x = randint(0,this.width-1)
                y = randint(0,this.height-1)
            # otherwise find a non-collapsed point closest to the last collapsed point
            else:
                close = None
                closeDis = None
                for y in range(len(this.grid)):
                    for x in range(len(this.grid[y])):
                        point = this.grid[y][x]
                        if len(point) > 1:
                            dis = abs(this.lastCollapsed[0]-x) + abs(this.lastCollapsed[1]-y)
                            if close == None or dis < closeDis:
                                close = (x,y)
                                closeDis = dis
                x = close[0]
                y = close[1]


        this.lastCollapsed = (x,y)

        # pick random tile out of available options

        # add by priority
        choices = []
        for tile in this.grid[y][x]:
            for i in range(tile.priority):
                choices.append(tile)
        

        available = set(choices)
        
        # check if other tiles are collapsed and the same
        # if they are the same, and have a higher self_priority than 1 add extra tiles
        # this allows a greater chance to group similar tiles
        for point in [(1,0),(0,1),(-1,0),(0,-1)]:
            point = (x+point[0], y+point[1])
            if point[0] < this.width and point[0] >= 0 and point[1] < this.height and point[1] >= 0:
                tiles = this.grid[point[1]][point[0]]
                if len(tiles) == 1:
                    tile = tiles[0]
                    if tile in available and tile.self_priority > 1:
                        for i in range(tile.self_priority*tile.priority):
                            choices.append(tile)
        

        a = randint(0,len(choices)-1)
        this.grid[y][x] = [choices[a]]

        return (x,y)

    def _union(this, s1, s2):
        """
        _union() | creates a new set with only values that appear in the two given sets\n
        s1       | (Set())\n
        s2       | (Set())\n
        returns  | (Set())\n
        """
        out = set()
        for val in s1:
            if val in s2:
                out.add(val)
                
        for val in s2:
            if val in s1:
                out.add(val)
        return out

    def _getTilesFromRules(this, rules):
        """
        _getTilesFromRules() |gets the actual tile objects corresponding\n
        with a list of tile numbers

        rules  | (list( int ))\n
        return | (list( Tile ))\n
        """
        tiles = set()
        a = set(rules)
        for tile in this.tiles:
            if tile.number in a:
                tiles.add(tile)
        return tiles

    def _updatePoint(this,x,y):
        """
        _updatePoint() | updates a points possibilities based off of its neighbors\n
        x | x position of point to update\n
        y | y position of point to update\n
        """
        # if the point has already been collapsed dont bother updating it further
        if len(this.grid[y][x]) == 1:
            return

        # create empty sets
        # for each cardinal direction, if the point is in the grid get all 
        # of the possible tiles for the tile at x,y based off of its neighbor
        l1 = set()
        l2 = set()
        l3 = set()
        l4 = set()

        if x + 1 < this.width:
            p = this.grid[y][x+1] # East
            for tile in p:
                t = this._getTilesFromRules(tile.rules["West"])
                l1.update(t)

        if x - 1 >= 0:
            p = this.grid[y][x-1] # West
            for tile in p:
                t = this._getTilesFromRules(tile.rules["East"])
                l2.update(t)

        if y + 1 < this.height:
            p = this.grid[y+1][x] # South
            for tile in p:
                t = this._getTilesFromRules(tile.rules["North"])
                l3.update(t)

        if y - 1 >= 0:
            p = this.grid[y-1][x] # North
            for tile in p:
                t = this._getTilesFromRules(tile.rules["South"])
                l4.update(t)


        # if any of the sets are empty, meaning the point was invalid,
        # make the set equal to the set of all tiles
        # this way when union the sets, the empty sets dont affect the output
        if len(l1) == 0:
            l1 = set(this.tiles)
        if len(l2) == 0:
            l2 = set(this.tiles)
        if len(l3) == 0:
            l3 = set(this.tiles)
        if len(l4) == 0:
            l4 = set(this.tiles)
        
        # get the union of all sets, or all posibilities for a given tile based on its neighbors
        f = this._union(this._union(l1,l2), this._union(l3,l4))
        this.grid[y][x] = list(f)
    
    def _updatePoints(this,x,y):
        """
        _updatePoints() | update all points in the grid to be up to date\n
        with the latest collapse
        x | x position of the last collapsed point\n
        y | y position of the last collapsed point\n
        """

        # starting from the given point, (last collapsed) move out in a circular pattern updating points
        # this ensures each point is updated according to the most recently changed neighbor
        needed = this.width*this.height - 1
        dis = 1
        while needed > 0:
            # define a square that encopses the circle for the next points
            depth = this.grid[max(0,y-dis):min(this.height, y+dis+1)]        
            for i in range(len(depth)):
                depth[i] = depth[i][max(0,x-dis):min(this.width, x+dis+1)]

            # get the location of the collapsed point in our new square region
            point = (x-max(0,x-dis), y-max(0,y-dis))


            # isolate only the points in a circle at distance dis
            # update said points
            for dy in range(len(depth)):
                for dx in range(len(depth[dy])):
                    if abs(point[0]-dx) + abs(point[1]-dy) == dis:
                        actualX = dx - point[0] + x
                        actualY = dy - point[1] + y
                        this._updatePoint(actualX, actualY)

                        needed -= 1

            dis += 1

    def _isCollapsed(this):
        """
        _isCollapsed() | checks if the grid has been entirely collapsed\n
        each tile is either a 0 or 1
        """
        for row in this.grid:
            for p in row:
                if len(p) > 1:
                    return False
        return True

    def _isValid(this):
        """
        _isValid() | checks if the grid has any tiles\n
        with no possible tile choice
        """
        for row in this.grid:
            for p in row:
                if len(p) == 0:
                    return False
        return True

    def start(this, repeat=True, findValid=False):
        """
        start()   | starts the WaveFunctionCollapse\n
        repeat    | (bool) whether or not to repeat until fully collapsed\n
        findValid | (bool) whether or not to retry when a suitable tile cannot be found\n
        """

        if not repeat:
            x,y = this._collapsePoint()
            this._updatePoints(x,y)
            return

        iter = 0
        while not this._isCollapsed():
            x,y = this._collapsePoint()
            this._updatePoints(x,y)
            iter += 1
            print(iter, "/", this.width*this.height, "(max)")
        
        if findValid and not this._isValid():
            this.__init__(this.width, this.height, this.tiles)
            this.collapseAll()    

    def buildImage(this):
        """
        buildImage() | builds the collapsed points as a 2D (top down, or profile)\n
        returns      | PIL Image\n
        """
        resW = this.tiles[0].size[0] * this.width
        resH = this.tiles[0].size[1] * this.height

        print(resW, resH)

        img = Image.new("RGBA", (resW, resH), (0,0,0,255))

        y = 0
        for row in this.grid:
            x = 0
            for tl in row:
                if len(tl) != 0:
                    tile = tl[0]
                    img.paste(tile.image,(x,y))
                x += int(resW/this.width)
            y += int(resH/this.width)


        img.save("gen.png")        
        
    def buildImageIsometric(this, yOffset=0, xOffset=0,diamond=False):
        """
        buildImageIsometric() | builds the collapsed points into an\n
        isometric view (isometric textures required) in either a diamond shape
        or a rigid square shape

        yOffset = 0   | yShift for tiles (depends on image size, and amount of empty space)\n
        xOffset = 0   | xShift for tiles (depends on image size, and amount of empty space)\n
        diamond=False | weather or not to build in a diamon shape\n

        returns       | PIL Image\n
        """
        if diamond:
            resW = this.tiles[0].size[0] + ((max(this.width,this.height))*xOffset*2)
            resH = this.tiles[0].size[1] + ((max(this.width,this.height))*yOffset*2)
            img = Image.new("RGBA", (resW, resH), (0,0,0,0))

            startX = int((resW/2) - (this.tiles[0].size[0]/2))
            startY = 0
            for row in this.grid:
                x = startX
                y = startY
                for point in row:
                    if len(point) != 0:
                        tile = point[0]
                        img.paste(tile.image,(x,y), tile.image)
                    x += xOffset
                    y += yOffset
                startX -= xOffset
                startY += yOffset

            return img


        else:
            resW = this.tiles[0].size[0] * this.width + (xOffset*-1)
            resH = (this.tiles[0].size[1] + yOffset) * (this.height+1)
            resH = this.tiles[0].size[1] + (this.tiles[0].size[1] + yOffset) * (this.height-1)

            print(resW, resH)

            img = Image.new("RGBA", (resW, resH), (0,0,0,0))

            xShift = False

            y = 0
            rowNum = 0
            for row in this.grid:
                x = resW - this.tiles[0].size[0]
                for tl in row:
                    if len(tl) != 0:
                        tile = tl[0]
                        if xShift:
                            img.paste(tile.image,(x+xOffset,y), tile.image)
                        else:
                            img.paste(tile.image,(x,y), tile.image)
                    x -= this.tiles[0].size[0]
                y += this.tiles[0].size[1] + yOffset
                xShift = not xShift
            return img


def compile_2D_tiles():
    # open air
    t3 = {"North":[3], "South": [3,16,15,5,6,7,25,11,19], "East": [3,25,19,15], "West": [3,25,11,15]}
    t3 = Tile(3,"tiles/3.png", t3)

    # rock, flower, chest
    t5 = {"North":[3], "South": [16], "East": [3,5,6,7,26,15], "West": [3,5,6,7,26,15]}
    t5 = Tile(5,"tiles/5.png", t5)

    t6 = {"North":[3], "South": [16], "East": [3,5,6,7,26,15], "West": [3,5,6,7,261,15]}
    t6 = Tile(6,"tiles/6.png", t6)

    t7 = {"North":[3], "South": [16], "East": [3,5,6,7,26,15], "West": [3,5,6,7,26,15]}
    t7 = Tile(7,"tiles/7.png", t7)

    # ground down left
    t11 = {"North":[3], "South": [12], "East": [16], "West": [3,5,6,7,26,15]}
    t11 = Tile(11,"tiles/11.png", t11)

    # rock down left
    t12 = {"North":[11], "South": [17], "East": [17], "West": [16,11]}
    t12 = Tile(12,"tiles/12.png", t12)
    
    # grass
    t15 = {"North":[3], "South": [16], "East": [3,5,6,7,26,15], "West": [3,5,6,7,26,15]}
    t15 = Tile(15,"tiles/15.png", t15)

    # ground flat
    t16 = {"North":[15,5,6,7,26], "South": [17], "East": [16,19,12], "West": [16,11,20]}
    t16 = Tile(16,"tiles/16.png", t16)

    # rock mid
    t17 = {"North":[16,17,12,20], "South": [17], "East": [17,12,20], "West": [17,12,20]}
    t17 = Tile(17,"tiles/17.png", t17)

    # ground down right
    t19 = {"North":[3], "South": [20], "East": [3,5,6,7,26,15], "West": [16]}
    t19 = Tile(19,"tiles/19.png", t19)

    # rock down right
    t20 = {"North":[19], "South": [17], "East": [16,19], "West": [17]}
    t20 = Tile(20,"tiles/20.png", t20)

    # lamp post top
    t25 = {"North":[3], "South": [26], "East": [3], "West": [3]}
    t25 = Tile(25,"tiles/25.png", t25)

    # lamp post bottom
    t26 = {"North":[25], "South": [16], "East": [3,5,6,7,15,11], "West": [3,5,6,7,15,19]}
    t26 = Tile(26,"tiles/26.png", t26)


    return [t3,t5,t6,t7,t11,t12,t15,t16,t17,t19,t20,t25,t26]

def compile_iso_tiles():
    # grass 1, 2, 3, 4, 5
    t1 = {"North": [1,2,3,4,5,6,8,9], "South": [1,2,3,4,5,6,8,9], "East": [1,2,3,4,5,6,8,9], "West": [1,2,3,4,5,6,8,9]}
    t1 = Tile(1,"Isometric tiles/Grass1.png", t1, priority=3)

    t2 = {"North": [1,2,3,4,5,6,8,9], "South": [1,2,3,4,5,6,8,9], "East": [1,2,3,4,5,6,8,9], "West": [1,2,3,4,5,6,8,9]}
    t2 = Tile(2,"Isometric tiles/Grass2.png", t2)

    #t3 = {"North": [1,2,3,4,5,6,8], "South": [1,2,3,4,5,6,8], "East": [1,2,3,4,5,6,8], "West": [1,2,3,4,5,6,8]}
    #t3 = Tile(3,"Isometric tiles/Grass3.png", t3)

    t4 = {"North": [1,2,3,4,5,6,8,9], "South": [1,2,3,4,5,6,8,9], "East": [1,2,3,4,5,6,8,9], "West": [1,2,3,4,5,6,8,9]}
    t4 = Tile(4,"Isometric tiles/Grass4.png", t4)

    t5 = {"North": [1,2,3,4,5,6,8,9], "South": [1,2,3,4,5,6,8,9], "East": [1,2,3,4,5,6,8,9], "West": [1,2,3,4,5,6,8,9]}
    t5 = Tile(5,"Isometric tiles/Grass5.png", t5)

    t6 = {"North": [1,2,3,4,5,6,8], "South": [1,2,3,4,5,6,8], "East": [1,2,3,4,5,6,8,9], "West": [1,2,3,4,5,6,8,9]}
    t6 = Tile(6,"Isometric tiles/Water1.png", t6, priority=3, self_priority=5)

    t7 = {"North": [7,8], "South": [7,8], "East": [7,8], "West": [7,8]}
    t7 = Tile(7,"Isometric tiles/Acid1.png", t7, priority=1, self_priority=5)

    t8 = {"North": [1,2,3,4,5,6,7,8,9], "South": [1,2,3,4,5,6,7,8,9], "East": [1,2,3,4,5,6,7,8,9], "West": [1,2,3,4,5,6,7,8,9]}
    t8 = Tile(8,"Isometric tiles/Block 1.png", t8, self_priority=3, priority=3)

    t9 = {"North": [9,1,2,3,4,5,8], "South": [9,1,2,3,4,5,8], "East": [6,], "West": [6,]}
    t9 = Tile(9,"Isometric tiles/bl.png", t9, priority=1, self_priority=10)


    return [t1,t2,t4,t5,t6,t7,t8,t9]


if "__main__" in __name__:
    #tiles = compile_2D_tiles()
    tiles = compile_iso_tiles()
    

    gen = WFC(8,8,tiles)
    gen.start()
    img = gen.buildImageIsometric(yOffset=64, xOffset=128, diamond=True)
    img.save("gen.png")