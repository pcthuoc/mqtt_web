import requests

# Thông tin cấu hình cho EMQX
EMQX_API_KEY = "26c669cd0814ac40"  # Thay bằng API Key của bạn
EMQX_SECRET_KEY = "mmQelPWPMCmMyrS9Bh9Aq39AhBPnbjukuFdVCAi9B8qFMEM"  # Thay bằng Secret Key của bạn
EMQX_URL = "http://165.232.166.11:8081/api/v5/acl"  # URL EMQX API để cấu hình ACL

def test_emqx_acl(api_key, topic):
    # Payload để cấu hình quyền cho một API Key
    payload = {
        "username": api_key,
        "topic": topic,
        "action": "subscribe"
    }

    # Gửi yêu cầu POST đến EMQX API
    response = requests.post(
        EMQX_URL,
        json=payload,
        auth=(EMQX_API_KEY, EMQX_SECRET_KEY),
        headers={"Content-Type": "application/json"}
    )

    # # Kiểm tra phản hồi từ EMQX
    # if response.status_code == 200:
    #     print(f"Successfully set ACL for API Key {api_key} on topic {topic}")
    # else:
    #     print(f"Failed to set ACL: {response.status_code} - {response.content}")

# Gọi hàm để kiểm tra
test_emqx_acl("your_test_api_key", "API/your_test_api_key")
