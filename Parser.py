import json

def bsRequest(id):
    from bs4 import BeautifulSoup
    import requests
    returnlist = {}
    print(id)
    r_comments = requests.get('http://forum.mfd.ru/forum/poster/comments/?id={id}'.format(id=id)).content
    r_posts = requests.get('http://forum.mfd.ru/forum/poster/posts/?id={id}'.format(id=id)).content
    soup_comments = BeautifulSoup(r_comments, "html.parser")
    soup_posts = BeautifulSoup(r_posts, "html.parser")
    comments = [p.text for p in soup_comments.find_all("div", {"class": "mfd-quote-text"})]
    posts = [p.text for p in soup_posts.find_all("div", {"class": "mfd-quote-text"})]
    if len(comments) != 0:
        returnlist["comment"] = comments[len(comments)-1]
    if len(posts) != 0:
        returnlist["post"] = posts[len(posts)-1]
    print(returnlist)
    return returnlist


def newMessageCheck(bot, update):
    import database
    with open('data.json') as json_input:
        data = json.load(json_input)
        json_input.close()
    for j in data:
        bsdata = bsRequest(j)
        if "post" in bsdata:
            if data[j]["post_hex"] != database.makeMD5(bsdata["post"]):
                bot.sendMessage(chat_id=-192662319,
                                text='New post from {id}:{post}'.format(id=j, post=bsdata["post"]))
                data[j]["post_hex"] = database.makeMD5(bsdata["post"])
        if "comment" in bsdata:
            if data[j]["comment_hex"] != database.makeMD5(bsdata["comment"]):
                bot.sendMessage(chat_id=-192662319,
                                text='New comment from {id}:{post}'.format(id=j, post=bsdata["post"]))
                data[j]["comment_hex"] = database.makeMD5(bsdata["comment"])
    with open('data.json','w') as json_export:
        json.dump(data, json_export)
        json_export.close()

