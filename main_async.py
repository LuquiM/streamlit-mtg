# Script para consulta em massa de cartas MTG nas lojas que gosto.
# Dev: Lucca Mariano
import random

# Imports ---------------------------------------------------------
import random
import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import asyncio
import aiohttp
import time
from aiolimiter import AsyncLimiter
import streamlit as st
from stqdm import stqdm
import json
from pathlib import Path
# Variables -------------------------------------------------------
store_dict = {'https://www.bazardebagda.com.br/': 'Bazar',
              'https://www.cardtutor.com.br/': 'Card Tutor',
              'https://www.chq.com.br/': 'CHQ',
              'https://www.epicgame.com.br/': 'Epic',
              'https://www.flowstore.com.br/': 'Flow',
              'https://www.magicdomain.com.br/': 'Magic Domain',
              'https://www.medievalcards.com.br/': 'Medieval'
              }

path = 'Decks/Tom Bombadil'
deck = 'Tom Bombadil'

headers = {'User-Agent': 'Mozilla'}

# Sub-Main --------------------------------------------------------
limiter = AsyncLimiter(40, 0.125)
headers = {'User-Agent': 'Custom'}


def highlight_max(s):
    is_max = s == s.max()
    return ['background-color: green' if v else '' for v in is_max]


def _draw_as_table(df, pagesize):
    alternating_colors = [['white'] * len(df.columns), ['lightgray'] * len(df.columns)] * len(df)
    alternating_colors = alternating_colors[:len(df)]
    fig, ax = plt.subplots(figsize=pagesize)
    ax.axis('tight')
    ax.axis('off')
    colors = []
    sum_min = 0
    for line_number, (idx, row) in enumerate(df.iterrows()):
        colors_in_column = alternating_colors[line_number].copy()
        loja_dict = row[row != 0.0].to_dict()
        try:
            del loja_dict['Liga Magic']
        except KeyError:
            pass
        try:
            loja_name = min(loja_dict, key=loja_dict.get)
        except:
            loja_name = random.choice(list(row.index))
        min_price = float(row[loja_name])
        if idx == 'Total':
            min_price = 0
        sum_min += min_price
        loja_index = df.columns.tolist().index(f'{loja_name}')
        colors_in_column[loja_index] = 'g'
        colors.append(colors_in_column)
    the_table = ax.table(cellText=df.values,
                         rowLabels=df.index,
                         colLabels=df.columns,
                         rowColours=['lightblue'] * len(df),
                         colColours=['lightblue'] * len(df.columns),
                         cellColours=colors,
                         loc='center')
    return fig, sum_min


def dataframe_to_pdf(df, filename, numpages=(1, 1), pagesize=(11, 8.5), path=''):
    with PdfPages(f'{filename}') as pdf:
        nh, nv = numpages
        rows_per_page = len(df) // nh
        cols_per_page = len(df.columns) // nv
        for i in range(0, nh):
            for j in range(0, nv):
                page = df.iloc[(i * rows_per_page):min((i + 1) * rows_per_page, len(df)),
                       (j * cols_per_page):min((j + 1) * cols_per_page, len(df.columns))]
                fig, sum_min = _draw_as_table(page, pagesize)
                if nh > 1 or nv > 1:
                    # Add a part/page number at bottom-center of page
                    fig.text(0.5, 0.5 / pagesize[0],
                             "Part-{}x{}: Page-{}".format(i + 1, j + 1, i * nv + j + 1),
                             ha='center', fontsize=8)
                pdf.savefig(fig, bbox_inches='tight')
                fig.savefig(filename)
                return pdf, fig, sum_min

async def get_html_info(store_website: str, card: str, semaphore, tries=0) -> str:
    url = f'{store_website}?view=ecom%2Fitens&id=82238&searchExactMatch=&busca={"+".join(card.strip("").split(" "))}' \
          f'&txt_limit=120&txt_estoque=1'
    while True and tries < 10:
        try:
            async with aiohttp.ClientSession(headers=headers, trust_env=True) as session:
                await semaphore.acquire()
                async with limiter:
                    async with session.get(url) as resp:
                        content = await resp.read()
                        semaphore.release()
                        return content
        except (aiohttp.ServerDisconnectedError, aiohttp.ClientResponseError,
                aiohttp.ClientConnectorError) as s:
            await asyncio.sleep(1)
            tries += 1


async def get_html_info_liga(card: str, semaphore, tries=0) -> str:
    url = f'https://www.ligamagic.com.br/?view=cards/card&card={"+".join(card.strip("").split(" "))}'
    while True and tries < 10:
        try:
            async with aiohttp.ClientSession(headers=headers, trust_env=True) as session:
                await semaphore.acquire()
                async with limiter:
                    async with session.get(url) as resp:
                        content = await resp.read()
                        semaphore.release()
                        return content
        except (aiohttp.ServerDisconnectedError, aiohttp.ClientResponseError,
                aiohttp.ClientConnectorError) as s:
            await asyncio.sleep(1)
            tries += 1


async def treat_html_liga(card: str, semaphore):
    content = await get_html_info_liga(card, semaphore)
    card_list = await process_liga(content, card)
    return card_list

async def treat_html(store_name: str, store_website: str, card: str, semaphore):
    content = await get_html_info(store_website, card, semaphore)
    card_list = await process(store_name, content, card)
    return card_list


async def process(store_name, content: str, card: str) -> dict:
    _soup = BeautifulSoup(content, "lxml")
    if _soup.find(lambda tag: tag.name == 'div' and
                              tag.get('class') == ['cards']):
        for card_item in _soup.find_all(lambda tag: tag.name == 'div' and
                              tag.get('class') == ['card-item']):
            if not any(text in card_item.find('div', {'class': 'title'}).text.lower() for text in {'(art card', '//'}):
                url_base = _soup.find("meta", property="og:url")['content'].split('/', 3)[0:3]
                url_base.remove('')
                start_url_new = "//".join(url_base) + '/'
                end_url_new = \
                    card_item.find('div', {'class': 'title'}).find('a')['href'].split(
                        '/',
                        1)[-1]
                url_new = start_url_new + end_url_new
                _soup = BeautifulSoup(requests.get(f'{url_new}', headers={'User-Agent': 'Custom'}).text, 'lxml')
                break
    _prices_divs = _soup.find_all("div", {"class": "table-cards-row"})
    _price_set = set()
    try:
        for _price_text in _prices_divs:
            try:
                _text = _price_text.find_all('div', {'class':'title-mobile'})[-1].nextSibling.text.lstrip(
                    'R$').strip()
            except:
                _text = _price_text.find('div', {'class': 'table-cards-body-cell card-preco'}).text.strip().lstrip(
                    'R$').strip()
                _text = "".join(letter for letter in _text if letter.isdigit() or letter in {'.', ','})
            try:
                _price = float(_text.split('R$')[-1].replace('.', '').replace(',', '.'))
            except:
                _price = 0
            _price_set.add(_price)
        card_dict = defaultdict()
        card_dict['Carta'] = card
        try:
            card_dict[f'{store_name}'] = sorted(_price_set)[0]
        except:
            card_dict[f'{store_name}'] = _price = 0
    except:
        pass
    return card_dict

async def process_liga(html, card):
    _soup = BeautifulSoup(html, "lxml")
    _price_segment = _soup.find_all('script', {'type': 'text/javascript'})
    price = 0
    for _price_text in _price_segment:
        if "avgprice='" in _price_text.text:
            try:
                price_dict = json.loads(_price_text.text.split("avgprice='")[-1].strip(";|,|'"))
                list_of_prices = [v for _, v in price_dict.items()]
                for dict_price in list_of_prices:
                    if "extras" in dict_price:
                        list_of_prices.extend([v for v in dict_price['extras'].copy().values()])
                        del dict_price['extras']
                prices = {price['precoMenor'] for price in list_of_prices}
                prices.discard(0)
                price = min(prices)
            except:
                pass
            break
    nome_carta = card
    card_dict = defaultdict()
    card_dict['Carta'] = card
    card_dict[f'Liga Magic'] = price
    return card_dict

async def get_card_list(card_set: set, store_name, store_website: str) -> list:
    semaphore = asyncio.Semaphore(value=5)
    tasks = [treat_html(store_name, store_website, card, semaphore) for card in card_set]
    card_list = await stqdm.gather(*tasks)
    return card_list


async def get_card_list_liga(card_set: set) -> list:
    semaphore = asyncio.Semaphore(value=5)
    tasks = [treat_html_liga(card, semaphore) for card in card_set]
    card_list = await stqdm.gather(*tasks)
    return card_list

async def main(store_dict:dict, card_set: set):
    tasks = [get_card_list(card_set, store_name, store_website) for store_website, store_name in store_dict.items()]
    card_list = await asyncio.gather(*tasks)
    card_list_liga = await get_card_list_liga(card_set)
    card_list.extend([card_list_liga])
    return card_list


def read_deck_file(file: str):
    with open(file, 'r', encoding='utf-8-sig') as f:
        lines = {''.join([i for i in line if not i.isdigit()]).strip() for line in f}
    return lines


def create_output_folder(path: str):
    Path(f"{path}").mkdir(parents=True, exist_ok=True)

def main_module(card_input:str, checkbox_list:list):
    store_dict = {'https://www.bazardebagda.com.br/': 'Bazar',
                  'https://www.cardtutor.com.br/': 'Card Tutor',
                  'https://www.chq.com.br/': 'CHQ',
                  'https://www.epicgame.com.br/': 'Epic',
                  'https://www.flowstore.com.br/': 'Flow',
                  'https://www.magicdomain.com.br/': 'Magic Domain',
                  'https://www.medievalcards.com.br/': 'Medieval'
                  }
    card_set = {''.join([i for i in line if not i.isdigit()]).strip() for line in card_input.split('\n')}
    card_set.discard('')
    store_dict_input = defaultdict()
    for idx, (k, v) in enumerate(store_dict.items()):
        if checkbox_list[idx]:
            store_dict_input[f'{k}'] = v
    card_list = asyncio.run(main(store_dict_input, card_set))
    df_list = [pd.DataFrame(df).set_index('Carta') for df in card_list]
    column_names = list(store_dict_input.values())
    column_names.extend(['Liga Magic'])
    df_raw = pd.DataFrame(index=list(card_set), columns=column_names)
    for df in df_list:
        df_raw.update(df)
    df_raw = df_raw.sort_values('Liga Magic', ascending=False)
    df_raw.loc['Total', :] = df_raw.sum(axis=0)
    pdf, fig, sum_min = dataframe_to_pdf(df_raw, f'Deck.pdf', path=path)
    st.dataframe(df_raw)
    st.write(f'Comprando cada carta na loja mais barata detectada, seu deck custará R$ {sum_min}.')
    st.pyplot(fig)



if __name__ == "__main__":
    start_time = time.time()
    path = 'Decks/Tom Bombadil'
    create_output_folder(path)
    card_set = read_deck_file(f'{path}/deck.mtg')
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    card_list = asyncio.run(main(store_dict, card_set))
    df_list = [pd.DataFrame(df).set_index('Carta') for df in card_list]
    column_names = list(store_dict.values())
    column_names.extend(['Liga Magic'])
    df_raw = pd.DataFrame(index=list(card_set), columns=column_names)
    for df in df_list:
        df_raw.update(df)
    df_raw = df_raw.sort_values('Bazar', ascending=False)
    df_raw.loc['Total', :] = df_raw.sum(axis=0)
    dataframe_to_pdf(df_raw, f'Deck - {deck}.pdf', path=path)
    print("--- %s  seconds ---" % (time.time() - start_time))
