from dotenv import load_dotenv
import os
import sys
import requests
import json
from datetime import datetime

load_dotenv()
notionToken = os.getenv("NOTION_TOKEN")

class Task:
    def __init__(self,name,type,date,status) -> None:
        self.name = name
        self.type = type
        self.date = date
        self.status = status
    
    def dateRange(self):
        self.start = self.date["start"]
        self.start = self.start[:19] if len(self.start) > 20 else self.start
        self.startDate = datetime.fromisoformat(self.start)
        if self.date["end"]:
            self.end = self.date["end"]
            self.end = self.end[:19] if len(self.end) > 20 else self.end
            self.range =  datetime.fromisoformat(self.end) - datetime.fromisoformat(self.start)
            if "days" in str(self.range):
                self.range = str(self.range).replace(" days","d")[:-9]
            if "day" in str(self.range):
                self.range = str(self.range).replace(" day","d")[:-9]
            if "hours" in str(self.range):
                self.range = str(self.range).replace(" hours","h")[:-9]
            if "hour" in str(self.range):
                self.range = str(self.range).replace(" hour","h")[:-9]
            if "minutes" in str(self.range):
                self.range = str(self.range).replace(" minutes","m")[:-9]
            if "minute" in str(self.range):
                self.range = str(self.range).replace(" minutes","m")[:-9]
        else :
            self.range = "1h"

        return self

def get_header():
    return {
    "Authorization": notionToken,
     "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
    }

def retrieveBlockChildren(block_id):
    response = requests.get("https://api.notion.com/v1/blocks/" + block_id + "/children", headers=get_header())
    return response.json()["results"]

def retrieveDatabase(database_id):
    response = requests.post("https://api.notion.com/v1/databases/" + database_id + "/query", headers=get_header())
    return response.json()["results"]

def get_ids(page_id):
    response = retrieveBlockChildren(page_id)
    for block in response:
        if "code" in block:
            if block["code"]["language"] == "mermaid":
                graph_id = block["id"]
                #print(graph_id)
        if "heading_2" in block:
            if block["heading_2"]["rich_text"][0]["text"]["content"] == "Database":
                response = retrieveBlockChildren(block["id"])
                for child in response:
                    if "child_database" in child:
                        db_id = child["id"]
    return db_id,graph_id

def get_tasks(database_id):
    response = retrieveDatabase(database_id)
    tasks = []
    for task in response:
        tasks.append(Task(task["properties"]["Name"]["title"][0]["text"]["content"],
                          task["properties"]["Type"]["multi_select"][0]["name"],
                          task["properties"]["Date"]["date"],
                          task["properties"]["Status"]["status"]["name"]))
    return tasks

def seperate_tasks(tasks):
    dates =  [task for task in tasks if task.type == "Dates"]
    rockets = [task for task in tasks if task.type == "Eningeering"]
    org = [task for task in tasks if task.type == "Organisation"]
    docs = [task for task in tasks if task.type == "Documentation"]
    other = [task for task in tasks if task.type == "Other"]

    return dates,rockets,org,docs,other

def generate_mermaid(dates,rockets,org,docs,other):
    mermaid = "gantt\n"
    mermaid += "dateFormat YYYY-MM-DD\n"
    mermaid += "title Gantt Chart\n"
    mermaid += "section Dates\n"
    for task in dates:
        mermaid += task.name + " : " + task.start + ", " + task.range + "\n"
    mermaid += "section Engineering\n"
    for task in rockets:
        mermaid += task.name + " : " + task.start + ", " + task.range + "\n"
    mermaid += "section Organisation\n"
    for task in org:
        mermaid += task.name + " : " + task.start + ", " + task.range + "\n"
    mermaid += "section Documentation\n"
    for task in docs:
        mermaid += task.name + " : " + task.start + ", " + task.range + "\n"
    mermaid += "section Other\n"
    for task in other:
        mermaid += task.name + " : " + task.start + ", " + task.range + "\n"
    return mermaid

def update_graph(graph_id,mermaid):
    data =  {
        "code":{
        "rich_text": [
            {
                "type": "text",
                "text": {
                    "content": mermaid,
                }
            }]   
        }
    }
    
    response = requests.patch("https://api.notion.com/v1/blocks/" + graph_id, headers=get_header(), json=data)
    print(response)

def get_graph(graph_id):
    response = requests.get("https://api.notion.com/v1/blocks/" + graph_id, headers=get_header())
    print(response.json())

def main(page_id):
    db_id, graph_id = get_ids(page_id)
    tasks = get_tasks(db_id)

    tasks = [task.dateRange() for task in tasks if task.date]
    dates,rockets,org,docs,other = seperate_tasks(sorted(tasks, key=lambda task: task.startDate))

    mermaid = generate_mermaid(dates,rockets,org,docs,other)
    #get_graph(graph_id)
    update_graph(graph_id,mermaid)
    f = open("mermaidCode.txt", "w")
    f.write(mermaid)
    f.close()

try:
    main(sys.argv[1])
except:
    main(os.getenv("PAGE_ID"))
