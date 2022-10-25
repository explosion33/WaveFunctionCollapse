from ntpath import join
from posixpath import split
from flask import  jsonify, render_template, redirect, request, url_for, abort, Response, send_file
from multiprocessing import Process, Value
from app import app
import sys

sys.path.insert(0, app.config["WFC"])
sys.path.insert(0, "/WFC")
print(app.config["WFC"], app.config["ROOT"])
from generate import WFC, Tile

updated = {}

def compile_iso_tiles(parent_dir="", options={}):
    print("COMPILE", options)
    tiles = []
    for tile in ["Grass1", "Grass2", "Tree", "Water", "Sand"]:
        if tile not in options:
            options[tile] = 1

    t = {"All": [1,2,3,9,10]}
    t = Tile(1,parent_dir + "Isometric tiles/Grass1.png", t, priority=options["Grass1"], self_priority=1)
    tiles.append(t)

    t = {"All": [1,2,3,9,10]}
    t = Tile(2,parent_dir + "Isometric tiles/Grass2.png", t, priority=options["Grass2"])
    tiles.append(t)

    t = {"All": [1,2,3]}
    t = Tile(3,parent_dir + "Isometric tiles/Tree.png", t, priority=options["Tree"], self_priority=1)
    tiles.append(t)

    t = {"All": [4,9], "East": [7,8], "West": [7,8]}
    t = Tile(4,parent_dir + "Isometric tiles/Water.png", t, priority=options["Water"], self_priority=1)
    tiles.append(t)

    t = {"All": [1,2,4,7,8,9,10]}
    t = Tile(9,parent_dir + "Isometric tiles/Sand.png", t, priority=options["Sand"], self_priority=1)
    tiles.append(t)


    return tiles

@app.route('/', methods=['GET'])
def home():
    options = [
        {"id": "Grass1", "label": "Grass", "max": 10, "min": 0, "start": 1},
        {"id": "Grass2", "label": "Bumpy Grass", "max": 10, "min": 0, "start": 1},
        {"id": "Tree", "label": "Tree", "max": 10, "min": 0, "start": 1},
        {"id": "Water", "label": "Water", "max": 10, "min": 0, "start": 1},
        {"id": "Sand", "label": "Sand", "max": 10, "min": 0, "start": 1},
    ]
    return render_template("main.html", options=options)


def generateImage(q, key, w=5, h=5, options={}):
    print("BUILD", options)
    print("building image ", str(key) + ".png")
    tiles = compile_iso_tiles(app.config["WFC"] + "/", options)
    print(tiles[0].priority)

    gen = WFC(w,h,tiles)
    gen.start()
    img = gen.buildImageIsometric(yOffset=64, xOffset=128, diamond=True)
    img.save("app/static/images/" + str(key) + ".png")

    q.value = 1


@app.route('/<key>', methods=["POST"])
def startGenerateTask(key):

    w = int(request.json["width"])
    h = int(request.json["height"])

    options = request.json["options"]
    print(w,h,options)

    updated[str(key)] = Value("i", 0)
    updated[str(key)].value = False
    p = Process(target=generateImage, args=[updated[str(key)],key, w, h, options])
    p.start()

    return jsonify({"status": "success"})

@app.route('/check/<key>')
def check(key):
    if str(key) in updated and updated[str(key)].value == 1:
        updated.pop(str(key))
        return jsonify("True")
    return jsonify("False")


@app.route("/favicon.ico", methods=["GET"])
def icon():
    print("getting icon")
    return send_file("static/favicon.ico")


@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404'), 404

