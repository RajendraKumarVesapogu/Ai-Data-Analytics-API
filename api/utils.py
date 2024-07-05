import requests
from .models import GameData
import pandas as pd
from io import StringIO
def toDateField(date):
    
    month_map = {'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'}
    
    if date == '':
        return None
    else:
        try: 
            split_date = date.replace(',', '').split(' ')     
            return split_date[2] + '-' + month_map[split_date[0]] + '-' + split_date[1]
        except Exception as e:
            return split_date[1] + '-' + month_map[split_date[0]] + '-' +"01"
def getCsvFromUrl(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None
    
def saveToDatabase(url):
    
    csvdata = getCsvFromUrl(url)
    
    data = pd.read_csv(StringIO(csvdata))
    
    column_mapping = {
        'AppID': 'AppID',
        'Name': 'Name',
        'Release date': 'Release_date',
        'Required age': 'Required_age',
        'Price': 'Price',
        'DLC count': 'DLC_count',
        'About the game': 'About_the_game',
        'Supported languages': 'Supported_languages',
        'Windows': 'Windows',
        'Mac': 'Mac',
        'Linux': 'Linux',
        'Positive': 'Positive',
        'Negative': 'Negative',
        'Score rank': 'Score_rank',
        'Developers': 'Developers',
        'Publishers': 'Publishers',
        'Categories': 'Categories',
        'Genres': 'Genres',
        'Tags': 'Tags'
    }
    data.rename(columns=column_mapping, inplace=True)
    GameData.objects.all().delete()
    try:
        for index, row in data.iterrows():
            game_data = GameData(
                AppID=row['AppID'],
                Name=row['Name'],
                Release_date=toDateField(row['Release_date']),
                Required_age=row['Required_age'],
                Price=row['Price'],
                DLC_count=row['DLC_count'],
                About_the_game=row['About_the_game'],
                Supported_languages=row['Supported_languages'],
                Windows=row['Windows'],
                Mac=row['Mac'],
                Linux=row['Linux'],
                Positive=row['Positive'],
                Negative=row['Negative'],
                Score_rank=row['Score_rank'],
                Developers=row['Developers'],
                Publishers=row['Publishers'],
                Categories=row['Categories'],
                Genres=row['Genres'],
                Tags=row['Tags'],
            )
            game_data.save()
        return "Success"
    except Exception as e:
        return e