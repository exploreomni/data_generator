#to be run independently of the framework
import requests
from pydash import get
import json, csv
from dotenv import load_dotenv
load_dotenv()
import os
imdb_ids = [
    'tt14269590', 'tt18335752', 'tt13406094', 'tt4236770'
]

for imdb_id in imdb_ids:
    url = "https://online-movie-database.p.rapidapi.com/title/get-videos"

    querystring = {"tconst":imdb_id,"limit":"5000","region":"US"}

    headers = {
        "X-RapidAPI-Key": os.environ['IMDB_PROXY_API_KEY'],
        "X-RapidAPI-Host": "online-movie-database.p.rapidapi.com"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)


    data = json.loads(response.text)

    new_data = []

    for film in get(data, 'resource.videos'):
        video = dict(
            title = get(film, 'title'),
            id = get(film, 'id').split('/')[2],
            duration = get(film, 'durationInSeconds'),
            content_type = get(film, 'contentType'),
            description = get(film, 'description'),
            audio_language = get(film, 'audioLanguage'),
            image_url = get(film, 'image.url'),
            parenttitle_year = get(film, 'parentTitle.year'),
            parenttitle_title = get(film, 'parentTitle.title'),
        )
        new_data.append(video)

    with open('lib/data/movies.csv', 'a') as f:
        writer = csv.DictWriter(f, fieldnames=video.keys())
        writer.writerows(new_data)
