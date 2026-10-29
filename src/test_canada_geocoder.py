
import requests

url = "https://geolocator.api.geo.ca/"

tests = [
    ("T1Y", "Calgary, Alberta"),
    ("M3C", "Toronto, Ontario"),
    ("V6Z", "Vancouver, British Columbia"),
]

for postal_prefix, place in tests:
    print(f"\nTesting {postal_prefix} ({place})")

    try:
        response = requests.get(
            url,
            params={
                "q": postal_prefix,
                "lang": "en",
                "keys": "fsa",
            },
            timeout=30,
        )
        response.raise_for_status()
        results = response.json()

        if not results:
            print("No results returned")
        else:
            for result in results[:3]:
                print(result)

    except requests.RequestException as exc:
        print("Request failed:", exc)
    except ValueError as exc:
        print("Could not parse JSON response:", exc)
