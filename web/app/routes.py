from ntpath import join
from posixpath import split
from flask import  jsonify, render_template, redirect, request, url_for, abort, Response
from multiprocessing import Process, Value
from app import app
import sys

sys.path.insert(0, app.config["WFC"])
from generate import WFC, compile_iso_tiles

tiles = compile_iso_tiles(app.config["WFC"] + "\\")

updated = {}

@app.route('/', methods=['GET'])
def home():
    return render_template("main.html")


def generateImage(q, key):
    print("building image ", str(key) + ".png")

    gen = WFC(10,10,tiles)
    gen.start()
    img = gen.buildImageIsometric(yOffset=64, xOffset=128, diamond=True)
    img.save("app/static/images/" + str(key) + ".png")

    q.value = 1


@app.route('/<key>', methods=["GET"])
def startGenerateTask(key):

    updated[str(key)] = Value("i", 0)
    updated[str(key)].value = False
    p = Process(target=generateImage, args=[updated[str(key)],key])
    p.start()

    return Response("{}", status=102, mimetype="application/json")

@app.route('/check/<key>')
def check(key):
    if str(key) in updated and updated[str(key)].value == 1:
        updated.pop(str(key))
        return jsonify("True")
    return jsonify("False")


@app.errorhandler(404)
def page_not_found(error):
   return render_template('404.html', title = '404'), 404

