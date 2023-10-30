import requests
import re
import os
from bs4 import BeautifulSoup


session=requests.session()

url = "https://animepahe.ru/"

def search_apahe(query):
    global url
    search_url = url + "api?m=search&q=" + query
    response = session.get(search_url)
    data = response.json()
    return data


def mid_apahe(session_id, episode_range):
    global url
    pages=[1, 2]
    if episode_range != "Full":
        pages[0]+=(episode_range[0]//30)
        pages[1]+=(episode_range[1]//30)
        
    else:
        url2 = url + "api?m=release&id=" + session_id + "&sort=episode_asc&page=1"
        r = session.get(url2)
        r = r.json()
        pages[0] = 1
        pages[1] = int(r["last_page"])
        episode_range=[1,int(r["total"])+1]
    data = []
    for page in range(pages[0],pages[1]):
        url2 = url + "api?m=release&id=" + session_id + "&sort=episode_asc&page="+ str(page)
        r = session.get(url2)
        for i in (r.json())['data']:
            s = str(i['session'])
            data.append(s)
    return data[(episode_range[0]%30)-1:30*(pages[1]-pages[0]-1)+episode_range[1]%30]


def dl_apahe1(anime_id: str, episode_ids: list) -> dict:
    
    global url
    urls = [f'{url}/play/{anime_id}/{episode_id}' for episode_id in episode_ids]
    responses  = []
    for i in urls:
        r = requests.get(i)
        responses.append(r)
    data_dict = {}
    for index, response in enumerate(responses):
        if response is not None and response.status_code == 200:
            text = response.text
            soup = BeautifulSoup(text, 'html.parser')
            options = soup.find("div", {"id":"pickDownload"}).find_all("a")
            temp = []
            for i in options:
                lang = "Dub" if "eng" in i.text else "Sub"
                res = i.text.split("·")[-1].split()[0]
                temp.append([i["href"], res, lang])
        data_dict[index+1] = temp
    return data_dict

def dl_apahe2(url: str) -> str:
    r = requests.get(url)
    redirect_link = (re.findall(r'(https://kwik\.cx/[^"]+)', r.text))[0]
    return redirect_link
