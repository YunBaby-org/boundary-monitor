from dotenv import load_dotenv
import urllib,os,requests,json

load_dotenv()
username = os.getenv("SMS_USER")
password = os.getenv("SMS_PASS")

def SendSMS(mobile,message):
    global username
    global password 
    msg = 'username='+username+'&password='+password+'&mobile='+mobile+'&message='+urllib.parse.quote(message)
    ans = requests.post('http://api.twsms.com/json/sms_send.php?'+msg)
    return json.loads(ans.text)
    #   {"code":"00000","text":"Success","msgid":340146985}
    #   code 00020 點數不足
    #   code 00000 完成
    #   code 00030 IP無使用權限

