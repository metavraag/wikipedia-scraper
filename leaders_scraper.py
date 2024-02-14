import requests


root_url = "https://country-leaders.onrender.com"
status_url = f"{root_url}/status"
cooke_url = f"{root_url}/cookie"
check_url = f"{root_url}/check"
contries_url = f"{root_url}/countries"
leaders_url = f"{root_url}/leaders"

cookie_response = requests.get(cooke_url)
cookies = cookie_response.cookies
print(cookies)

# status_response = requests.get(status_url)
status_response = requests.get(status_url, cookies=cookies)

print(status_response.json())

countries = requests.get(contries_url, cookies=cookies).json()
print(countries)
