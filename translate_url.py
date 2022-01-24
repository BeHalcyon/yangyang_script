
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

header = 'https://api.m.jd.com/client.action?functionId=newBabelAwardCollection'
body = '{"activityId":"3WzqTqNgz2FzYetCe2XJnTsm8cUP","scene":"1","args":"key=74BFA6515492FE1B5F56B4C640198402B927E79E3BEE3DB285928F8D1ED513EFFDB6D547F9F68562365F664A35B10853_bingo,roleId=A2B8CAF2D3CD20E26A49AF33CC07F777_bingo,strengthenKey=10512DF4C3CA58276FBA323D56C1FDA0D96E4E9F80D4E5620B7629495B26C224BFF5FE99849857C1038ADFA5A483F6B4_bingo"}'

print(url(header, body))



