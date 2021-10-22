import requests, re, json
from bs4 import BeautifulSoup
import xlsxwriter
import urllib3


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
#requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


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

        headers = ['Страна', 'Стадион', 'Язык', 'Лига', 'Город', 'Вместимость', 'Год открытия', 'Размеры поля', 'Команды', 'Бюджет команды']
        
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
            ws.write_string(xwsw, 7, item['Размеры поля'])
            ws.write_string(xwsw, 8, item['Команды'])
            ws.write_string(xwsw, 9, item['Бюджет команды'])
            xwsw = xwsw+1



def get_soup(url, **kwargs):
    response = requests.get(url, **kwargs)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, features='html.parser')
    else:
        soup = None
    return soup


def crawl_stadiums(pages_count):

    stadiumss = []
    fmt = 'https://soccer365.ru/index.php?c=competitions&a=champs_list_data&tp=0&cn_id=0&st=0&ttl=&p={page}'
    
    for page_n in range(1, 1 + pages_count):
        print('page: {}'.format(page_n))

        page_url = fmt.format(page=page_n)
        soup = get_soup(page_url)
        
        season_items = soup.find('div', class_='season_items') # Блок с лигами
        leagues = season_items.find_all('div', class_='season_item') 
        #for _, l_item in zip(range(2), leagues):
        for l_item in leagues:
            l_arr_a = l_item.find_all('a')
            for a_l in l_arr_a:
                url = a_l.get('href')
                if 'competitions' in url:
                    print('Ссылка на лигу - ' + url)
                    soup1 = get_soup('https://soccer365.ru' + url)
                    l_name = soup1.find('h1', class_='profile_info_title red').text
                    print(l_name)
                    soup2 = get_soup('https://soccer365.ru' + url + 'stadiums/')
                    if soup2:
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
                                        if values[0] in jsonObject.keys():
                                            values.append(jsonObject[values[0]])
                                        else: 
                                            values.append('None')
                                        values.append(l_name)
                                        availability = ['Страна', 'Город', 'Вместимость', 'Год открытия', 'Размеры поля', 'Команды']
                                        for check in availability:
                                            if not check in keys:
                                                keys.append(check)
                                                values.append('None')                       
                                if keys and values:
                                    xsw = dict(zip(keys, values))

                                    # БЮДЖЕТ КОМАНДЫ  #############################
                                    xsw['Бюджет команды'] = 'None'
                                    my_st = xsw['Команды'].split(",")
                                    budget_query = f"https://www.google.com/search?q=бюджет%20клуба%20{my_st[0]}"
                                    budget_query = budget_query.replace(' ', '%20')
                                    print(budget_query)
                                    try:
                                        headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:65.0) Gecko/20100101 Firefox/65.0"}
                                        requestspider = requests.get(budget_query, headers=headers, verify=False, timeout=3)                                  
                                        if requestspider.status_code == 200:
                                            soup4 = BeautifulSoup(requestspider.content, "html.parser")    
                                            if soup4.find('div', class_='iKJnec'):                         
                                                b_header = soup4.find('div', class_='iKJnec').text

                                                print(b_header)
                                                if '(футбольный клуб' in b_header:
                                                    bud_table = soup4.find('table')
                                                    bud_tds = bud_table.find_all('td')
                                                    for idb, bvaltd in enumerate(bud_tds):
                                                        if bvaltd.get('style') and bvaltd.text == 'Бюджет':
                                                            print(bud_tds[idb+1].text)
                                                            xsw['Бюджет команды'] = bud_tds[idb+1].text
                                                
                                                if 'Футбольные клубы с бюджетом свыше 100 млн долларов США' in b_header or 'Футбольные клубы с бюджетом от 70 до 100 млн долларов США' in b_header or 'Футбольные клубы с бюджетом от 50 до 70 млн долларов США':
                                                    bud_table = soup4.find('table')
                                                    bud_tds = bud_table.find_all('td')
                                                    for idb, bvaltd in enumerate(bud_tds):
                                                        if bvaltd.get('style') and (bvaltd.text in my_st[0] or my_st[0] in bvaltd.text):
                                                            print(bud_tds[idb+1].text)
                                                            xsw['Бюджет команды'] = bud_tds[idb+1].text + 'млн. $'                                    
                                    except requests.Timeout as err:
                                        pass                            
                                    ###############################################

                                    if 'Погода' in keys:
                                        del xsw['Погода']
                                    stadiumss.append(xsw)

    return stadiumss


#dump_to_json(OUT_FILENAME, stadiumss) 
dump_to_xlsx(OUT_XLSX_FILENAME, crawl_stadiums(5))  


