import json
import database
from settings import my_id

def bsRequest(id):
    from bs4 import BeautifulSoup
    import requests
    return_list = {}
    try:
        r_comments = requests.get('http://forum.mfd.ru/forum/poster/comments/?id={id}'.format(id=id)).content
        r_posts = requests.get('http://forum.mfd.ru/forum/poster/posts/?id={id}'.format(id=id)).content
        soup_comments = BeautifulSoup(r_comments, "html.parser")
        soup_posts = BeautifulSoup(r_posts, "html.parser")
        comments = [p.text for p in soup_comments.find_all("div", {"class": "mfd-quote-text"})]
        posts = [p.text for p in soup_posts.find_all("div", {"class": "mfd-quote-text"})]
        if len(comments) > 0:
            return_list["comment"] = comments[0]
        if len(posts) > 0:
            return_list["post"] = posts[len(posts) - 1]
        return return_list
    except:
        return return_list


def newMessageCheck(bot):
    with open('data.json') as json_input:
        data = json.load(json_input)
        json_input.close()
    for j in data:
        bsdata = bsRequest(j)
        getData(bot, bsdata, data, j, "post")
        getData(bot, bsdata, data, j, "comment")
    with open('data.json', 'w') as json_export:
        json.dump(data, json_export)
        json_export.close()


def getData(bot, bsdata, data, j, text):
    if text in bsdata:
        if data[j][f"{text}_hex"] != database.makeMD5(bsdata[text]):
            bot.sendMessage(chat_id=my_id,
                            text=f'New post from {{{j}}}:{{{bsdata[text]}}}')
            data[j][f"{text}_hex"] = database.makeMD5(bsdata[text])
