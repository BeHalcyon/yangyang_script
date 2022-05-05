
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


header = 'https://api.m.jd.com/client.action?client=wh5&clientVersion=1.0.0&functionId=newBabelAwardCollection'
args = 'key=E72F2D6FD3B257AE6EAEEF81FEF44D9C3EFB9B5E0F0E11C4562D68BDA7BA69BF5C4E716FB9BBD7B1678E83551EA3A72E_bingo,roleId=3FE9EECAAA41B666E4FFAF79F20E21120520F1A5AFE5C9E8D77BD263F6726B9E3576C6C5571777201DA90CF204F2336AB211D7BA6D0E7255BAFF71BCC9ED7782F4BB5E97DDCA47183788BB228E79E0C37E88EBDD62C00AECFDE419BBD98287372A20B7D98629E6EA6369402EA320CF23958FE3451A67DF687C49761CDC81622DC1953FE9A31CDF1A4246C02614AD33B67229842B53A486AA95A37BA40B0BF4C082B618FCD43038CBD1059E9E556F1178_bingo,strengthenKey=10512DF4C3CA58276FBA323D56C1FDA0D96E4E9F80D4E5620B7629495B26C22491AA4D3EDF96006A35FF45C7A14E007E_bingo'
body = '{"activityId":"vN4YuYXS1mPse7yeVPRq4TNvCMR","scene":"1","args":"' + args + '"}'

print(url(header, body))

