/*
2021.01.09 极速版59-20抢券 [exchange_59_20.js]
cron:0 59 6,9,14,17,20 * * *
 */


let ck_str = process.env.YANGYANG_EXCHANGE_CKS ? process.env.YANGYANG_EXCHANGE_CKS : "0@1@2@3"; // 需要抢的号

let ck_str_items=ck_str.split("@");  //分割成字符串数组
let ck_int_items=[];//保存转换后的整型字符串
   


const $ = new Env('59-20抢券');
const moment = require('moment');
const notify = $.isNode() ? require('./sendNotify') : '';
//Node.js用户请在jdCookie.js处填写京东ck;
const jdCookieNode = $.isNode() ? require('./jdCookie.js') : '';
let jdNotify = true;//是否关闭通知，false打开通知推送，true关闭通知推送

//IOS等用户直接用NobyDa的jd cookie
let cookiesArr = [], cookie = '', message;
if ($.isNode()) {
  Object.keys(jdCookieNode).forEach((item) => {
    cookiesArr.push(jdCookieNode[item])
  })
  if (process.env.JD_DEBUG && process.env.JD_DEBUG === 'false') console.log = () => {
  };
} else {
  cookiesArr = [$.getdata('CookieJD'), $.getdata('CookieJD2'), ...jsonParse($.getdata('CookiesJD') || "[]").map(item => item.cookie)].filter(item => !!item);
}

let start_hour = process.env.YANGYANG_EXCHANGE_FULI_START_HOUR ? parseInt(process.env.YANGYANG_EXCHANGE_FULI_START_HOUR) : 13;
let end_hour = process.env.YANGYANG_EXCHANGE_FULI_END_HOUR ? parseInt(process.env.YANGYANG_EXCHANGE_FULI_END_HOUR) : 17;
let waiting_time =  process.env.YANGYANG_EXCHANGE_WAITING_TIME ? parseInt(process.env.YANGYANG_EXCHANGE_WAITING_TIME) : 56000;

const h = (new Date()).getHours()
const fuli_time = h >= start_hour && h <= end_hour


ck_str_items.forEach(item => {  
  ck_int_items.push(+item);  
});
let ck_int_items_mask = new Array(cookiesArr.length);
for (let i = 0; i < ck_int_items_mask.length; i ++) {
  ck_int_items_mask[i] = false;
}

for (let i = 0; i < ck_int_items.length; i ++) {
  ck_int_items_mask[ck_int_items[i]] = true;
}
let buf_cookiesArr = [];

for (let i = 0; i < ck_int_items_mask.length; i ++) {
  // 内部成员抢券
  if (!fuli_time) {
    if (ck_int_items_mask[i]) {
      buf_cookiesArr.push(cookiesArr[i]);
    }
  }
  // 外部成员
  else {
    if (!ck_int_items_mask[i]) {
      buf_cookiesArr.push(cookiesArr[i]);
    }
  }
}

cookiesArr = buf_cookiesArr;
// 循环次数
let randomCount = process.env.YANGYANG_EXCHANGE_LOOP_TIMES ? Math.ceil(parseInt(process.env.YANGYANG_EXCHANGE_LOOP_TIMES) / cookiesArr.length) : 10;
console.log("循环次数为", randomCount);
console.log("总循环次数为", randomCount*cookiesArr.length);

const JD_API_HOST = 'https://api.m.jd.com/client.action?';
let wait = ms => new Promise(resolve => setTimeout(resolve, ms));
!(async () => {
  if (!cookiesArr[0]) {
    $.msg($.name, '【提示】请先获取京东账号一cookie\n直接使用NobyDa的京东签到获取', 'https://bean.m.jd.com/bean/signIndex.action', { "open-url": "https://bean.m.jd.com/bean/signIndex.action" });
    return;
  }
  console.log("准备开始抢券！")
  // 等57秒再抢
  await wait(waiting_time)
  for (let j = 0; j < randomCount; ++j)
    for (let i = 0; i < cookiesArr.length; i++) {
      if (cookiesArr[i]) {
        cookie = cookiesArr[i];
        $.UserName = decodeURIComponent(cookie.match(/pt_pin=([^; ]+)(?=;?)/) && cookie.match(/pt_pin=([^; ]+)(?=;?)/)[1])
        $.index = i + 1;
        console.log(`*********京东账号${$.index} ${$.UserName}*********`)
        $.isLogin = true;
        $.nickName = '';
        message = '';
        await jdCar();
      }
    }
})()
  .catch((e) => {
    $.log('', `❌ ${$.name}, 失败! 原因: ${e}!`, '')
  })
  .finally(() => {
    $.done();
  })

async function jdCar() {
  await exchange()
}

function showMsg() {
  return new Promise(resolve => {
    $.msg($.name, '', `【京东账号${$.index}】${$.nickName}\n${message}`);
    resolve()
  })
}

function exchange() {
  return new Promise(resolve => {
    $.post(taskUrl('functionId=lite_newBabelAwardCollection'), (err, resp, data) => {
      try {
        if (err) {
          console.log(`${JSON.stringify(err)}`)
          console.log(`${$.name} user/exchange/bean API请求失败，请检查网路重试\n`)
        } else {
          console.log(moment().format("YYYY-MM-DD HH:mm:ss.SSS"));
          console.log(data);
          if (safeGet(data)) {
            data = JSON.parse(data);
            console.log(`抢券结果：${JSON.stringify(data)}\n`)
          }
        }
      } catch (e) {
        $.logErr(e, resp)
      } finally {
        resolve();
      }
    })
  })
}

function taskUrl(function_id, body = {}) {
  return {
    // url: `${JD_API_HOST}${function_id}?timestamp=${new Date().getTime() + new Date().getTimezoneOffset() * 60 * 1000 + 8 * 60 * 60 * 1000}`,
    url: `https://api.m.jd.com/client.action?functionId=receiveNecklaceCoupon`,
    headers: {
      "Accept": "*/*",
      "Accept-Encoding": "gzip, deflate, br",
      "Accept-Language": "zh-cn",
      "Connection": "keep-alive",
      "Content-Type": "application/x-www-form-urlencoded",
      'origin': 'https://prodev.m.jd.com',
      "Referer": "https://prodev.m.jd.com/jdlite/active/3qRAXpNehcsUpToARD9ekP4g6Jhi/index.html?__in_task_view__=jdLiteiOS&lng=113.501145&lat=22.239933&sid=2914b193bd74ab1111eb83e2ed369f8w&un_area=19_1607_3639_59644",
      "Cookie": cookie,
      "User-Agent": $.isNode() ? (process.env.JD_USER_AGENT ? process.env.JD_USER_AGENT : (require('./USER_AGENTS').USER_AGENT)) : ($.getdata('JDUA') ? $.getdata('JDUA') : "jdapp;iPhone;9.4.4;14.3;network/4g;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1"),
    },
    // body= "body={%22activityId%22:%223H885vA4sQj6ctYzzPVix4iiYN2P%22,%22scene%22:%221%22,%22args%22:%22key=A8B9E46AA230D12669B22F6E084C303E06132BB42A39FFB7B285EC61204648F3FE5373963CA264B6CC02566AB901DE98_babel,roleId=BE49B763F657D252312B5D9E866C34EF_babel,strengthenKey=E9632480FF1A5F1B4D66C5999347325B3F3103AEC45237750EB4B4CE785A9F35CAB9C308E7AFE14C2AAD590FE2A2D709_babel%22}&screen=750*1334&client=wh5&clientVersion=1.0.0"
    body: "body=%7B%22shshshfpb%22%3A%22JD0111d47dcT9hP9WRvk164429978244003SLYoasrQ8hZkkBXNZqTojLP6pXPA5bfYXhS0q92ubiIOHNFyAkX9PWLbmgyTDBq2tk0r3GcKvQk6mVgihhLfRhMZnHeuBbWMoZE17r0t50E1nc1qmq~k%5C/JWwU6dNQpwxW8QYlciL9%2BBd9mPsllwQMWu7OAPj6YRch0zv4ksAz3w%2BnBoZYnuJJwDE18tolOm8rqgSf7%5C/uZA%3D%3D%22%2C%22globalLng%22%3A%2262a08f6788983aab59e41c8ea75ebf54f90f3c961d906c3c5dc8943e41731fe0%22%2C%22globalLat%22%3A%2244e380f87201ef296678e742783d789dcabf23802bfb39147dc9096b0e418cbe%22%2C%22couponSource%22%3A%22manual%22%2C%22channel%22%3A%22%E9%A2%86%E5%88%B8%E4%B8%AD%E5%BF%83%22%2C%22monitorSource%22%3A%22ccresource_ios_index_config%22%2C%22source%22%3A%22couponCenter_app%22%2C%22childActivityUrl%22%3A%22openapp.jdmobile%253a%252f%252fvirtual%253fparams%253d%257b%255c%2522category%255c%2522%253a%255c%2522jump%255c%2522%252c%255c%2522des%255c%2522%253a%255c%2522couponCenter%255c%2522%257d%22%2C%22pageClickKey%22%3A%22CouponCenter%22%2C%22rcType%22%3A%224%22%2C%22batchId%22%3A%22838474366%22%2C%22lat%22%3A%2244e380f87201ef296678e742783d789dcabf23802bfb39147dc9096b0e418cbe%22%2C%22extend%22%3A%2288DB80104521161CDFFBD5A8057E28D3EF2A36CD609FB9F93630C431EC3F2FF7A213BE06482C2B115ACD30536499B3CB0A01A2E3517769E5B0D9D7A5FEB8B889BD33FABABAAE44534079014FFCB53C97E4B83FDFBF4D390B5981BCB1425ED380A6899D989FA0A8BD599EFAA992F18E08F0EDBD1C98F3FDD9C3D8868755C40A29FD24CD82692E698A804D1CF84FBF64469DAAE1D4A18BCBC81A719FF6FA20A69AD2CC6BA9BC1D7D9260AFCB101491B9AC7E5DA6E5A8541A03F267F95AE8C4BFA5BD35C5C49C4E08541A7F779BE86F0D28779B79689C1419EBBEE37AD1040A66A788C7B98A813A7C555933FB648795E653D6D8A88FDBE69BCC672084ECFD8A23B955E1BE1666565328CF378A8B06529D3197B5E899EF72D6F5EB0F09110E43F80E4C862357FAFAAE6099A1592F07022FF446B0742A400C015E02E2AB1CB10FBBF8AB0D70D6491DE0DA0E345A784CFEB73E3C04D4B3DFC726A27FA276D6A4C47056%22%2C%22subChannel%22%3A%22feeds%E6%B5%81%22%2C%22lng%22%3A%2262a08f6788983aab59e41c8ea75ebf54f90f3c961d906c3c5dc8943e41731fe0%22%2C%22couponSourceDetail%22%3Anull%2C%22eid%22%3A%22eidIc53c81217fs8ni223iz6RzemO4UMVKKgWJ4tuEuaMOrgwe4l8JtEUlSh%5C/aGhA6T54E1HBQIbBabKuXIlImDNSCF%2BUoSe7eYTH8DAlBcbuYu95oVr%22%7D&build=167963&client=apple&clientVersion=10.3.6&d_brand=apple&d_model=iPhone12%2C1&ef=1&eid=eidIc53c81217fs8ni223iz6RzemO4UMVKKgWJ4tuEuaMOrgwe4l8JtEUlSh/aGhA6T54E1HBQIbBabKuXIlImDNSCF%2BUoSe7eYTH8DAlBcbuYu95oVr&ep=%7B%22ciphertype%22%3A5%2C%22cipher%22%3A%7B%22screen%22%3A%22ENS4AtO3EJS%3D%22%2C%22area%22%3A%22CJVpCJSnC18zDNK4XzcnDzOn%22%2C%22wifiBssid%22%3A%22DQHvD2PvYwDuDNvuENqyD2ZwDJOnZJZvZtVsCtUyZWY%3D%22%2C%22osVersion%22%3A%22CJUkCs4n%22%2C%22uuid%22%3A%22aQf1ZRdxb2r4ovZ1EJZhcxYlVNZSZz09%22%2C%22adid%22%3A%22DUC0GJu2CUUjHJKmGI00CJDPBUTODJujCtO0CNc3GJC0C0DM%22%2C%22openudid%22%3A%22CzZuYJvrEJU5CNvwYwYzD2C3CNdsD2GnENqyDJG0ZtZtCJC4ENZvCK%3D%3D%22%7D%2C%22ts%22%3A1644299668%2C%22hdid%22%3A%22JM9F1ywUPwflvMIpYPok0tt5k9kW4ArJEU3lfLhxBqw%3D%22%2C%22version%22%3A%221.0.3%22%2C%22appname%22%3A%22com.360buy.jdmobile%22%2C%22ridx%22%3A-1%7D&ext=%7B%22prstate%22%3A%220%22%2C%22pvcStu%22%3A%221%22%7D&isBackground=N&joycious=44&lang=zh_CN&networkType=wifi&networklibtype=JDNetworkBaseAF&partner=apple&rfs=0000&scope=11&sign=95d02c5fa16a008c6e37ecd5a11fd083&st=1644300003201&sv=112&uemps=0-0&uts=0f31TVRjBSsqndu4/jgUPz6uymy50MQJkkTzNFVdh/hkbmP2i2twYYJqsu1pwkDGEOztzxjOoHX57XM62Pz4ZwHLpYOuLAAUo836uelXIM/zx812zSy22XgqIKVfRoxqQp35rLzr4XBugRGBEm0LvljjEmm9P5mhAltdeIb0sVmf2UHb9t6L8UVAmGqX/UD88IpsXffVP%2BL5cuFi93A5UQ%3D%3D"
  }
}


function TotalBean() {
  return new Promise(async resolve => {
    const options = {
      "url": `https://wq.jd.com/user/info/QueryJDUserInfo?sceneval=2`,
      "headers": {
        "Accept": "application/json,text/plain, */*",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br",
        "Accept-Language": "zh-cn",
        "Connection": "keep-alive",
        "Cookie": cookie,
        "Referer": "https://wqs.jd.com/my/jingdou/my.shtml?sceneval=2",
        "User-Agent": $.isNode() ? (process.env.JD_USER_AGENT ? process.env.JD_USER_AGENT : (require('./USER_AGENTS').USER_AGENT)) : ($.getdata('JDUA') ? $.getdata('JDUA') : "jdapp;iPhone;9.4.4;14.3;network/4g;Mozilla/5.0 (iPhone; CPU iPhone OS 14_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148;supportJDSHWK/1")
      }
    }
    $.post(options, (err, resp, data) => {
      try {
        if (err) {
          console.log(`${JSON.stringify(err)}`)
          console.log(`${$.name} API请求失败，请检查网路重试`)
        } else {
          if (data) {
            data = JSON.parse(data);
            if (data['retcode'] === 13) {
              $.isLogin = false; //cookie过期
              return
            }
            if (data['retcode'] === 0) {
              $.nickName = (data['base'] && data['base'].nickname) || $.UserName;
            } else {
              $.nickName = $.UserName
            }
          } else {
            console.log(`京东服务器返回空数据`)
          }
        }
      } catch (e) {
        $.logErr(e, resp)
      } finally {
        resolve();
      }
    })
  })
}

function safeGet(data) {
  try {
    if (typeof JSON.parse(data) == "object") {
      return true;
    }
  } catch (e) {
    console.log(e);
    console.log(`京东服务器访问数据为空，请检查自身设备网络情况`);
    return false;
  }
}
function jsonParse(str) {
  if (typeof str == "string") {
    try {
      return JSON.parse(str);
    } catch (e) {
      console.log(e);
      $.msg($.name, '', '请勿随意在BoxJs输入框修改内容\n建议通过脚本去获取cookie')
      return [];
    }
  }
}
// prettier-ignore
function Env(t, e) { "undefined" != typeof process && JSON.stringify(process.env).indexOf("GITHUB") > -1 && process.exit(0); class s { constructor(t) { this.env = t } send(t, e = "GET") { t = "string" == typeof t ? { url: t } : t; let s = this.get; return "POST" === e && (s = this.post), new Promise((e, i) => { s.call(this, t, (t, s, r) => { t ? i(t) : e(s) }) }) } get(t) { return this.send.call(this.env, t) } post(t) { return this.send.call(this.env, t, "POST") } } return new class { constructor(t, e) { this.name = t, this.http = new s(this), this.data = null, this.dataFile = "box.dat", this.logs = [], this.isMute = !1, this.isNeedRewrite = !1, this.logSeparator = "\n", this.startTime = (new Date).getTime(), Object.assign(this, e), this.log("", `🔔${this.name}, 开始!`) } isNode() { return "undefined" != typeof module && !!module.exports } isQuanX() { return "undefined" != typeof $task } isSurge() { return "undefined" != typeof $httpClient && "undefined" == typeof $loon } isLoon() { return "undefined" != typeof $loon } toObj(t, e = null) { try { return JSON.parse(t) } catch { return e } } toStr(t, e = null) { try { return JSON.stringify(t) } catch { return e } } getjson(t, e) { let s = e; const i = this.getdata(t); if (i) try { s = JSON.parse(this.getdata(t)) } catch { } return s } setjson(t, e) { try { return this.setdata(JSON.stringify(t), e) } catch { return !1 } } getScript(t) { return new Promise(e => { this.get({ url: t }, (t, s, i) => e(i)) }) } runScript(t, e) { return new Promise(s => { let i = this.getdata("@chavy_boxjs_userCfgs.httpapi"); i = i ? i.replace(/\n/g, "").trim() : i; let r = this.getdata("@chavy_boxjs_userCfgs.httpapi_timeout"); r = r ? 1 * r : 20, r = e && e.timeout ? e.timeout : r; const [o, h] = i.split("@"), n = { url: `http://${h}/v1/scripting/evaluate`, body: { script_text: t, mock_type: "cron", timeout: r }, headers: { "X-Key": o, Accept: "*/*" } }; this.post(n, (t, e, i) => s(i)) }).catch(t => this.logErr(t)) } loaddata() { if (!this.isNode()) return {}; { this.fs = this.fs ? this.fs : require("fs"), this.path = this.path ? this.path : require("path"); const t = this.path.resolve(this.dataFile), e = this.path.resolve(process.cwd(), this.dataFile), s = this.fs.existsSync(t), i = !s && this.fs.existsSync(e); if (!s && !i) return {}; { const i = s ? t : e; try { return JSON.parse(this.fs.readFileSync(i)) } catch (t) { return {} } } } } writedata() { if (this.isNode()) { this.fs = this.fs ? this.fs : require("fs"), this.path = this.path ? this.path : require("path"); const t = this.path.resolve(this.dataFile), e = this.path.resolve(process.cwd(), this.dataFile), s = this.fs.existsSync(t), i = !s && this.fs.existsSync(e), r = JSON.stringify(this.data); s ? this.fs.writeFileSync(t, r) : i ? this.fs.writeFileSync(e, r) : this.fs.writeFileSync(t, r) } } lodash_get(t, e, s) { const i = e.replace(/\[(\d+)\]/g, ".$1").split("."); let r = t; for (const t of i) if (r = Object(r)[t], void 0 === r) return s; return r } lodash_set(t, e, s) { return Object(t) !== t ? t : (Array.isArray(e) || (e = e.toString().match(/[^.[\]]+/g) || []), e.slice(0, -1).reduce((t, s, i) => Object(t[s]) === t[s] ? t[s] : t[s] = Math.abs(e[i + 1]) >> 0 == +e[i + 1] ? [] : {}, t)[e[e.length - 1]] = s, t) } getdata(t) { let e = this.getval(t); if (/^@/.test(t)) { const [, s, i] = /^@(.*?)\.(.*?)$/.exec(t), r = s ? this.getval(s) : ""; if (r) try { const t = JSON.parse(r); e = t ? this.lodash_get(t, i, "") : e } catch (t) { e = "" } } return e } setdata(t, e) { let s = !1; if (/^@/.test(e)) { const [, i, r] = /^@(.*?)\.(.*?)$/.exec(e), o = this.getval(i), h = i ? "null" === o ? null : o || "{}" : "{}"; try { const e = JSON.parse(h); this.lodash_set(e, r, t), s = this.setval(JSON.stringify(e), i) } catch (e) { const o = {}; this.lodash_set(o, r, t), s = this.setval(JSON.stringify(o), i) } } else s = this.setval(t, e); return s } getval(t) { return this.isSurge() || this.isLoon() ? $persistentStore.read(t) : this.isQuanX() ? $prefs.valueForKey(t) : this.isNode() ? (this.data = this.loaddata(), this.data[t]) : this.data && this.data[t] || null } setval(t, e) { return this.isSurge() || this.isLoon() ? $persistentStore.write(t, e) : this.isQuanX() ? $prefs.setValueForKey(t, e) : this.isNode() ? (this.data = this.loaddata(), this.data[e] = t, this.writedata(), !0) : this.data && this.data[e] || null } initGotEnv(t) { this.got = this.got ? this.got : require("got"), this.cktough = this.cktough ? this.cktough : require("tough-cookie"), this.ckjar = this.ckjar ? this.ckjar : new this.cktough.CookieJar, t && (t.headers = t.headers ? t.headers : {}, void 0 === t.headers.Cookie && void 0 === t.cookieJar && (t.cookieJar = this.ckjar)) } get(t, e = (() => { })) { t.headers && (delete t.headers["Content-Type"], delete t.headers["Content-Length"]), this.isSurge() || this.isLoon() ? (this.isSurge() && this.isNeedRewrite && (t.headers = t.headers || {}, Object.assign(t.headers, { "X-Surge-Skip-Scripting": !1 })), $httpClient.get(t, (t, s, i) => { !t && s && (s.body = i, s.statusCode = s.status), e(t, s, i) })) : this.isQuanX() ? (this.isNeedRewrite && (t.opts = t.opts || {}, Object.assign(t.opts, { hints: !1 })), $task.fetch(t).then(t => { const { statusCode: s, statusCode: i, headers: r, body: o } = t; e(null, { status: s, statusCode: i, headers: r, body: o }, o) }, t => e(t))) : this.isNode() && (this.initGotEnv(t), this.got(t).on("redirect", (t, e) => { try { if (t.headers["set-cookie"]) { const s = t.headers["set-cookie"].map(this.cktough.Cookie.parse).toString(); s && this.ckjar.setCookieSync(s, null), e.cookieJar = this.ckjar } } catch (t) { this.logErr(t) } }).then(t => { const { statusCode: s, statusCode: i, headers: r, body: o } = t; e(null, { status: s, statusCode: i, headers: r, body: o }, o) }, t => { const { message: s, response: i } = t; e(s, i, i && i.body) })) } post(t, e = (() => { })) { if (t.body && t.headers && !t.headers["Content-Type"] && (t.headers["Content-Type"] = "application/x-www-form-urlencoded"), t.headers && delete t.headers["Content-Length"], this.isSurge() || this.isLoon()) this.isSurge() && this.isNeedRewrite && (t.headers = t.headers || {}, Object.assign(t.headers, { "X-Surge-Skip-Scripting": !1 })), $httpClient.post(t, (t, s, i) => { !t && s && (s.body = i, s.statusCode = s.status), e(t, s, i) }); else if (this.isQuanX()) t.method = "POST", this.isNeedRewrite && (t.opts = t.opts || {}, Object.assign(t.opts, { hints: !1 })), $task.fetch(t).then(t => { const { statusCode: s, statusCode: i, headers: r, body: o } = t; e(null, { status: s, statusCode: i, headers: r, body: o }, o) }, t => e(t)); else if (this.isNode()) { this.initGotEnv(t); const { url: s, ...i } = t; this.got.post(s, i).then(t => { const { statusCode: s, statusCode: i, headers: r, body: o } = t; e(null, { status: s, statusCode: i, headers: r, body: o }, o) }, t => { const { message: s, response: i } = t; e(s, i, i && i.body) }) } } time(t, e = null) { const s = e ? new Date(e) : new Date; let i = { "M+": s.getMonth() + 1, "d+": s.getDate(), "H+": s.getHours(), "m+": s.getMinutes(), "s+": s.getSeconds(), "q+": Math.floor((s.getMonth() + 3) / 3), S: s.getMilliseconds() }; /(y+)/.test(t) && (t = t.replace(RegExp.$1, (s.getFullYear() + "").substr(4 - RegExp.$1.length))); for (let e in i) new RegExp("(" + e + ")").test(t) && (t = t.replace(RegExp.$1, 1 == RegExp.$1.length ? i[e] : ("00" + i[e]).substr(("" + i[e]).length))); return t } msg(e = t, s = "", i = "", r) { const o = t => { if (!t) return t; if ("string" == typeof t) return this.isLoon() ? t : this.isQuanX() ? { "open-url": t } : this.isSurge() ? { url: t } : void 0; if ("object" == typeof t) { if (this.isLoon()) { let e = t.openUrl || t.url || t["open-url"], s = t.mediaUrl || t["media-url"]; return { openUrl: e, mediaUrl: s } } if (this.isQuanX()) { let e = t["open-url"] || t.url || t.openUrl, s = t["media-url"] || t.mediaUrl; return { "open-url": e, "media-url": s } } if (this.isSurge()) { let e = t.url || t.openUrl || t["open-url"]; return { url: e } } } }; if (this.isMute || (this.isSurge() || this.isLoon() ? $notification.post(e, s, i, o(r)) : this.isQuanX() && $notify(e, s, i, o(r))), !this.isMuteLog) { let t = ["", "==============📣系统通知📣=============="]; t.push(e), s && t.push(s), i && t.push(i), console.log(t.join("\n")), this.logs = this.logs.concat(t) } } log(...t) { t.length > 0 && (this.logs = [...this.logs, ...t]), console.log(t.join(this.logSeparator)) } logErr(t, e) { const s = !this.isSurge() && !this.isQuanX() && !this.isLoon(); s ? this.log("", `❗️${this.name}, 错误!`, t.stack) : this.log("", `❗️${this.name}, 错误!`, t) } wait(t) { return new Promise(e => setTimeout(e, t)) } done(t = {}) { const e = (new Date).getTime(), s = (e - this.startTime) / 1e3; this.log("", `🔔${this.name}, 结束! 🕛 ${s} 秒`), this.log(), (this.isSurge() || this.isQuanX() || this.isLoon()) && $done(t) } }(t, e) }
