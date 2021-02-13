import datetime

def collect_cli_user_info():
    print("Begin to collect CLI user information:")

    user_surname = input("Surname: ")
    user_lastname = input("Lastname: ")
    user_username = input("Username: ")
    user_birthday = input("Birthday: ")
    user_weight = input("Weight: ")
    user_height = input("Height: ")
    user_sex = input("Sex: ")

    retdict = {"user_surname": user_surname,
               "user_lastname": user_lastname,
               "user_username": user_username,
               "user_birthday": user_birthday,
               "user_weight": [{str(datetime.datetime.now().timestamp()): user_weight}],
               "user_height": user_height,
               "user_sex": user_sex}

    cr = input("Do you with to add Strava credentials? (y/n)")
    if cr == "y":
        user_str_client_id = input("Add STRAVA client_id: ")
        user_str_client_secret = input("Add STRAVA client secret: ")

        fstrava = {}
        fstrava["client_id"] = user_str_client_id
        fstrava["client_secret"] = user_str_client_secret
        fstrava["datetime"] = str(datetime.datetime.now().timestamp())

        retdict["strava"] = []
        retdict["strava"].append(fstrava)

    elif cr == "n":
        pass
    else:
        pass


    return retdict
