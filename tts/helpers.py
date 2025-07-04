import requests

def check_internet_connectivity(url="https://www.google.com", timeout=5):
    try:
        response = requests.get(url, timeout=timeout)
        return True if response.status_code == 200 else False
    except requests.RequestException:
        return False
    
def check_is_video_url_connectivity(url, timeout):
    try:
        response = requests.get(url, timeout=timeout)
        return True if response.status_code == 200 else False
    except requests.RequestException:
        return False

