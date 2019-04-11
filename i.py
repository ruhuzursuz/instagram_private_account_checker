import re
import os
import json
import hashlib
import requests
import time

# requests modülü lazım. requestssiz yapmaya çalışayım mı?
# cmd'yi açıp "pip install requests" ile kurabilirsin

# scriptin olduğu yere hesaplar.txt dosyası oluştur
# gözlemek istediğim hesapların linklerini alt alta yaz

# bence çok gereksiz bir çaba bu. ama neyse.

hesaplar = []
uyuma_suresi = 300 #kaç saniyede 1 çalışsın


with open("hesaplar.txt","r") as oku:
    for satir in oku:
        hesaplar.append(satir.strip())

def calculate_x_instagram_gis(rhx_gis, variables):
    text = rhx_gis + ":" + variables
    x_i_gis = hashlib.md5(text.encode()).hexdigest()
    return x_i_gis

def indir(gorseller):
    for gorsel in gorseller:
        gorsel_id = gorsel["node"]["id"]
        if gorsel["node"]["is_video"]:
            shortcode = gorsel["node"]["shortcode"]
            video_sayfasi = "https://www.instagram.com/p/" + shortcode
            response = s.get(video_sayfasi).text
            gorsel_link = re.findall('og:video" content="(.*?)"',response)[0]
            uzanti = ".mp4"
        else:
            uzanti = ".jpg"
            gorsel_link = gorsel["node"]["display_url"]
            
        gorsel_yolu = username + "_photos/" + gorsel_id + uzanti
        if not os.path.isfile(gorsel_yolu):
            response = s.get(gorsel_link)
            with open(gorsel_yolu,"wb") as yaz:
                yaz.write(response.content)
            print(gorsel["node"]["shortcode"] + uzanti + " kaydedildi")

while True:

    s = requests.Session()
    headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 OPR/58.0.3135.127"}
    s.headers.update(headers)


    for hesap in hesaplar:
        response = s.get(hesap)
        script = re.findall('window._sharedData = (.*?);',response.text)[0]
        data = json.loads(script)
        rhx_gis = data["rhx_gis"]
        csrf_token = data["config"]["csrf_token"]
        json_data = data["entry_data"]["ProfilePage"][0]["graphql"]["user"]
        gizli_mi = json_data["is_private"]
        if not gizli_mi:
            hesap_id = json_data["id"]
            has_next_page = True
            end_cursor = None
            username = json_data["username"]
            print(username," hesabı artık gizli değil!","\a")
            if not os.path.exists(username + "_photos"):
                os.mkdir(username + "_photos")

            while has_next_page:
                if end_cursor is None:
                    has_next_page = json_data["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
                    end_cursor = json_data["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
                    gorseller = json_data["edge_owner_to_timeline_media"]["edges"]
                    indir(gorseller)
                
                if end_cursor is not None:
                    query_hash = "f2405b236d85e8296cf30347c9f08c2a"
                    variables = '{"id":'+hesap_id+',"first":12,"after":"'+end_cursor+'"}'
                    instagram_gis = calculate_x_instagram_gis(rhx_gis,variables)
                    payload = {"query_hash": query_hash,"variables" : variables}
                    headers = {"user-agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36 OPR/58.0.3135.127","x-instagram-gis": instagram_gis}
                    s.headers.update(headers)
                    response = s.get("https://www.instagram.com/graphql/query/?", params = payload).json()
                    gorseller = response["data"]["user"]["edge_owner_to_timeline_media"]["edges"]
                    indir(gorseller)
                    has_next_page = response["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["has_next_page"]
                    end_cursor = response["data"]["user"]["edge_owner_to_timeline_media"]["page_info"]["end_cursor"]
            print(username, " hesabının görsellerini güncelledim\n")
            print("Kendisiyle işimiz bitti gibi. Linkini text dosyasından silmeyi düşünebilirsin","\a")
            print("Aksi takdirde sürekli fotoğraflarını kontrol edeceğim\n")

    print("Hesapları kontrol ettim. Biraz uyuyacağım")
    time.sleep(uyuma_suresi)
                
                
                    
