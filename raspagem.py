#!/usr/bin/env python
# coding: utf-8

# In[3]:


import os
import mechanize
from bs4 import BeautifulSoup
import pandas as pd
from time import time
from time import sleep
from random import randint


# In[4]:


url = 'https://www.cbf.com.br/futebol-brasileiro/competicoes/campeonato-brasileiro-serie-a'
DATASET_FOLDER  = 'dataset'
br = mechanize.Browser()
br.addheaders = [('User-agent', 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_6_8) AppleWebKit/535.7 (KHTML, like Gecko) Chrome/16.0.912.63 Safari/535.7')]


# In[5]:


#Retorna um DataFrame Pandas com as estatísticas dos jogadores de determinado jogo
def get_estatisticas_por_jogo(num_jogo):
    
    br.open(url + "/2019/" + str(num_jogo))
    resp = br.response().read()
    soup = BeautifulSoup(resp, "html.parser")
    
    jogador = []
    num_camisa = []
    time = []
    mandante = []
    titular = []
    foi_substituido = []
    entrou_no_jogo = []
    cartao_amarelo = []
    cartao_vermelho = []
    gol = []
    vitoria = []
    derrota = []
    empate = []

    tab_escalacao = soup.find(class_="jogo-escalacao")

    time_mandante = tab_escalacao.findAll('div', class_="text-center")[0].find("span").text
    time_visitante = tab_escalacao.findAll('div', class_="text-center")[1].find("span").text

    tab_titulares = tab_escalacao.findAll('div', class_="row")[1].findAll('div', class_="col-xs-6")
    tab_reservas = tab_escalacao.findAll('div', class_="row")[3].findAll('div', class_="col-xs-6")

    count = -1
    for x in tab_titulares:

        count +=1

        li = x.findAll('li')

        for t in li:

            tmp_str = ''
            qtd_cartao_ama = 0
            qtd_cartao_ver = 0
            qtd_gols = 0

            if count == 0:
                tmp_str += 'Mandante,\t' + time_mandante + ',\t'
                mandante.append(1)
                time.append(time_mandante)
            else:
                tmp_str += 'Visitante,\t' + time_visitante + ',\t'
                mandante.append(0)
                time.append(time_visitante)

            if t.find("i", class_="icon pull-right") is None:
                tmp_str += 'Titular,\tEntrou,\t'
                titular.append(1)
                entrou_no_jogo.append(1)
                foi_substituido.append(0)
            else:
                tmp_sub = t.find("i", class_="icon pull-right").find('path')['fill']

                if tmp_sub == '#FA1200':
                    tmp_str += 'Titular,\tSubst.,\t'
                    titular.append(1)
                    entrou_no_jogo.append(1)
                    foi_substituido.append(1)
                else: 
                    if tmp_sub == '#399C00':
                        tmp_str += 'Reserva,\tEntrou,\t'
                        titular.append(0)
                        entrou_no_jogo.append(1)
                        foi_substituido.append(0)

            if t.find('strong').find("i", class_="icon small icon-yellow-card") is not None:
                qtd_cartao_ama = len(t.find('strong').findAll("i", class_="icon small icon-yellow-card"))

            if t.find('strong').find("i", class_="icon small icon-red-card") is not None:
                qtd_cartao_ver = len(t.find('strong').findAll("i", class_="icon small icon-red-card"))

            if t.find('strong').find("i", class_="icon small") is not None:
                qtd_gols = len(t.find('strong').findAll("i", class_="icon small"))



            tmp_str +=  t.find('span').text.strip() + " " + t.find('strong').text.strip()

            tmp_str += ',\t\t' + str(qtd_cartao_ama) + ',\t' + str(qtd_cartao_ver)

            tmp_str = str(qtd_gols) + ',\t' + tmp_str

            # print(tmp_str)

            jogador.append(t.find('strong').text.strip())
            num_camisa.append(t.find('span').text.strip())

            cartao_amarelo.append(qtd_cartao_ama)
            cartao_vermelho.append(qtd_cartao_ver)
            gol.append(qtd_gols)


    count = -1
    for x in tab_reservas:

        count +=1

        li = x.findAll('li')

        for t in li:

            tmp_str = ''
            qtd_cartao_ama = 0
            qtd_cartao_ver = 0
            qtd_gols = 0

            if count == 0:
                tmp_str += 'Mandante,\t' + time_mandante + ',\t'
                mandante.append(1)
                time.append(time_mandante)
            else:
                tmp_str += 'Visitante,\t' + time_visitante + ',\t'
                mandante.append(0)
                time.append(time_visitante)

            titular.append(0)
            entrou_no_jogo.append(0)
            foi_substituido.append(0)


            jogador.append(t.find('strong').text.strip())
            num_camisa.append(t.find('span').text.strip())

            cartao_amarelo.append(0)
            cartao_vermelho.append(0)
            gol.append(0)


    #junta tudo

    df_jogo = pd.DataFrame({'jogo' : num_jogo,
                            'jogador' : jogador,
                            'num_camisa' : num_camisa,
                            'time' : time,
                            'mandante' : mandante,
                            'titular' : titular,
                            'foi_substituido' : foi_substituido,
                            'entrou_no_jogo' : entrou_no_jogo,
                            'cartao_amarelo' : cartao_amarelo,
                            'cartao_vermelho' : cartao_vermelho,
                            'gol' : gol,
                            'vitoria': 0,
                            'empate': 0
                          })


    gol_mandante = df_jogo[df_jogo['mandante'] == 1].sum()['gol']
    gol_visitante = df_jogo[df_jogo['mandante'] == 0].sum()['gol']
    empate = int(gol_mandante == gol_visitante)
    vitoria_mandante = int(gol_mandante > gol_visitante)
    vitoria_visitante = int(gol_mandante < gol_visitante)

    df_jogo['vitoria'] = df_jogo['mandante'].map(lambda x: vitoria_mandante if x ==1 else vitoria_visitante)
    df_jogo['empate'] = empate
    
    return df_jogo


# In[6]:


#Retorna um dataframa pandas com a atual artilharia do campeonato
def get_artilharia():
    
    br.open(url + "/2019")
    resp = br.response().read()
    soup = BeautifulSoup(resp, "html.parser")

    colocacao = []
    time = []
    jogador = []
    num_gol = []

    rows = soup.find(class_="box-jogador").find('table').find('tbody').findAll('tr')

    col = 0
    for tr in rows:
        col += 1

        tds = tr.findAll('td')

        if tds[0].find('img') is None:
            break

        tmp_time = tds[0].find('img').get('title')
        tmp_jogador =  tds[2].text
        
        tmp_gol = tr.find('th').text
        
        colocacao.append(col)
        time.append(tmp_time)
        jogador.append(tmp_jogador)
        num_gol.append(tmp_gol)



    df = pd.DataFrame({'colocacao' : colocacao,
                        'time' : time,
                        'jogador' : jogador,
                        'gols' : num_gol
                      })

    return df


# In[24]:


#Retorna um array com todos os jogos já realizados
def get_jogos_realizados():
    
    jogos_realizados = []
    
    br.open(url + "/2019")
    resp = br.response().read()
    soup = BeautifulSoup(resp, "html.parser")
    
    rodadas = soup.find('aside', class_="aside-rodadas").find('div').findAll('div', class_="swiper-slide")
    
    for r in rodadas:
        
        lis = r.findAll('li')
        
        for li in lis:
            
            link = li.find('div').findAll('span', class_="partida-desc")[-1].find('a', class_="btn-success")
            
            #Se o jogo não tiver acontecido, continua
            if link is None:
                continue
            
            href = link.get('href')
            
            inf = href.rfind('/')
            sup = href.rfind('?')
            
            num_jogo = int(href[inf+1:sup])
            
            jogos_realizados.append(num_jogo)
            
    return jogos_realizados


# In[8]:


def get_jogos_raspados():
    
    lista = os.listdir(DATASET_FOLDER)
    lista = [int(x[5:7]) for x in lista if x.find('jogo') >= 0]
    
    return lista


# In[9]:


def get_jogos_para_raspar():
    realizados = get_jogos_realizados()
    raspados = get_jogos_raspados()
    return list(set(realizados) - set(raspados))


# In[30]:


def raspar(max_jogos = -1):
    
    #Controles de quantidade de requisição
    inicio = time()
    #sleep(randint(5,60))
    espera = time() - inicio
    
    print('Request: ' + 'Artilharia, espera: ' + str(espera) )
    df_artilharia = get_artilharia()
    df_artilharia.to_csv(DATASET_FOLDER + '/artilharia.csv', index = False)
    
    #Controles de quantidade de requisição
    inicio = time()
    sleep(randint(5,30))
    espera = time() - inicio
    
    print('Request: ' + 'Jogos para raspar, espera: ' + str(espera) )
    lista_jogos = get_jogos_para_raspar()
    
    if len(lista_jogos) == 0:
        print("Nenhum novo jogo para ser raspado.")
    
    count = 0
    
    for j in lista_jogos:
            
        if max_jogos > 0 and count >= max_jogos:
            return
        
        count += 1
        
        #Controles de quantidade de requisição
        inicio = time()
        sleep(randint(5,60))
        espera = time() - inicio
        
        print('Request: ' + 'Jogo ' + str(j) + ', espera: ' + str(espera) )
        
        jogo = get_estatisticas_por_jogo(j)
        
        jogo.to_csv(DATASET_FOLDER + '/jogo_' + str(j).rjust(2,'0') + '.csv', index=False)
        
    print("Raspagem finalizada.")


# In[31]:


#Faz a raspagem das estatísticas dos jogos por jogador
raspar()

