import requests
import json
import csv
import math
from alive_progress import alive_bar

# initialize page counts for progress tracking
endpoint = "https://api.womenvsapes.io/projects/3/nfts/?page={start_page}&ordering=extra_data__rarity_ranking"
response = requests.get(endpoint.format(start_page=1))
response_json = json.loads(response.text)
total_count = response_json['count']
page_items_count = len(response_json['results'])
total_page_count = math.ceil(total_count/page_items_count)

# define starting page and dict for export
start_page = 1
toprocess_page_count = total_page_count - start_page + 1
toprocess_start = (start_page-1)*page_items_count+1
toprocess_count = toprocess_page_count*page_items_count
next_page = endpoint.format(start_page=start_page)
output_dict = []
with alive_bar(toprocess_count, title="Crawling API", title_length=24) as bar:
    for i in range(toprocess_start, total_count, page_items_count):
        if next_page == None:
            print("Not supposed to reach this code...")
            break
        response = requests.get(next_page)
        if response.status_code != 200:
            print("API request failed. Crawling interrupted.")
            break
        response_json = json.loads(response.text)
        next_page = response_json['next']
        results = response_json['results']
        results_minted = [x for x in results if x['token_address'] != None]
        for result in results_minted:
            output_dict.append({"id": result['id'],"token_address": result['token_address'], "token_id": result['token_id'], "name": result['metadata']['name'], "ranking": result['extra_data']['ranking'], "probability": "{:.32f}".format(float(result['extra_data']['probality'])), "rarity_ranking": result['extra_data']['rarity_ranking']})
        bar(len(results))

# define csv for export
csv_file = "wva.csv"
csv_columns = ['id','token_address','token_id','name','ranking','probability','rarity_ranking']
try:
    with open(csv_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
        writer.writeheader()
        # write wva metadata from dict to file
        with alive_bar(len(output_dict), title="Writing CSV", title_length=24) as bar:
            for data in output_dict:
                writer.writerow(data)
                bar()
        
except IOError:
    print("I/O error")