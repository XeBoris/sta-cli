import requests
import os
import hashlib
import urllib
import json
from markupsafe import escape
#from loguru import logger

from flask import Blueprint, redirect, request
urls_blueprint = Blueprint('urls', __name__,)

from sta_core.handler.db_handler import DataBaseHandler
from sta_core.handler.shelve_handler import ShelveHandler

db_entry = None

def get_user(user):
    db_temp = ShelveHandler()
    db_dict = db_temp.read_shelve_by_keys(["db_name",
                                           "db_type",
                                           "db_path",
                                            ])

    dbh = DataBaseHandler(db_type=db_dict["db_type"])
    dbh.set_db_path(db_path=db_dict["db_path"])
    dbh.set_db_name(db_name=db_dict["db_name"])

    user_entry = dbh.search_user(user=user, by="username")
    db_entry = user_entry[0]

    del dbh
    del db_temp
    return db_entry

def token_to_shelf(db_entry, stoken):

    db_temp = ShelveHandler()
    db_dict = db_temp.read_shelve_by_keys(["db_name",
                                           "db_type",
                                           "db_path",
                                           ])

    dbh = DataBaseHandler(db_type=db_dict["db_type"])
    dbh.set_db_path(db_path=db_dict["db_path"])
    dbh.set_db_name(db_name=db_dict["db_name"])

    print(stoken)

    db_entry["strava_bearer"] = {
         "access_token": stoken["access_token"],
         "refresh_token": stoken["refresh_token"],
         "expires_at": stoken["expires_at"],
         "expires_in": stoken["expires_in"],
         "token_type": stoken["token_type"],
         "athlete_id": stoken["athlete"]["id"]
    }
    print(db_entry)
    dbh.modify_user(user_hash=db_entry.get("user_hash"),
                    key="strava_bearer",
                    value=db_entry["strava_bearer"],
                    mode="update")

def authorize_url(user):
    """Generate authorization uri"""
    global db_entry
    db_entry = get_user(user)

    latest_strava = sorted(db_entry["strava"], key=lambda k: k['datetime'])[-1]
    latest_strava_client_id = latest_strava["client_id"]

    app_url = os.getenv('APP_URL', 'http://localhost')
    #logger.debug(f"APP_URL={app_url}")
    params = {
        "client_id": latest_strava_client_id,
        "response_type": "code",
        "redirect_uri": f"{app_url}:5000/authorization_successful",
        "scope": "read_all,profile:read_all,activity:read_all",
        #"state": 'https://github.com/sladkovm/strava-oauth',
        "approval_prompt": "force"
    }
    values_url = urllib.parse.urlencode(params)
    base_url = 'https://www.strava.com/oauth/authorize'
    rv = base_url + '?' + values_url
    #logger.debug(rv)
    return rv


k = """
<html>
Welcome to Strava <br>
<br>
<br>
<form action="{{ url_for('addRegion') }}" method="post">
    Project file path: <input type="text" name="projectFilePath"><br>
    <input type="submit" value="Submit">
</form>

</html>
"""
@urls_blueprint.route('/')
def home():
    return k

@urls_blueprint.route('/addRegion', methods=['POST'])
def addRegion():
    print(request.form['projectFilePath'])
    return (request.form['projectFilePath'])

@urls_blueprint.route('/client')
def client():
    resp.text = os.getenv('STRAVA_CLIENT_ID')

@urls_blueprint.route('/authorize/<username>')
def authorize(username):
    user = escape(username)
    """Redirect user to the Strava Authorization page"""
    return redirect(location=authorize_url(user))


@urls_blueprint.route('/authorization_successful')
def authorization_successful():
    """Exchange code for a user token"""

    #db_entry = get_user()
    print("auth", db_entry)

    latest_strava = sorted(db_entry["strava"], key=lambda k: k['datetime'])[-1]
    latest_strava_client_id = latest_strava["client_id"]
    latest_strava_client_secret = latest_strava["client_secret"]


    params = {
        "client_id": latest_strava_client_id,
        "client_secret": latest_strava_client_secret,
        "code": request.args.get("code"),
        "grant_type": "authorization_code"
    }
    r = requests.post("https://www.strava.com/oauth/token", params)
    #logger.debug(r.text)

    if r.json().get("message") == "Bad Request":
        print("Return message")
        print(r.json())
        exit()
    else:
        print("Safe token")
        token_to_shelf(db_entry=db_entry,
                       stoken=r.json())
    return r.json()





