import requests
from time import sleep
import csv
import tqdm as tqdm
import argparse

def banner():
    print("""
        __ __   __           __
.-----.|__|  |_|  |--.--.--.|  |--.
|  _  ||  |   _|     |  |  ||  _  |
|___  ||__|____|__|__|_____||_____|
|_____|
        __  by @khast3x
.-----.|  |_.---.-.----.--------.---.-.-----.
|__ --||   _|  _  |   _|        |  _  |  _  |
|_____||____|___._|__| |__|__|__|___._|   __|
                                      |__|
          """)

class Repo:

    def __init__(self, full_name, description, html_url, language,
                 stargazers_count, created_at, pushed_at):
        self.full_name = full_name
        self.description = description
        self.html_url = html_url
        self.language = language
        self.stargazers_count = stargazers_count
        self.created_at = created_at
        self.pushed_at = pushed_at

banner()
parser = argparse.ArgumentParser(description="Export target's starred repositories from github to a CSV file. You can either use a github user token or call the api anonymously. This limited to 60 requests per hour.")
parser.add_argument("-u", "--username", action="store", help="Target Github username", dest="username", required=True)
parser.add_argument("-t", "--token", action="store", help="Github token to allow more requests to API. Max is 60 requests per hour", dest="token", default="")
parser.add_argument("-o", "--output", action="store", help="CSV output filename", dest="dest_csv", default="stars.csv")
args = parser.parse_args()

if args.token:
    print("* Using custom github token")
    user_token = "Bearer {}".format(args.token)
else:
    print("* Using rate-limited mode (No Auth)")
    user_token = ""

headers = {'Authorization': user_token}
url = "https://api.github.com/users/{}/starred".format(args.username)

response = requests.request("GET", url, headers=headers)
data_set = []
print("* Getting all Github starred pages and repos\n")
for i in tqdm.trange(int(response.links["last"]["url"].split("=")[1]) - 1):
    raw = response.json()
    for r in raw:
        data_set.append(Repo(r["full_name"], r["description"],
                             r["html_url"], r["language"],
                             r["stargazers_count"], r["created_at"],
                             r["pushed_at"]))

    response = requests.request("GET", response.links["next"]["url"], headers=headers)
    sleep(0.1)

with open(args.dest_csv, 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile)

    spamwriter.writerow(["full_name", "description", "html_url", "language",
                        "stargazers_count", "created_at", "pushed_at"])
    print("* Writing to CSV\n")
    for repo in tqdm.tqdm(data_set):
        spamwriter.writerow([repo.full_name, repo.description, repo.html_url,
                            repo.language, repo.stargazers_count,
                            repo.created_at, repo.pushed_at])
    print("\n* Found a total of {} repositories\n* Done writing to {}\n\n-> You can use https://app.rawgraphs.io or a worksheet software to manipulate your data".format(len(data_set), args.dest_csv))
