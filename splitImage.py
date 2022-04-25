from xmlrpc.client import Boolean
from PIL import Image


def tileIsSame(im, im2) -> Boolean:
    for x in range(im.size[0]):
        for y in range(im.size[1]):
            p = im.getpixel((x,y))
            p2 = im2.getpixel((x,y))

            if p != p2:
                return False
    return True

def removeBackground(im, colors):
    img = im.convert("RGBA")

    for i in range(len(colors)):
        if len(colors[i]) == 3:
            colors[i] = (colors[i][0],colors[i][1],colors[i][2],255)
        
    for x in range(im.size[0]):
        for y in range(im.size[1]):
            p = img.getpixel((x,y))
            if p in colors:
                img.putpixel((x,y), (0,0,0,0))
    return img

tiles = []

SIZE = (32,32)
count = 0
with Image.open("topDownTileset.png") as im:
    for x in range(0,im.size[0], SIZE[0]):
        for y in range(0,im.size[1], SIZE[1]):
            tile = im.crop((x,y,x+SIZE[0],y+SIZE[1]))

            color1 = (208,228,227)
            color2 = (255,255,255)
            tile = removeBackground(tile, [color1,color2])

            save = True
            for saved in tiles:
                if tileIsSame(tile,saved):
                    save = False
                    break
            
            if save:
                tile.save("tiles/" + str(count) + ".png")
                count += 1
                tiles.append(tile)

    