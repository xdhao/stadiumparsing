import requests, re, json
from bs4 import BeautifulSoup
import xlsxwriter


OUT_FILENAME = 'out.json'
OUT_XLSX_FILENAME = 'out.xlsx'
f = open( "Страны и языки.json" , "rb" )
jsonObject = json.load(f)
f.close()

def dump_to_json(filename, data, **kwargs):
    kwargs.setdefault('ensure_ascii', False)
    kwargs.setdefault('indent', 1)

    with open(OUT_FILENAME, 'w', encoding='utf-8') as f:
        json.dump(data, f, **kwargs)

def dump_to_xlsx(filename, data):
    if not len(data):
        return None
    
    with xlsxwriter.Workbook(filename) as workbook:
        ws = workbook.add_worksheet()
        bold = workbook.add_format({'bold': True})

        headers = ['Страна', 'Язык', 'Город', 'Команда', 'Лига', 'Стадион', 'Вместимость', 'Открытие']

        for col, h in enumerate(headers):
            ws.write_string(0, col, h, cell_format=bold)
        
        xwsw = 1
        for item in data:
            for val in item['leagues']:
                for vl in val['teams']:
                    for lv in vl['stadiums']:
                        ws.write_string(xwsw, 0, lv['country_stad'])
                        ws.write_string(xwsw, 1, lv['language'])
                        ws.write_string(xwsw, 2, lv['stad_city'])
                        ws.write_string(xwsw, 3, vl['club_name'])
                        ws.write_string(xwsw, 4, val['league_name'])
                        ws.write_string(xwsw, 5, lv['namestad'])
                        ws.write_string(xwsw, 6, lv['spect_count'])
                        ws.write_string(xwsw, 7, lv['stad_open'])
                        xwsw = xwsw+1



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
#for _, div_countries in zip(range(2), countries):
for div_countries in countries:
    for a_countries in div_countries:
        href_countries = a_countries.get('href')
        c_url = "http://wildstat.ru" + href_countries 
        country_links.append(c_url) 
        print("\tSTRANA:"+str(xc)+c_url)
        xc = xc+1 

        soup1 = get_soup(c_url)
        leagues = soup1.find_all('div', class_='smn-left-g')
        l_items = []
        #for _, div_leagues in zip(range(2), leagues):
        for div_leagues in leagues:
            for a_leagues in div_leagues:
                href_leagues = a_leagues.get('href')
                l_url = "http://wildstat.ru" + href_leagues 
                league_links.append(l_url)
                print("\tLIGA:"+str(xl)+l_url)
                xl = xl+1 
                   
                soup2 = get_soup(l_url)
                league_name = soup2.find('h1').text
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
                        club_name = soup3.find('h1').text + ' ' + soup3.find('h2').text
                        div_stadium = soup3.find('div', id='middle_col')
                        p_s  = div_stadium.find_all('p')
                        for idx, p_st in enumerate(p_s):                        
                            if p_st.find('b'):
                                b_text = p_st.find('b').text
                                if 'Стадион:' in b_text:
                                    stadiums = p_s[idx].find('a')
                                    s_items = []
                                    if stadiums:
                                        href_stadiums = stadiums.get('href')
                                        if '/map_stadium/' in href_stadiums:
                                            s_url = "http://wildstat.ru" + href_stadiums
                                            stadium_links.append(s_url)
                                            print("\tStadium:"+str(xs)+s_url)
                                            xs = xs+1

                                            soup4 = get_soup(s_url)
                                            stad_table = soup4.find('table')
                                            s_td = stad_table.find_all('td')
                                            for td in s_td:              
                                                if td.find('h1'):
                                                    namestad = td.find('h1').text                                              
                                                if td.find('h2'):
                                                    geoloc = td.find('h2').text.split(",")
                                                    country_stad = geoloc[0]
                                                    stad_city = geoloc[1]
                                                if td.find('b'):
                                                    barr = td.find_all('b')
                                                    stad_open = barr[0].text
                                                    if len(barr) > 1 :
                                                        spect_count = barr[1].text
                                            if namestad and country_stad and stad_city:
                                                if stad_open and spect_count:
                                                    s_item ={
                                                        's_url': s_url,
                                                        'namestad': namestad,
                                                        'country_stad': country_stad,
                                                        'stad_city': stad_city,
                                                        'language': jsonObject[country_stad],
                                                        'stad_open': stad_open, 
                                                        'spect_count': spect_count,
                                                    }
                                                else:
                                                    s_item ={
                                                        's_url': s_url,
                                                        'namestad': namestad,
                                                        'country_stad': country_stad,
                                                        'stad_city': stad_city,
                                                        'language': jsonObject[country_stad],
                                                        'stad_open': ' ', 
                                                        'spect_count': ' ',
                                                    }                                                    
                                                s_items.append(s_item)
                                            namestad = ' '
                                            country_stad = ' '
                                            stad_city = ' '
                                            stad_open = ' '
                                            spect_count = ' '
                        t_item = {
                            't_url': t_url,
                            'stadiums': s_items,
                            'club_name': club_name,
                        }    
                        t_items.append(t_item)               
                l_item = {
                    'l_url': l_url,
                    'teams': t_items,
                    'league_name': league_name,
                }
                l_items.append(l_item)
        c_item = {
            'c_url': c_url,
            'leagues': l_items, 
        }
        c_items.append(c_item)                                        

'''                                           
item = {
    'countries': c_items,
    }
dump_to_json(OUT_FILENAME, item) 
'''

dump_to_xlsx(OUT_XLSX_FILENAME, c_items)  


