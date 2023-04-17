from utils import *
import os
from datetime import datetime

def clean_article(article:dict):
    article = add_text_column(article)
    article = add_clean_date(article)
    return {
        "Heading": article["Heading"],
        "SubHeading": article["SubHeading"],
        "BodyText": article["BodyText"],
        "text": article["text"], 
        "clean_date": article["clean_date"],
        "full_text": "\n".join([article["Heading"], article["SubHeading"], article["text"]])}

date_ranges = {
    "2019_election_announcement": [("07-05-2019", "09-05-2019")], # Election announcement
    "2019_election_campagin":     [("29-05-2019", "06-06-2019")], # Election campaign + day
    "2019_election_government": [("25-06-2019", "27-06-2019")],  # Government formation

    "mink_start": [
        ("04-11-2020", "12-11-2020") 
    ],
    "mink_mogens_jensen": [
        ("17-11-2020", "19-11-2020")
        ],
    "covid_week_1": [
        ("10-03-2020", "17-03-2020"), # First lockdown
    ],
    "covid_week_2": [
        ("18-03-2020", "25-03-2020"), # First lockdown
    ],
    # "nurse_strike": [
    #     ("12-06-2021", "26-06-2021"),
    #     ("23-08-2021", "30-08-2021")
    # ],
    # "defence_referendum" : [
    #     ("06-03-2022", "13-03-2022"), # Election announcement
    #     ("20-05-2022", "03-06-2022")  # Election campaign + day
    # ],
    # "2022_election": [
    #     ("05-10-2022", "07-10-2022"), # Election announcement
    #     ("18-10-2022", "02-11-2022"), # Election campaign + day
    #     ("12-12-2022", "14-12-2022")  # Government formation
    # ],
    # "test_event": [
    #     ("01-01-2020", "03-01-2020")
    # ]
}

def clean_and_save(file_path, out_path):
    articles = load_ndjson(file_path)
    # If there is any data in the file
    if len(articles) > 1:
        clean_day = [clean_article(article) for article in articles if not ignore_article(article)]
        paper_name = get_paper_from_filename(file_path.split("/")[-1])
        paper_date = get_date_from_filename(file_path.split("/")[-1])
        os.makedirs(out_path, exist_ok=True)
        # print(f'writing to {os.path.join(out_path, f"{paper_name}_{paper_date}.ndjson")}')
        write_ndjson(os.path.join(out_path, f"{paper_name}_{paper_date}.ndjson"), clean_day, "w")


def main(in_path:str, type:str, date_ranges:dict = date_ranges):
    """Cleans news articles and saves them to clean_news folder
    Skips dates with no articles

    Args:
        in_path (str): Path to where raw data is stored
        type (str): Which type of data to clean. Takes values "print" or "web"
    """ 
    out_path = os.path.join(
        "..",
        "data",
        "clean_news"
        )
    for folder in subset_folders(in_path, type):
        for file in os.listdir(folder):
            paper_date = datetime.strptime(get_date_from_filename(file), "%d-%m-%Y")
            for event, ranges in date_ranges.items():
                for start, end in ranges:
                    if datetime.strptime(start, "%d-%m-%Y") <= paper_date <= datetime.strptime(end, "%d-%m-%Y"):
                        clean_and_save(os.path.join(folder, file), os.path.join(out_path, event))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path", type=str, help="Path to dataset")
    parser.add_argument("-t", "--type", type=str, help="Type of dataset (print or web)", default ="print")
    args = parser.parse_args()

    main(args.path, args.type)