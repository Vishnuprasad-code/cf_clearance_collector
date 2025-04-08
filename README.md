# cf_clearance cookie collector API

A simple RESTful API that returns the response cookies after passing cloudflare human verificaton.

---
## About the Solver

This cf_clearance cookie collector API is designed to extract response cookies after passing cloudflare human verificaton using browser automation tool:- [nodriver](https://github.com/ultrafunkamsterdam/nodriver).

- Nodriver is an efficient browser automation tool that helps us pass cloudflare turnstile human verification. The API simply launches the nodriver chrome browser, visit the url given by the user, pass the human verfication, and extract and return the cookies.
- The API itself is built using **FastAPI**, providing a fast and intuitive web interface for interaction.
- Containerized using **Docker**, making it easy to deploy.

---
## API Setup

- git clone https://github.com/Vishnuprasad-code/cf_clearance_collector.git
- cd cf_clearance_collector
- docker-compose up --build

## Usage
- Create Task and fetch task id
```
url = "http://0.0.0.0:8000/solve_captcha/clouflare/create_task/"
payload = {
    "url": <url:str>,  # url of the site with cloudflare protection
    "browser_config_args": <config args: Dict>  #  nodriver config args as dict:- (https://ultrafunkamsterdam.github.io/nodriver/nodriver/classes/others_and_helpers.html#config-class)
}
response = requests.post(
    url=url,
    json=payload
)
print(response.status_code, response.json())
task_id = response.json().get('task_id')
'''
## sample payload
payload = {
    "url": "https://nopecha.com/demo/cloudflare",
    "browser_config_args": {
        "headless": False,
        "browser_args": [
            "--proxy-server=<your-proxy>"
        ],
        "lang": "en-US",
    }
}
## sample response
{'state': 'Created Task', 'task_id': '5bf3436c137411f0babe0e554f559473', 'error': None}
status: 201
'''
```
- Start polling for solution using the task id
```
while(True):
    url = "http://0.0.0.0:8000/solve_captcha/clouflare/get_cookie/"
    payload = {
        "task_id": task_id
    }
    response = requests.post(
        url=url,
        json=payload
    )
    print(response.json())
    if response.json().get("state") == "Finished":
        break

    time.sleep(20)
'''
## sample responses
{"state":"Processing","cookies":{},"error":null}
or
{
  "state": "Finished",
  "cookies": {
    "cookies": [
      {
        "name": "cf_clearance",
        "value": "1744006437-1.0.1.1-nimO3UKNZ9oA.oS.9GSnUbaYet0dxvCtYOpaKgMWuG8cRC3CrB8UewrdEqjpRtOgoxLBRUdYpP2Ar5DPD3ccgfhwe_WTIrI8wyaQm8d.X.Y",
        "path": "/"
      }
    ],
    "userAgent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
  },
  "error": null
}
'''
```
- Use the same user agent obtained from the response while using the cookies
- If you are passing --proxy-server make sure to use the same ip while uisng the cookies

---

