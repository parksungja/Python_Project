from flask import Flask, jsonify

app = Flask(__name__)

# 셔틀버스 시간표 데이터
shuttle_schedule = {
    "morning": "08:00, 09:00, 10:00",
    "afternoon": "13:00, 14:00, 15:00",
    "evening": "17:00, 18:00, 19:00"
}

# 셔틀버스 시간표를 웹 페이지로 출력
@app.route('/schedule', methods=['GET'])
def get_schedule():
    return jsonify(shuttle_schedule)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, ssl_context=('cert.pem', 'key.pem'), debug=False)
    
import requests

# 카카오톡 REST API 키
REST_API_KEY = 'e697ca8e3b671b1804fbbfcbf8dd957c'
REDIRECT_URI = 'https://localhost:8080/oauth'  # 예: http://localhost:5000/oauth

# 엑세스 토큰 
Access_token = 'tcXTC_7EKEtzVhjemXoduKM4RVtWSSdH4jarrazla3B5DEu4FijCkwAAAAQKPXObAAABktvWoGUFVMIyByjmyg'

auth_code = 'AUTH_CODE_FROM_REDIRECT'
access_token = get_access_token(auth_code)
print(f"발급된 액세스 토큰: {access_token}")

import json
def send_kakao_message(access_token):
    url = "https://kapi.kakao.com/v2/api/talk/memo/default/send"
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # 카카오톡 메시지 내용 설정 (템플릿)
    data = {
        "template_object": json.dumps({
            "object_type": "text",
            "text": "셔틀버스 시간표 알림입니다.",
            "link": {
                "web_url": "http://yourwebsite.com/schedule",
                "mobile_web_url": "http://yourwebsite.com/schedule"
            },
            "button_title": "시간표 확인"
        })
    }
    
    response = requests.post(url, headers=headers, data=data)
    
    if response.status_code == 200:
        print("메시지 전송 성공")
    else:
        print(f"메시지 전송 실패: {response.status_code}, {response.text}")

# 메시지 전송
send_kakao_message(access_token)

