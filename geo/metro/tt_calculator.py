"""В этом модуле создается матрица расстояний с учетом общественного транспорта."""
import os

import bs4
import numpy as np
import pandas as pd
import requests
from geopy.distance import distance
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph._shortest_path import floyd_warshall


class MetroWalker:
    def __init__(self, xml_filename, dataframe: pd.DataFrame = None, matrix: np.ndarray = None):
        """parse metro xml."""
        self.dataframe = dataframe or self.parse_metrodata(xml_filename)
        """
        calculate time budgets
        """
        self.matrix = self.build_graph(self.dataframe) if not matrix else matrix

    def get_metro_xml(self, url):
        headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:45.0) G`ecko/20100101 Firefox/45.0'}
        r = requests.get(url, headers=headers)
        return r.text

    def parse_metrodata(self, xml_url_or_filename):
        if os.path.exists(xml_url_or_filename):
            print(f'Get XML from file: {xml_url_or_filename}')

            with open(xml_url_or_filename) as f:
                soup = bs4.BeautifulSoup(f.read(), 'lxml')
        else:
            print(f'Get XML from url: {xml_url_or_filename}')
            soup = bs4.BeautifulSoup(self.get_metro_xml(xml_url_or_filename), 'lxml')

        stations = soup.find('scheme', {'locale': 'ru'}).findAll('station')
        data = {}
        for station in stations:
            try:
                name = station.find('name').find('text').text
            except:
                try:
                    name = int(station.find('name')['sameasforstation'])
                except:
                    continue
                # name = int(re.sub(r"[^0-9.,]+", '', station.find('name').text))
            # print(station['id'])
            data[int(station['id'])] = {'coord': (
            float(station.find('geocoordinates')['latitude']), float(station.find('geocoordinates')['longitude'])),
                                        'name': name, 'links': []}

        for id, item in data.items():
            if type(item['name']) == int:
                item['name'] = data[item['name']]['name']

        links = soup.find('scheme', {'locale': 'ru'}).find('links')
        for weight, link in zip(links.findAll('weight', {'type': 'time'}), links.findAll('link')):
            data[int(link['fromstation'])]['links'].append({int(link['tostation']): float(weight.text)})
            data[int(link['tostation'])]['links'].append({int(link['fromstation']): float(weight.text)})

        dataframe = pd.DataFrame.from_dict(data, orient='index')
        return dataframe

    def build_graph(self, data):
        res = max(int(k) for k in data.index)
        matrix = [[0] * (res + 1) for i in range(res + 1)]

        for sid1, station_data in data.iterrows():
            for link in station_data['links']:
                # print(link)
                for sid2, dist in link.items():
                    matrix[int(sid1)][int(sid2)] = dist

        graph = csr_matrix(matrix)

        dist_matrix, predecessors = floyd_warshall(csgraph=graph, directed=False, return_predecessors=True)

        return dist_matrix

    def walking_time(self, start, finish):
        """time in seconds."""
        return (distance(start, finish).km / 5.0) * 3600

    def calc_time(self, start, finish):
        by_walk = self.walking_time(start, finish)
        print(f"Time by walk: {by_walk:.2f}sec")
        self.dataframe['from_start'] = list(map(lambda x: distance(x, start).km, self.dataframe['coord']))
        self.dataframe['from_finish'] = list(map(lambda x: distance(x, finish).km, self.dataframe['coord']))

        best_time = by_walk
        for fr in self.dataframe.sort_values(by='from_start')[:10].index:
            for to in self.dataframe.sort_values(by='from_finish')[:10].index:
                budget = self.matrix[fr][to] + self.walking_time(self.dataframe.loc[fr, 'coord'],
                                                                 start) + self.walking_time(
                    self.dataframe.loc[to, 'coord'], finish)
                best_time = min(best_time, budget)
                ### Printing
                print(f"Time for route {self.dataframe.loc[fr, 'name']}->{self.dataframe.loc[to, 'name']}:\t \
walk: {self.walking_time(self.dataframe.loc[fr, 'coord'], start):.2f} + train:{self.matrix[fr][to]:.2f} + \
walk: {self.walking_time(self.dataframe.loc[to, 'coord'], finish):.2f} = {budget:.2f}sec")

        print(f"Best time: {best_time:.2f}sec")
        return best_time


def main():
    xml_filename = 'moscow_metro.xml'
    xml_url = 'https://metro.mobile.yandex.net/metro/get_file?file=scheme_1.xml&ver='
    start = (55.94, 37.52)
    finish = (55.73, 37.70)
    mv = MetroWalker(xml_url)
    mv.calc_time(start, finish)
    mv.calc_time(finish, start)


if __name__ == "__main__":
    main()
