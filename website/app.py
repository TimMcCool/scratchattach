"""
The /website folder contains the source code for scratchattach's website (scratchattach.tim1de.net).
It is NOT part of the scratchattach Python library and won't be downloaded when you install scratchattach.
"""

import time
import random
import secrets
from flask import Flask, render_template, send_from_directory, jsonify
from vercel.cache import RuntimeCache
import scratchattach as sa

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
# community_projects_cache: list[dict] = []
# last_cache_time = 0
cache = RuntimeCache(namespace="website")

@app.route('/api/community_projects/')
def community_projects():
    # global community_projects_cache
    # global last_cache_time
    community_projects_cache_data = cache.get("community_projects")
    community_projects_cache = community_projects_cache_data and community_projects_cache_data.get("value")
    if not community_projects_cache:
        projects = sa.Studio(id=31478892).projects(limit=40)
        if isinstance(projects[0], dict): #atm the server this is running on still uses scratchattach 1.7.4 that returns a list of dicts here
            community_projects_cache = [
                {"project_id":p["id"], "title":p["title"], "author":p["username"], "thumbnail_url":f"https://uploads.scratch.mit.edu/get_image/project/{p['id']}_480x360.png"} for p in projects
            ]
        else:
            community_projects_cache = [
                {"project_id":p.id, "title":p.title, "author":p.author_name, "thumbnail_url":f"https://uploads.scratch.mit.edu/get_image/project/{p.id}_480x360.png"} for p in projects
            ]
        community_projects_cache_data = {"value": community_projects_cache, "data_id": secrets.token_urlsafe(32)}
        cache.set("community_projects", community_projects_cache_data, {"ttl": 300, "tags": ["website"]})
    response = jsonify(random.choices(community_projects_cache, k=5))
    response.headers.add("Fetched-Data-Id", community_projects_cache_data and community_projects_cache_data.get("data_id"))
    return response
