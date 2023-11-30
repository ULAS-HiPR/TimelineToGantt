from dotenv import load_dotenv
import os
import sys
import requests

load_dotenv()
notionToken = os.getenv("NOTION_TOKEN")

def get_header():
    return {
    "Authorization": notionToken,
     "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
    }

def get_ids(page_id):
    print("https://api.notion.com/v1/pages/" + page_id)
    response = requests.get("https://api.notion.com/v1/pages/" + page_id, headers=get_header())
    print(response.content)
    pass

def main(page_id):
    #db_id, graph_id = get_ids(page_id)
    get_ids(page_id)


try:
    main(sys.argv[1])
except:
    main(os.getenv("PAGE_ID"))