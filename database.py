def makeMD5(text):
    import hashlib
    text_hex = hashlib.md5()
    text_hex.update(text.encode('utf-8'))
    text_hex = text_hex.hexdigest()
    return text_hex

def addToDatabase(bot, update):
    from Parser import bsRequest
    import json
    id = update.message.text.split('/add ')[1]
    bsdata = bsRequest(id)
    if "post" in bsdata:
        post_hex = makeMD5(bsdata["post"])
    else:
        post_hex = ''
    if "comment" in bsdata:
        comment_hex = makeMD5(bsdata["comment"])
    else:
        comment_hex = ''
    with open('data.json') as json_import:
        data = json.load(json_import)
        json_import.close()
    data[id] = {
        "post_hex": post_hex,
        "comment_hex": comment_hex
    }
    with open('data.json', 'w') as json_export:
        json.dump(data, json_export)
        json_export.close()
    update.message.reply_text('Пользователь {id} успешно добавлен'.format(id=id))