import requests
from bs4 import BeautifulSoup
import math
import re
import pandas as pd

DOLAR_BLUE_HOY = float(1100)

# Agrego estas lineas para pasar marcas y modelos directamente como archivo CSV.
# en caso de querer usar solo una marca/modelo, comentar las proximas 5 lineas y modificar marca y modelo hardcodeados

df = pd.read_csv('modelos.csv', delimiter=',')
df = df.reset_index()
for index, row in df.iterrows():
    Marca = row["Marca"]
    Modelo = row["Modelo"]
    URL = "https://autos.mercadolibre.com.ar/" + Marca + "/" +  Modelo + "/"

    items_dict = []

    def dict_to_csv_file(listate:list, csv_file: str) -> None:
        try:
            with open(csv_file, 'w') as csvfile:
                csvfile.write(",".join(listate[0].keys()) + "\n")
                for li in listate:
                    csvfile.write(",".join(li.values())+"\n")
        except IOError:
            print("I/O error")



    def main():
        page = 1
        response = requests.get(URL)
        soup = BeautifulSoup(response.text, "html.parser")
        total_resultados = int(re.findall(r'\d+', soup.find(class_="ui-search-search-result__quantity-results").string.replace(".",""))[0])
        total_paginas = math.trunc(total_resultados / 48) + 1
    #    total_paginas = int(soup.find(class_="andes-pagination__page-count").text.split(" ")[-1])
        #if total_resultados <= 49:
        for item in soup.findAll('li', class_='ui-search-layout__item'):
            moneda = item.find(class_='andes-money-amount__currency-symbol').text
            price = item.find(class_='andes-money-amount__fraction').text.replace('.', '')
            location = item.find(class_='ui-search-item__location').text
            price_if_blue = str(int(float(price) / DOLAR_BLUE_HOY))
            items_dict.append(
                {
                    'title': item.find(class_='ui-search-item__title').text.replace(',', ' '),
                    'moneda': moneda,
                    'price': price,
                    'price_in_blue': price if moneda == 'US$' else price_if_blue,
                    'year': item.findAll(class_='ui-search-card-attributes__attribute')[0].text,
                    'km': item.findAll(class_='ui-search-card-attributes__attribute')[1].text.replace('Km', ''),
                    'location': location,
                    'link': item.find('a', class_='ui-search-link')['href'],
                    'page': str(page)
                }
            )
        if total_resultados > 49:
            while next_url_html := soup.find(class_="andes-pagination__button--next").find(class_="andes-pagination__link")["href"]:
                next_url_html = soup.find(class_="andes-pagination__button--next").find(class_="andes-pagination__link")["href"]
                page += 1
                response = requests.get(next_url_html)

                soup = BeautifulSoup(response.text, "html.parser")

                for item in soup.findAll('li', class_='ui-search-layout__item'):
                    moneda = item.find(class_='andes-money-amount__currency-symbol').text
                    price = item.find(class_='andes-money-amount__fraction').text.replace('.','')
                    location = item.find(class_='ui-search-item__location').text
                    price_if_blue = price if moneda == 'US$' else str(int(float(price) / DOLAR_BLUE_HOY))

                    items_dict.append(
                        {
                            'title': item.find(class_='ui-search-item__title').text.replace(',', ' '),
                            'moneda': moneda,
                            'price': price,
                            'price_in_blue': price_if_blue,
                            'year': item.findAll(class_='ui-search-card-attributes__attribute')[0].text,
                            'km': item.findAll(class_='ui-search-card-attributes__attribute')[1].text.replace('Km', ''),
                            'location': location,
                            #'distance': distance_km,
                            'link': item.find('a', class_='ui-search-link')['href'],
                            'page': str(page)
                        }
                    )
                print(f"Pagina {page} de {total_paginas} de {Marca} {Modelo}")

        dict_to_csv_file(items_dict, Modelo +".csv")
    if __name__ == '__main__':
        main()
        print("Fin del Scrapeo de "+ Modelo)
print("Fin del scrapeo de los siguientes modelos")
print(df)
