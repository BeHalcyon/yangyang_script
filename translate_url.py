
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
body = '{"activityId":"UcLBtK9kh8rA8M2h6pBfhd7rsd7","scene":"1","args":"key=D651DC890AA761CC39C581557571EF35720127D95D4422B80E57E16A02124747AC25142AF604076FEF3739C893178A69_bingo,roleId=CDDD72A6BDA35006C390C9873C7D59EC26958060D8F8C64AA1C6D19CA06982B9_bingo,strengthenKey=19F512DCD8EE34ABE9C4FB4A92C2F42AD087F2793D128E179E54442023E04B8EAED22A924F640F5833468BE7513F40BC_bingo"}'

print(url(header, body))

