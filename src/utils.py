import re
from datetime import datetime
import os
import ndjson
from typing import List, Union, Dict

def strip_for_html(text: str) -> str:
    """Strips html tags from text

    Args:
        text (str): text to strip

    Returns:
        str: stripped text
    """    
    html_expression = re.compile(r"<[^>]+>")
    return html_expression.sub("", text)

def ignore_article(article: dict) -> bool:
    """Checks if article should be ignored because it is a note or a frontpage reference

    Args:
        article (dict): article to check

    Returns:
        bool: True if article should be ignored
    """    
    if "Forsidehenvisning" in article["Heading"]:
        return True
    if "Note" in article["Heading"]:
        return True
    return False

def add_text_column(article:dict) -> dict:
    """Adds text column to article containing heading, subheading and bodytext

    Args:
        article (dict): article to add text column to

    Returns:
        article (dict): article with text column
    """    
    article["text"] = ""
    if article["Heading"].strip(" "):
        article["text"] = article["Heading"]
    if article["SubHeading"].strip(" "):
        article["text"] += f'\n {article["SubHeading"]}'
    if article["BodyText"].strip(" "):
        article["text"] += f'\n\n {strip_for_html(article["BodyText"])}'
    return article

def get_date(date: str) -> str:
    """Converts date to clean format with no time

    Args:
        date (str): date to convert

    Returns:
        str: clean date as string
    """    
    try:
        datetime_obj = datetime.strptime(date, "%Y-%m-%dT%H:%M:%SZ") # '2020-06-02T00:00:00Z'
    except:
        print("Unknow date format:", date)
    return datetime_obj.date().strftime("%d-%m-%Y")

def add_clean_date(article: dict) -> dict:
    """ Adds clean date to article

    Args:
        article (dict): article to add clean date to

    Returns:
        article (dict): article with clean date field
    """    
    article["clean_date"] = get_date(article["PublishDate"])
    return article


def subset_folders(path:str, type:str):
    """Yields folders with specific type

    Args:
        path (str): path to where subfolders are located
        type (str): type of folder to yield. Takes values "print" or "web"

    Yields:
        str: path to subfolder if it has the correct type
    """    
    for folder in os.listdir(path):
        if folder.endswith(type):
            yield os.path.join(path, folder)


def load_ndjson(path:str) -> dict:
    """Loads ndjson file

    Args:
        path (str): path to ndjson file

    Returns:
        data (dict): data from ndjson file
    """    
    with open(path, "r") as f:
        data = ndjson.load(f)
    return data

def write_ndjson(path:str, data:Union[List, Dict], method:str="a"):
    """Writes data to ndjson file

    Args:
        path (str): path to ndjson file
        data (Union[List, Dict]): data to write to file. Must be in ndjson format
        method (str, optional): method to use when writing data. Defaults to "a" (i.e., append).
    
    Returns:
        None
    """
    with open(path, method) as f:
        ndjson.dump(data, f)

def get_date_from_filename(file_name:str):
    """Gets date from file name

    Args:
        file_name (str): file name to get date from

    Returns:
        str: the date of the given file
    """    
    date = re.sub(r'\D',"", file_name)[:8] # TODO: make more robust/better regex
    datetime_obj = datetime.strptime(date, "%Y%m%d") 
    return datetime_obj.date().strftime("%d-%m-%Y")

def get_day_of_week(file_name:str):
    """Gets day of week from file name

    Args:
        file_name (str): file name to get day of week from

    Returns:
        str: the weekday of the given file
    """    
    weekday_dict = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday"
    }
    date = re.sub(r'\D',"", file_name)[:8]
    datetime_obj = datetime.strptime(date, "%Y%m%d") 
    day_of_week = datetime_obj.weekday()
    return weekday_dict[day_of_week]

def get_paper_from_filename(file_name:str):
    """Gets paper name from file name

    Args:
        file_name (str): file name to get paper name from

    Returns:
        str: the paper name of the given file
    """    
    paper = "".join([i for i in file_name if not i.isdigit()]).replace(".ndjson", "").replace("_--", "")
    return paper

def avg_articles_pr_day(out_path: str) -> Dict[str, float]:
    """Calculates average number of articles per day for each paper

    Args:
        out_path (str): path to where ndjson files are located

    Returns:
        Dict[str, float]: dictionary with paper as key and average number of articles per day as value
    """    
    articles = {
    'politiken-print':[],
    'ekstrabladet-print':[],
    'weekendavisen-print':[],
    'jyllands-posten-print':[],
    'kristeligt-dagblad-print':[],
    'berglinske-print':[],
    'information-print':[],
    'bt-print':[]}
    for file in os.listdir(out_path):
        paper = get_paper_from_filename(file)
        data = load_ndjson(os.path.join(out_path, file))
        articles[paper].append(len(data))
    n_articles = {paper:{
        "daily_article_average":sum(list_n)/len(list_n),
        "total_articles":sum(list_n),
        "total_days":len(list_n)
     } for paper, list_n in articles.items()}
    return n_articles
    