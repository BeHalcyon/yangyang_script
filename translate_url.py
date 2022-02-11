
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
body = '{"couponSource":"ace","couponSourceDetail":null,"eid":"eidAc18e812136s4nTjtooubT3ilXFcHm4cYWp047yFwDgQUNBDtBBL8hAcO30AD++373zBE1iv9iNKLCWclDhywo3299Kkm3mr+x0dOrvzHVD9ZmZ5W","extend":"0271DFD6890D3B60ACB8BA8A9E49BEB17FE8E6323A36834B63FE69E95D38088E4F2382B6F3D785A866EE750B76429E5132C90E76D8AB5619327E01D1578C6F08B6BD9E05DFCD8856878CFD0DFB662DCFEEAD7C70516C06C40B020D94A5452E71","lat":"","lng":"","pageClickKey":"Coupons_GetCenter","rcType":"1","shshshfpb":"JD012145b9SEqmv1RLhi164457505239906mrUOCZoxkzRWlNiRb5lmvrBnT2Vzl3RnVjIKZTlp_dX4pEZkKez6uZ2rhOv5qouTW6OWG_OPAirzGe5Ih1s8GSUA8huiifnWgYGkePiJjEg0ztgann~k0ShE0VFfS0uLrm3yoNumA5uD3r3emQ2FL8eLhl_nVQm9h1UL6G1c50WKI9cK9CGrc72sGp6QaA_KJe-2T4vNjsZC85hKH-dijSGLBXgj-_Zrzk5zXO1VYUYqsykIGFW2XQo-It8KicT93wlvPuOc3-zweMofPunqpTzJekgy6Bc","source":"couponCenter_app"}'

print(url(header, body))

