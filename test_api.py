import requests

API_KEY = '6b845e21876738c1812355e2d8681a6e'

# Test: Get upcoming soccer matches
url = f'https://api.the-odds-api.com/v4/sports/soccer_epl/odds/?apiKey={API_KEY}&regions=eu&markets=h2h,spreads,totals&oddsFormat=decimal'

print("Making API request...")
response = requests.get(url)
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"Found {len(data)} matches")
    print(data)
else:
    print(f"Error: {response.text}")
