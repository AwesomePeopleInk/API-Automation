"""
     autopull.py
    by thewatcher
      GNU GPLv3
"""

import json
import os
import subprocess
import flask

APP = flask.Flask(__name__)

def cfg_load(path):
    """
    Loads the config file. The config file
    maps repo names to paths. It also says
    which branch to watch. Example:
    {
        "repo-name": {
            "path": "path-to-repo",
            "watch-branch": "name-of-branch"
        }
    }
    """
    with open(path) as data_file:
        data = json.load(data_file)
    return data

@APP.route("/ci-server", methods=["POST"])
def receiver():
    """
    This function gets run when a POST to
    localhost/ci-server occures. It then
    cd's to the path provided by the config
    file and pulls the updated source from
    github.
    """
    if flask.request.method == "POST":
        if flask.request.headers.get("X-GitHub-Event") == "push":
            cfg = cfg_load("config/config.json")
            res = json.JSONDecoder().decode(flask.request.form["payload"])
            try:
                if cfg[res["repository"]["name"]]["watch-branch"] not in res["ref"]:
                    return "an error occured", 501
                print(res["commits"][0]["author"]["username"] + " committed to " + res["repository"]["url"] + "\n→ " + res["commits"][0]["url"])
            except KeyError:
                print("someone committed to " + res["repository"]["url"] + "\n→ " + res["commits"][0]["url"])
            try:
                os.chdir(cfg[res["repository"]["name"]]["path"])
                if subprocess.call(["git", "pull", res["repository"]["url"]]) != 0:
                    return "an error occured", 500
            except KeyError:
                return "an error occured", 500
            return "succes", 200
        else:
            return "an error occured", 500
