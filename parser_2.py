import requests, re, json
from bs4 import BeautifulSoup
import xlsxwriter


OUT_FILENAME = 'out2.json'
OUT_XLSX_FILENAME = 'from_soccer365.xlsx'
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
            ws.write_string(xwsw, 0, item['Страна'])
            ws.write_string(xwsw, 1, item['Стадион'])
            ws.write_string(xwsw, 2, item['Язык'])
            ws.write_string(xwsw, 3, item['Лига'])
            ws.write_string(xwsw, 4, item['Город'])
            ws.write_string(xwsw, 5, item['Вместимость'])
            ws.write_string(xwsw, 6, item['Год открытия'])
            ws.write_string(xwsw, 7, item['Команды'])
            xwsw = xwsw+1



def get_soup(url, **kwargs):
    response = requests.get(url, **kwargs)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, features='html.parser')
    else:
        soup = None
    return soup

source = 'https://soccer365.ru/competitions/' #Стартовая страница
soup = get_soup(source)

stadiumss = []


season_items = soup.find('div', class_='season_items') # Блок с лигами
leagues = season_items.find_all('div', class_='season_item') 
for _, l_item in zip(range(1), leagues):
#for l_item in leagues:
    l_arr_a = l_item.find_all('a')
    for a_l in l_arr_a:
        url = a_l.get('href')
        if 'competitions' in url:
            print('Ссылка на лигу - ' + url)
            soup1 = get_soup('https://soccer365.ru' + url)
            l_name = soup1.find('h1', class_='profile_info_title red').text
            print(l_name)
            soup2 = get_soup('https://soccer365.ru' + url + 'stadiums/')
            stads_table = soup2.find('table', id = 'stadiums')
            s_arr_a = stads_table.find_all('a')
            for a_s in s_arr_a:
                surl = a_s.get('href')
                if 'stadiums' in surl:
                    s_source = ('https://soccer365.ru' + surl)
                    print(s_source)
                    soup3 = get_soup(s_source)
                    s_name = soup3.find('h1', class_='profile_info_title red').text
                    print(s_name)
                    param_table = soup3.find('table', class_='profile_params')
                    tds = param_table.find_all('td')
                    keys = []
                    values = []
                    for idv, valtd in enumerate(tds):
                        if valtd.get('class'):                        
                            keys.append(valtd.text)
                            keys.append('Стадион')
                            keys.append('Язык')
                            keys.append('Лига')
                            valx = tds[idv+1].text
                            valx = re.sub("^\s+|\n|\r|\t|\xa0|\s+$", '', valx)     
                            valx = valx.replace("|", ", ")              
                            values.append(valx)
                            values.append(s_name)
                            values.append(jsonObject[values[0]])
                            values.append(l_name)
                            if not 'Вместимость' in keys:
                                keys.append('Вместимость')
                                values.append('None')
                            if not 'Год открытия' in keys:
                                keys.append('Год открытия')
                                values.append('None')
                            if not 'Размеры поля' in keys:
                                keys.append('Размеры поля')
                                values.append('None')
                            if not 'Команды' in keys:
                                keys.append('Команды')
                                values.append('None')                         
                    if keys and values:
                        xsw = dict(zip(keys, values))
                        del xsw['Погода']
                        stadiumss.append(xsw)
                            
dump_to_json(OUT_FILENAME, stadiumss) 
dump_to_xlsx(OUT_XLSX_FILENAME, stadiumss)  


