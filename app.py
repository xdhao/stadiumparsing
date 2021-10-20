import requests, re, json
from bs4 import BeautifulSoup

OUT_FILENAME = 'out.json'

def dump_to_json(filename, data, **kwargs):
    kwargs.setdefault('ensure_ascii', False)
    kwargs.setdefault('indent', 1)

    with open(OUT_FILENAME, 'w') as f:
        json.dump(data, f, **kwargs)


def get_soup(url, **kwargs):
    response = requests.get(url, **kwargs)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, features='html.parser')
    else:
        soup = None
    return soup

source = 'http://wildstat.ru/p/2' #Стартовая страница(по умолчанию выбрана Россия)
soup = get_soup(source)
c_items = []


country_links = []
league_links = []
team_links = []
stadium_links = []
xc = 0
xl = 0
xt = 0
xs = 0


countries = soup.find_all('div', class_='dmn-left-g') # Страны в блоках div
for div_countries in countries:
    for a_countries in div_countries:
        href_countries = a_countries.get('href')
        c_url = "http://wildstat.ru" + href_countries 
        country_links.append(c_url) # массив ссылок на страницы полного списка лиг отдельных стран
        print("\tSTRANA:"+str(xc)+c_url)
        xc = xc+1 

        #for smn_country in country_links:
        soup1 = get_soup(c_url)
        leagues = soup1.find_all('div', class_='smn-left-g')
        l_items = []
        for div_leagues in leagues:
            for a_leagues in div_leagues:
                href_leagues = a_leagues.get('href')
                l_url = "http://wildstat.ru" + href_leagues 
                league_links.append(l_url)
                print("\tLIGA:"+str(xl)+l_url)
                xl = xl+1 
                   
                #for smn_league in league_links:
                soup2 = get_soup(l_url)
                div_table = soup2.find('div', class_='content-rb')
                teams = div_table.find_all('a')
                t_items = []
                for a_teams in teams:
                    href_teams = a_teams.get('href')
                    if '/club/' in href_teams:
                        t_url = "http://wildstat.ru" + href_teams                             
                        team_links.append(t_url)
                        print("\tteam:"+str(xt)+t_url)
                        xt = xt+1

                        soup3 = get_soup(t_url)
                        stadiums = soup3.find_all('a')
                        s_items = []
                        for a_stadiums in stadiums:
                            href_stadiums = a_stadiums.get('href')
                            if '/map_stadium/' in href_stadiums:
                                s_url = "http://wildstat.ru" + href_stadiums
                                stadium_links.append(s_url)
                                print("\tStadium:"+str(xs)+s_url)
                                xs = xs+1 

                                s_item ={
                                    's_url': s_url,
                                }
                                s_items.append(s_item)


                        t_item = {
                            't_url': t_url,
                            'stadiums': s_items,
                        }    
                        t_items.append(t_item)               
                l_item = {
                    'l_url': l_url,
                    'teams': t_items,
                }
                l_items.append(l_item)
        c_item = {
            'c_url': c_url,
            'leagues': l_items, 
        }
        c_items.append(c_item)                                        
                                            
item = {
    'countries': c_items,
    }
dump_to_json(OUT_FILENAME, item)   


  
'''

tTable = soup.find('div', class_='content-rb')
links = tTable.find_all('a')
for link in links:
    tag = link.get('href')
    if '/club/' in tag:
        url = "http://wildstat.ru/p/2001" + tag #2 ссылка
        print(url) 
    

head = mainPage.find_all('a', class_='detail-link-text')
startLink = head[0].get('href') # news/'id'.html
splitArrayOne = startLink.split('/') # 'id'.html
splitArrayTwo =  splitArrayOne[2].split('.') # 'id'
startID = splitArrayTwo[0]


for i in range(0, 40):
    
    url = "https://v102.ru/news/" + str(int(startID) - i) + ".html"#2 ссылка
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    bigline = soup.find('div', class_='short-text')
    headline = soup.find('div', class_='col-lg-11')
    newsTimes = soup.find('span', class_='date-new')
    
    headline = headline.text #` заголовок
    newsLine = bigline.text
    newsLine =  re.sub("^\s+|\n|\r|\s+$", '', newsLine) #3 текст новости
    newsTime = newsTimes.text #4   дата
    if newsTime:
        s1="".join(c for c in newsTime if c.isalpha()==False)
        newsTime = s1
    news_ = {
    "headline":headline,
    "text":newsLine,
    "url":url,
    "time":newsTime
    }
    if news.find_one({'headline': headline}) is None:
        if news.find_one({'url': url}) is None:
            if news.find_one({'time': newsTime}) is None:
                news.insert_one(news_)
                print('added entry to the database', i, url )
    else:
        print('entry already exists', i, url )
'''  