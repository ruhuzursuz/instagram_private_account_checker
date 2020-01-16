import re
import os
import json
import requests
import time

# make a text file named usernames.txt
# put the usernames line by line

sleep_time = 300
query_hash = "f2405b236d85e8296cf30347c9f08c2a"

with open("usernames.txt", "r") as usernames_file:
    usernames = usernames_file.read().splitlines()


def download(images):
    for image in images:
        image_id = image["node"]["id"]
        shortcode = image["node"]["shortcode"]
        if image["node"]["is_video"]:
            image_page_url = "https://www.instagram.com/p/" + shortcode
            image_page_url_response = s.get(image_page_url).text
            image_direct_url = re.search('og:video" content="(.*?)"', image_page_url_response)[1]
            extension = ".mp4"
        else:
            extension = ".jpg"
            image_direct_url = image["node"]["display_url"]
            
        image_file_path = username + "_images/" + image_id + extension
        if not os.path.isfile(image_file_path):
            image_content = s.get(image_direct_url).content
            with open(image_file_path, "wb") as image_file:
                image_file.write(image_content)
            print(shortcode + extension + " saved")


s = requests.Session()
response = s.get("https://instagram.com/")
csrf_token = re.search('"csrf_token":"(.*?)"', response.text)[1]
s.headers.update({"X-CSRFToken": csrf_token})

while True:
    
    for username in usernames:
        response = s.get("https://instagram.com/" + username)
        script = re.search('window._sharedData = (.*?);', response.text)[1]
        data = json.loads(script)
        user_data = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]
        is_private = user_data["is_private"]
        if not is_private:
            user_id = user_data["id"]
            has_next_page = True
            end_cursor = None
            print(username, " account is not private now!", "\a")
            if not os.path.exists(username + "_photos"):
                os.mkdir(username + "_photos")

            while has_next_page:
                if end_cursor is None:
                    has_next_page = user_data["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
                    end_cursor = user_data["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
                    pics_and_vids = user_data["edge_owner_to_timeline_media"]["edges"]
                    download(pics_and_vids)
                
                if end_cursor is not None:
                    variables = '{"id":' + user_id + ',"first":12,"after":"' + end_cursor + '"}'
                    payload = {"query_hash": query_hash, "variables": variables}
                    resp = s.get("https://www.instagram.com/graphql/query/?", params=payload).json()
                    pics_and_vids = resp["data"]["user"]["edge_owner_to_timeline_media"]["edges"]
                    download(pics_and_vids)
                    has_next_page = resp["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
                    end_cursor = resp["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
            print(username, " images are updated\n")
            print("you can delete username from the file", "\a")
            print("otherwise i will check the same username againg and again\n")
            print("it is up to you\n")

    print("i've checked the accounts. i'll sleep now")
    time.sleep(sleep_time)
