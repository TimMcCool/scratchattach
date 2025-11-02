"""
The /website folder contains the source code for scratchattach's website (scratchattach.tim1de.net).
It is NOT part of the scratchattach Python library and won't be downloaded when you install scratchattach.
"""

from flask import Flask, render_template, send_from_directory, jsonify
import scratchattach as sa
import time
import random

app = Flask(__name__, template_folder="source")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory('source/css', filename)

@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory('source/images', filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory('source/js', filename)

# community projects are cached to prevent spamming Scratch's API
community_projects_cache: list[dict] = []
last_cache_time = 0

@app.route('/api/community_projects/')
def community_projects():
    global community_projects_cache
    if time.time() - 300 > last_cache_time:
        projects = sa.Studio(id=31478892).projects(limit=40)
        if isinstance(projects[0], dict): #atm the server this is running on still uses scratchattach 1.7.4 that returns a list of dicts here
            community_projects_cache = [
                {"project_id":p["id"], "title":p["title"], "author":p["username"], "thumbnail_url":f"https://uploads.scratch.mit.edu/get_image/project/{p['id']}_480x360.png"} for p in projects
            ]
        else:
            community_projects_cache = [
                {"project_id":p.id, "title":p.title, "author":p.author_name, "thumbnail_url":f"https://uploads.scratch.mit.edu/get_image/project/{p.id}_480x360.png"} for p in projects
            ]
    return jsonify(random.choices(community_projects_cache, k=5))