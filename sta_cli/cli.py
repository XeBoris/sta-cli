"""Console script for sportstrackeranalyzer."""
import argparse
import sys
import os
import datetime
import shelve

#Imports sta-cli modules
from .inputs import collect_cli_user_info


#Imports from sta-core modules
from sta_core.simple_actions import create_db
from sta_core.simple_actions import load_db
from sta_core.simple_actions import set_user
from sta_core.simple_actions import list_user
from sta_core.simple_actions import list_shelve
from sta_core.simple_actions import mod_user
from sta_core.simple_actions import add_tracks
from sta_core.simple_actions import find_tracks
from sta_core.simple_actions import remove_tracks
from sta_core.simple_actions import remove_leaves

from sta_core.handler.shelve_handler import ShelveHandler
from sta_core.handler.db_handler import DataBaseHandler

from sta_etl.sta_etl import cli_proc
from sta_etl.sta_etl import list_plugins

shelve_temp = os.path.join(os.path.expanduser("~"), ".sta")

def main():
    """Console script for sportstrackeranalyzer."""
    parser = argparse.ArgumentParser()
    parser.add_argument('_', nargs='*')
    parser.add_argument('--type', dest='type', type=str)
    parser.add_argument('--path', dest='path', type=str)

    parser.add_argument('--key', dest='key', type=str)
    parser.add_argument('--value', dest='value', type=str)
    parser.add_argument('--date', dest='date', type=str)
    parser.add_argument('--hash', dest='hash', type=str)
    parser.add_argument('--overwrite', dest='overwrite', action='store_true')


    parser.add_argument('--track-source', dest='track_source', type=str) #runtastic, strava,...
    parser.add_argument('--source-type', dest='source_type', type=str) #db-dump, gps, online

    args = parser.parse_args()

    print("Arguments: " + str(args))
    print("Replace this message by putting your code into "
          "sportstrackeranalyzer.cli.main")

    print(args._)

    if args._[0] == "createDB":
        db_name = args._[1]
        db_path = args.path
        db_type = args.type
        create_db(db_type=db_type,
                  db_path=db_path,
                  db_name=db_name)

    elif args._[0] == "loadDB":
        db_name = args._[1]
        db_path = args.path
        db_type = args.type

        load_db(db_type=db_type,
                db_path=db_path,
                db_name=db_name)

    elif args._[0] == "setUser":
        db_user = args._[1]
        set_user(db_user=db_user)

    elif args._[0] == "addUser":
        """
        We add a new user to our Database
        """
        #Bind the CLI interface to the database core:
        db_temp = ShelveHandler()
        db_dict = db_temp.read_shelve_by_keys(["db_name", "db_type", "db_path"])

        dbh = DataBaseHandler(db_type=db_dict["db_type"])
        dbh.set_db_path(db_path=db_dict["db_path"])
        dbh.set_db_name(db_name=db_dict["db_name"])

        #Getting CLI response handler from sta-cli
        init_user_dictionary = collect_cli_user_info()

        dbh.create_user(init_user_dictionary)
        del dbh
        del db_temp


    elif args._[0] == "listShelve":
        #all allowed key arguments:
        key_args = ["all-keys", "key-values", "shelve-path"]

        #Handle simple_action in the core module:
        shelve_key = args.key
        ret = list_shelve(shelve_key)


        #prepare CLI output:
        print(f"Overview: {shelve_key}")
        print()
        if shelve_key == "all-keys":
            print(f"All keys are: {ret}")
        elif shelve_key == "key-values":
            for k, val in ret.items():
                if isinstance(val, str):
                    print(f" [{k}] - {val}")
                elif isinstance(val, dict):
                    for j, jval in val.items():
                        print(f" [{k}] - [{j}] - {jval}")
        elif shelve_key == "shelve-path":
            print(f"Current shelve paths: {ret}")
        else:
            print("You need to specify one of the following arguments:")
            for i in key_args:
                print(f"  --key {i}")
        print()

    elif args._[0] == "listUser":
        """
        Here we are performing operations regarding listing users from the
        connected database core.
        """

        #Bind the CLI interface to the database core:
        db_temp = ShelveHandler()
        db_dict = db_temp.read_shelve_by_keys(["db_name", "db_type", "db_path"])

        dbh = DataBaseHandler(db_type=db_dict["db_type"])
        dbh.set_db_path(db_path=db_dict["db_path"])
        dbh.set_db_name(db_name=db_dict["db_name"])

        #Start to handle list requests.
        search_result = dbh.search_user("koenigbb", by="username")

        all_hashes = dbh.get_all_users("user_hash")

        for i_hash in all_hashes:
            i_user = dbh.search_user(i_hash, by="hash")
            if len(i_user) == 0:
                continue
            i_user = i_user[0]
            user_line = f"{i_user.get('user_surname')} {i_user.get('user_lastname')}: {i_user.get('user_username')} / {i_user.get('user_hash')}"

            print(user_line)

        del db_temp
        del dbh

    elif args._[0] == "modUser":
        # prepare to modify the user database
        db_key = args.key
        db_value = args.value
        db_date = args.date
        mod_user(key=db_key,
                 value=db_value,
                 date=db_date)

    elif args._[0] == "addTracks":

        #Handle argument inputs
        track_source = args.track_source
        source_type = args.source_type
        overwrite = args.overwrite
        input_path = args.path
        date_obj = args.date

        # Bind the CLI interface to the database core:
        db_temp = ShelveHandler()
        db_dict = db_temp.read_shelve_by_keys(db_temp.get_all_shelve_keys())

        dbh = DataBaseHandler(db_type=db_dict["db_type"])
        dbh.set_db_path(db_path=db_dict["db_path"])
        dbh.set_db_name(db_name=db_dict["db_name"])

        dbh_info = {"db_type": db_dict["db_type"],
                    "db_path": db_dict["db_path"],
                    "db_name": db_dict["db_name"],
                    "db_hash": db_dict["db_hash"]}

        add_tracks(core_information=dbh_info,
                   track_source=track_source,
                   source_type=source_type,
                   input_path=input_path,
                   overwrite=overwrite,
                   date_obj=date_obj)

    elif args._[0] == "findTracks":
        track_source = args.track_source
        source_type = args.source_type
        date = args.date

        find_tracks(track_source, source_type, date)

    elif args._[0] == "removeTracks":
        track_hash = args.hash

        remove_tracks(track_hash)

    elif args._[0] == "removeLeaves":
        track_hash = args.hash

        remove_leaves(track_hash)

    elif args._[0] == "authorizeStrava":
        from .strava_auth_routes import urls_blueprint
        import webbrowser
        from threading import Timer
        from flask import Flask

        def open_browser():
            webbrowser.open_new('http://127.0.0.1:5000/')


        app = Flask(__name__)
        app.register_blueprint(urls_blueprint)
        Timer(1, open_browser).start()
        app.run(debug=True)

    elif args._[0] == "process":
        track_hash = args.hash
        plugins = args.type

        # Bind the CLI interface to the database core:
        db_temp = ShelveHandler()
        db_dict = db_temp.read_shelve_by_keys(db_temp.get_all_shelve_keys())
        print(db_dict)

        dbh_info = {"db_type": db_dict["db_type"],
                    "db_path": db_dict["db_path"],
                    "db_name": db_dict["db_name"],
                    "db_hash": db_dict["db_hash"]}
        print(dbh_info)
        print("")
        cli_proc(track_hash, dbh_info, plugins)

    elif args._[0] == "list-process-plugins":
        all_plugins = list_plugins()
        print("Here is a list existing plugins:")
        for i_plugin in all_plugins:
            print(f"<> {i_plugin}")
    return 0




if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
