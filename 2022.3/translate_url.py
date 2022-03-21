
# without body=
def url(header, body):
    d = {}
    d["{"] = "%7B"
    d["}"] = "%7D"
    d["\""] = "%22"
    d[":"] = "%3A"
    d[","] = "%2C"
    d["="] = "%3D"
    for k, v in d.items():
        body = body.replace(k, v)
    return header + "&body=" + body

header = 'https://api.m.jd.com/client.action?functionId=withdrawRedPocket&client=wh5&clientVersion=1.0.0&uuid=865441035434968-4c49e3f54533'
header = 'https://api.m.jd.com/client.action?functionId=withdrawRedPocket&client=wh5&clientVersion=1.0.0&uuid=865441035434968-4c49e3f54533'
header = 'https://api.m.jd.com/client.action?functionId=withdrawRedPocket&client=wh5&clientVersion=1.0.0&uuid=865441035434968-4c49e3f54533'
body = '{"depositeType":1}'

header = 'https://api.m.jd.com/client.action?functionId=withdrawWechat&client=wh5&clientVersion=1.0.0&uuid=865441035434968-4c49e3f54533'
body = '{"depositeType":3,"wechatCode":"031qj6ml2W7TP849MUnl2a4Syt0qj6mu"}'

print(url(header, body))

