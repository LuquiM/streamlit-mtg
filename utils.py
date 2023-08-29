# Script para consolidação de biblioteca de utilidades.
# Dev: Lucca Mariano

# Imports ---------------------------------------------------------
import requests
from bs4 import BeautifulSoup
import pandas as pd
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
# Sub-Main -------------------------------------------------------
def create_output_folder(path:str):
    Path(f"{path}").mkdir(parents=True, exist_ok=True)

def treat_dataframe(df: pd.DataFrame):
    df.rename(columns=lambda x: x.strip(), inplace=True)
    df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
    df.fillna('', inplace=True)
    df = df.dropna(how='all', inplace=True)
    return df
if __name__ == '__main__':
    print('Bem vindo à minha biblioteca!')