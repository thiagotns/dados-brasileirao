import os
import mechanize
from bs4 import BeautifulSoup
import pandas as pd
from time import time
from time import sleep
from random import randint


URL = 'https://www.cbf.com.br/futebol-brasileiro/competicoes/campeonato-brasileiro-serie-a/'
DATASET_FOLDER  = 'dataset'
br = mechanize.Browser()
br.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7')]


def get_stats_by_match(match_num, year = 2019):
    
    match_url = URL + str(year) + '/' +  str(match_num)

    br.open(match_url)
    resp = br.response().read()
    soup = BeautifulSoup(resp, "html.parser")
    
    player = []
    number = []
    team = []
    at_home = []
    starter = []
    substituted = []
    substitute = []
    yellow_card = []
    red_card = []
    goal = []
    win = []
    lose = []
    draw = []

    tab_starting_line = soup.find(class_="jogo-escalacao")

    team_at_home = tab_starting_line.findAll('div', class_="text-center")[0].find("span").text
    team_away = tab_starting_line.findAll('div', class_="text-center")[1].find("span").text

    tab_starters = tab_starting_line.findAll('div', class_="row")[1].findAll('div', class_="col-xs-6")
    tab_reserves = tab_starting_line.findAll('div', class_="row")[3].findAll('div', class_="col-xs-6")

    count = -1
    for x in tab_starters:

        count +=1

        li = x.findAll('li')

        for t in li:

            tmp_str = ''
            yellow_card_count = 0
            red_card_count = 0
            goals_count = 0

            if count == 0:
                tmp_str += 'at_home,\t' + team_at_home + ',\t'
                at_home.append(1)
                team.append(team_at_home)
            else:
                tmp_str += 'Away Team,\t' + team_away + ',\t'
                at_home.append(0)
                team.append(team_away)

            if t.find("i", class_="icon pull-right") is None:
                tmp_str += 'starter,\t'
                starter.append(1)
                substitute.append(1)
                substituted.append(0)
            else:
                tmp_sub = t.find("i", class_="icon pull-right").find('path')['fill']

                if tmp_sub == '#FA1200':
                    tmp_str += 'starter,\tSubst.,\t'
                    starter.append(1)
                    substitute.append(1)
                    substituted.append(1)
                else: 
                    if tmp_sub == '#399C00':
                        tmp_str += 'Reserve,\t'
                        starter.append(0)
                        substitute.append(1)
                        substituted.append(0)

            if t.find('strong').find("i", class_="icon small icon-yellow-card") is not None:
                yellow_card_count = len(t.find('strong').findAll("i", class_="icon small icon-yellow-card"))

            if t.find('strong').find("i", class_="icon small icon-red-card") is not None:
                red_card_count = len(t.find('strong').findAll("i", class_="icon small icon-red-card"))

            if t.find('strong').find("i", class_="icon small") is not None:
                goals_count = len(t.find('strong').findAll("i", class_="icon small"))



            tmp_str +=  t.find('span').text.strip() + " " + t.find('strong').text.strip()

            tmp_str += ',\t\t' + str(yellow_card_count) + ',\t' + str(red_card_count)

            tmp_str = str(goals_count) + ',\t' + tmp_str

            print(tmp_str)

            player.append(t.find('strong').text.strip())
            number.append(t.find('span').text.strip())

            yellow_card.append(yellow_card_count)
            red_card.append(red_card_count)
            goal.append(goals_count)


    count = -1
    for x in tab_reserves:

        count +=1

        li = x.findAll('li')

        for t in li:

            tmp_str = ''
            yellow_card_count = 0
            red_card_count = 0
            goals_count = 0

            if count == 0:
                tmp_str += 'at_home,\t' + team_at_home + ',\t'
                at_home.append(1)
                team.append(team_at_home)
            else:
                tmp_str += 'Away Team,\t' + team_away + ',\t'
                at_home.append(0)
                team.append(team_away)

            starter.append(0)
            substitute.append(0)
            substituted.append(0)


            player.append(t.find('strong').text.strip())
            number.append(t.find('span').text.strip())

            yellow_card.append(0)
            red_card.append(0)
            goal.append(0)


    df_match = pd.DataFrame({'jogo' : match_num,
                            'player' : player,
                            'number' : number,
                            'team' : team,
                            'at_home' : at_home,
                            'starter' : starter,
                            'substituted' : substituted,
                            'substitute' : substitute,
                            'yellow_card' : yellow_card,
                            'red_card' : red_card,
                            'goal' : goal,
                            'win': 0,
                            'draw': 0
                          })


    goal_at_home = df_match[df_match['at_home'] == 1].sum()['goal']
    goal_visitante = df_match[df_match['at_home'] == 0].sum()['goal']
    draw = int(goal_at_home == goal_visitante)
    win_at_home = int(goal_at_home > goal_visitante)
    win_visitante = int(goal_at_home < goal_visitante)

    df_match['win'] = df_match['at_home'].map(lambda x: win_at_home if x ==1 else win_visitante)
    df_match['draw'] = draw
    
    return df_match


def get_matches(year = 2019):
    
    matches = []
    
    matches_url = URL + str(year)

    br.open(matches_url)
    resp = br.response().read()
    soup = BeautifulSoup(resp, "html.parser")
    
    rounds = soup.find('aside', class_="aside-rodadas").find('div').findAll('div', class_="swiper-slide")
    
    for r in rounds:
        
        lis = r.findAll('li')
        
        for li in lis:
            
            link = li.find('div').findAll('span', class_="partida-desc")[-1].find('a', class_="btn-success")
            
            #Continue if the match does not occurred yet
            if link is None:
                continue
            
            href = link.get('href')
            
            inf = href.rfind('/')
            sup = href.rfind('?')
            
            match_num = int(href[inf+1:sup])
            
            matches.append(match_num)
            
    return matches


def get_downloaded_matches():
    # Return the list of match ids already downloaded

    file_list = os.listdir(DATASET_FOLDER)
    file_list = [int(x[6:8]) for x in file_list if x.find('match') >= 0]

    return file_list


print(get_downloaded_matches())