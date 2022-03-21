rm -rf ck sc pt
cl(){

read -p "请输入手机号: " mobile
appid=959
qversion=1.0.0
country_code=86
}
ck(){
ts=$(expr $(date +%s%N) / 1000000)
sub_cmd=1
gsign=$(echo -n $appid$qversion$ts"36"$sub_cmd"sb2cwlYyaCSN1KUv5RHG3tmqxfEb8NKN" | md5sum | cut -d ' ' -f1)
d="client_ver=1.0.0&gsign=$gsign&appid=$appid&return_page=https%3A%2F%2Fcrpl.jd.com%2Fn%2Fmine%3FpartnerId%3DWBTF0KYY%26ADTAG%3Dkyy_mrqd%26token%3D&cmd=36&sdk_ver=1.0.0&sub_cmd=$sub_cmd&qversion=$qversion&ts=$ts"
l=${#d}
curl -s -k -i --raw -o ck --http2 -X POST -H "Host:qapplogin.m.jd.com" -H "cookie:" -H "user-agent:Mozilla/5.0 (Linux; Android 10; V1838T Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/98.0.4758.87 Mobile Safari/537.36 hap/1.9/vivo com.vivo.hybrid/1.9.6.302 com.jd.crplandroidhap/1.0.3 ({"packageName":"com.vivo.hybrid","type":"deeplink","extra":{}})" -H "accept-language:zh-CN,zh;q=0.9,en;q=0.8" -H "content-type:application/x-www-form-urlencoded; charset=utf-8" -H "content-length:$l" -H "accept-encoding:" -d "$d" "https://qapplogin.m.jd.com/cgi-bin/qapp/quick"
gsalt=$(cat ck | grep -o "gsalt.*" | cut -d '"' -f3)
guid=$(cat ck | grep -o "guid.*" | cut -d '"' -f3)
lsid=$(cat ck | grep -o "lsid.*" | cut -d '"' -f3)
rsa_modulus=$(cat ck | grep -o "rsa_modulus.*" | cut -d '"' -f3)
ck=$(echo "guid=$guid;  lsid=$lsid;  gsalt=$gsalt;  rsa_modulus=$rsa_modulus;")
}
sc(){
ts=$(expr $(date +%s%N) / 1000000)
sub_cmd=2
gsign=$(echo -n $appid$qversion$ts"36"$sub_cmd$gsalt | md5sum | cut -d ' ' -f1)
sign=$(echo -n $appid$qversion$country_code$mobile'4dtyyzKF3w6o54fJZnmeW3bVHl0$PbXj' | md5sum | cut -d ' ' -f1)
d="country_code=$country_code&client_ver=1.0.0&gsign=$gsign&appid=$appid&mobile=$mobile&sign=$sign&cmd=36&sub_cmd=$sub_cmd&qversion=$qversion&ts=$ts"
l=${#d}
curl -s -k -i --raw -o sc --http2 -X POST -H "Host:qapplogin.m.jd.com" -H "cookie:$ck" -H "user-agent:Mozilla/5.0 (Linux; Android 10; V1838T Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/98.0.4758.87 Mobile Safari/537.36 hap/1.9/vivo com.vivo.hybrid/1.9.6.302 com.jd.crplandroidhap/1.0.3 ({"packageName":"com.vivo.hybrid","type":"deeplink","extra":{}})" -H "accept-language:zh-CN,zh;q=0.9,en;q=0.8" -H "content-type:application/x-www-form-urlencoded; charset=utf-8" -H "content-length:$l" -H "accept-encoding:" -d "$d" "https://qapplogin.m.jd.com/cgi-bin/qapp/quick"
err_msg=$(cat sc | grep -o "err_msg.*" | cut -d '"' -f3)
[ -z $err_msg ] && echo 手机号为$mobile的验证码发送成功 || echo $err_msg
}
pt(){
read -p "请输入验证码: " smscode
ts=$(expr $(date +%s%N) / 1000000)
sub_cmd=3
gsign=$(echo -n $appid$qversion$ts"36"$sub_cmd$gsalt | md5sum | cut -d ' ' -f1)
d="country_code=$country_code&client_ver=1.0.0&gsign=$gsign&smscode=$smscode&appid=$appid&mobile=$mobile&cmd=36&sub_cmd=$sub_cmd&qversion=$qversion&ts=$ts"
l=${#d}
curl -s -k -i --raw -o pt --http2 -X POST -H "Host:qapplogin.m.jd.com" -H "cookie:$ck" -H "user-agent:Mozilla/5.0 (Linux; Android 10; V1838T Build/QP1A.190711.020; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/98.0.4758.87 Mobile Safari/537.36 hap/1.9/vivo com.vivo.hybrid/1.9.6.302 com.jd.crplandroidhap/1.0.3 ({"packageName":"com.vivo.hybrid","type":"deeplink","extra":{}})" -H "accept-language:zh-CN,zh;q=0.9,en;q=0.8" -H "content-type:application/x-www-form-urlencoded; charset=utf-8" -H "content-length:$l" -H "accept-encoding:" -d "country_code=$country_code&client_ver=1.0.0&gsign=$gsign&smscode=$smscode&appid=$appid&mobile=$mobile&cmd=36&sub_cmd=$sub_cmd&qversion=$qversion&ts=$ts" "https://qapplogin.m.jd.com/cgi-bin/qapp/quick"
err_msg=$(cat pt | grep -o "err_msg.*" | cut -d '"' -f3)
if [ -z $err_msg ]
then pt_key=$(cat pt | grep -o "pt_key.*" | cut -d '"' -f3)
pt_pin=$(cat pt | grep -o "pt_pin.*" | cut -d '"' -f3)
qlck="pt_key=$pt_key;pt_pin=$pt_pin;"

echo 你的JD_COOKIE为 $qlck 
date +%s
rm -rf ck sc pt
else echo $err_msg
fi
}
cl && ck && sc
[ -z $err_msg ] && pt