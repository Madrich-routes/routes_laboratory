import asyncio
from asyncio import Future, get_event_loop
from datetime import datetime
from typing import List, Set, Tuple, Union

import numpy as np
from aiohttp.client import ClientSession
from herepy import MatrixSummaryAttribute, RouteMode
from ujson import loads

array = np.ndarray

Point = Tuple[float, float]
Points = Union[array, List[Point]]

factor_to_summary = {
    'costFactor': MatrixSummaryAttribute.cost_factor,
    'travelTime': MatrixSummaryAttribute.travel_time,
    'distance': MatrixSummaryAttribute.distance
}


def run(function, **kwargs):
    """Обертка для асинхронных функций, которые используют aiohttp.

    :param function: вызываемая ф-я
    :param kwargs: параметры для нее
    :return: ну че там вызвали, то и вернет
    """

    async def __run():
        async with ClientSession() as session:
            kwargs.update({'session': session})
            return await function(**kwargs)

    return get_event_loop().run_until_complete(__run())


def get_matrix(points: Points, modes: List[RouteMode], start_t: float, key: str,
               factor: Union[str, List[str]] = 'travelTime') -> Points:
    """Get full Adjacency matrix.

    :param points: points
    :param modes: [Type, TransportMode, TrafficMode, Feature]
    :param start_t: start time in seconds
    :param key: API key
    :param factor: adjacency matrix values
    :return: Adjacency matrix
    """
    return run(function=HereModule.get_matrix, points=points, modes=modes, key=key, start_t=start_t, factor=factor)


def get_matrix_sd(src: Points, dst: Points, modes: List[RouteMode],
                  start_t: float, key: str, factor: Union[str, List[str]]) -> Points:
    """Get matrix from sources to destinations.

    :param src: sources
    :param dst: destinations
    :param modes: modes here api
    :param start_t: start time
    :param key: here api key
    :param factor: factors for matrix
    :return:
    """
    return run(function=HereModule.get_matrix_sd, src=src, dst=dst,
               modes=modes, key=key, start_t=start_t, factor=factor)


def get_matrices(points: Points, modes: List[RouteMode], start_t: float, max_cost: int, key: str,
                 split=15, factor: Union[str, List[str]] = 'travelTime') -> Points:
    """ All adjacency matrices from start time to max_cost time every disc minutes
    :rtype: object
    :param points: points
    :param modes: [Type, TransportMode, TrafficMode, Feature]
    :param start_t: start time in seconds
    :param max_cost: max cost of tour
    :param key: API key
    :param split: minutes
    :param factor: adjacency matrix values
    :return: all these matrices : [time index][src][dst]
    """
    return run(function=HereModule.get_matrices, points=points, modes=modes, start_t=start_t,
               max_cost=max_cost, key=key, split=split, factor=factor)


class HereModule:
    URL_MATRIX = 'https://matrix.route.ls.hereapi.com/routing/7.2/calculatematrix.json'

    @staticmethod
    async def __get(url: str, session: ClientSession, data: dict) -> dict:
        async with session.get(url, params=data) as resp:
            if resp.status != 200:
                raise Exception(f'Response error: {resp.status} - {resp.reason}')
            return loads(await resp.text('utf-8'))

    @staticmethod
    async def matrix(session: ClientSession, src: Points, dst: Points,
                     modes: List[RouteMode], summary: List[MatrixSummaryAttribute], key: str, departure='now') -> dict:
        """Matrix between M starts and N destinations, M < 16.

        :param session: aiohttp ClientSession
        :param src: points
        :param dst: points
        :param modes: [Type, TransportMode, TrafficMode, Feature]
        :param summary: MatrixSummaryAttribute
        :param key: API key
        :param departure: "%Y-%m-%dT%H:%M:%S+0?" - '2013-07-04T17:00:00+02'
        :return: big dict
        """
        assert len(src) <= 15, 'len src > 15'
        assert len(dst) <= 100, 'len dst > 100'

        data = {
            'apikey': key,
            'departure': departure,
            'mode': ';'.join([str(mode) for mode in modes]),
            'summaryAttributes': ','.join([str(attribute) for attribute in summary])
        }
        data.update({f'start{i}': f'geo!{round(pt[0], 6)},{round(pt[1], 6)}' for i, pt in enumerate(src)})
        data.update({f'destination{i}': f'geo!{round(pt[0], 6)},{round(pt[1], 6)}' for i, pt in enumerate(dst)})

        return await HereModule.__get(HereModule.URL_MATRIX, session, data)

    @staticmethod
    def __return_matrix(fact: str, size_x: int, size_y: int, done: Set[Future], src: Points, dst: Points):
        matrix = np.zeros(shape=(size_x, size_y), dtype=np.int64)
        for future in done:
            idx, jdx, data = future.result()
            entries = data['response']['matrixEntry']
            for entry in entries:
                try:
                    dest_index, src_index = entry['destinationIndex'], entry['startIndex']
                    if 'summary' not in entry:
                        matrix[src_index + idx * 15][dest_index + jdx * 100] = -1
                    assert 'summary' in entry, f'{entry} ' \
                                               f'from {src[src_index + idx * 15]} ' \
                                               f'to {dst[dest_index + jdx * 100]}'
                    matrix[src_index + idx * 15][dest_index + jdx * 100] = entry['summary'][fact]
                except Exception as exc:
                    print(exc)
        return matrix

    @staticmethod
    async def get_matrix_sd(session: ClientSession, src: Points, dst: Points, modes: List[RouteMode],
                            start_t: float, key: str, factor: Union[str, List[str]]) -> Union[array, List[array]]:

        size_src, size_dst = len(src), len(dst)
        cell = int(np.ceil(size_src / 15)), int(np.ceil(size_dst / 100))
        departure = datetime.fromtimestamp(start_t).strftime("%Y-%m-%dT%H:%M:%S+03")  # Moscow
        summary = [factor_to_summary[factor]] if type(factor) is str else [factor_to_summary[f] for f in factor]

        async def executor(x, y, src_small, dst_small):
            return x, y, await HereModule.matrix(session, src_small, dst_small, modes, summary, key, departure)

        f = []
        for i in range(cell[0]):
            for j in range(cell[1]):
                f.append(executor(i, j, src[i * 15: (i + 1) * 15], dst[j * 100: (j + 1) * 100]))
        done, _ = await asyncio.wait(f)

        if type(factor) is str:
            return HereModule.__return_matrix(factor, size_src, size_dst, done, src, dst)
        return [HereModule.__return_matrix(f, size_src, size_dst, done, src, dst) for f in factor]

    @staticmethod
    async def get_matrix(session: ClientSession, points: Points, modes: List[RouteMode],
                         start_t: float, key: str, factor: Union[str, List[str]]) -> Union[array, List[array]]:
        """Get full Adjacency matrix.

        :param session: aiohttp ClientSession
        :param points: points
        :param modes: [Type, TransportMode, TrafficMode, Feature]
        :param start_t: start time in seconds
        :param key: API key
        :param factor: adjacency matrix values
        :return: Adjacency matrix
        """
        size, f = len(points), []
        cell = int(np.ceil(size / 15)), int(np.ceil(size / 100))
        summary = [factor_to_summary[factor]] if type(factor) is str else [factor_to_summary[f] for f in factor]
        departure = datetime.fromtimestamp(start_t).strftime("%Y-%m-%dT%H:%M:%S+03")  # Moscow

        async def executor(x, y, src, dst):
            return x, y, await HereModule.matrix(session, src, dst, modes, summary, key, departure)

        for i in range(cell[0]):
            for j in range(cell[1]):
                f.append(executor(i, j, points[i * 15: (i + 1) * 15], points[j * 100: (j + 1) * 100]))
        done, _ = await asyncio.wait(f)

        if type(factor) is str:
            return HereModule.__return_matrix(factor, size, size, done, points, points)
        return [HereModule.__return_matrix(f, size, size, done, points, points) for f in factor]

    @staticmethod
    async def get_matrices(session: ClientSession, points: Points, modes: List[RouteMode],
                           factor: Union[str, List[str]], start_t: float, max_cost: int, key: str, split: int,
                           ) -> Union[array, List[array]]:
        """All adjacency matrices from start time to max_cost time every disc minutes.

        :param session: aiohttp ClientSession
        :param points: points
        :param modes: [Type, TransportMode, TrafficMode, Feature]
        :param start_t: start time in seconds
        :param max_cost: max cost of tour
        :param key: API key
        :param split: minutes
        :param factor: adjacency matrix values
        :return: all these matrices : [time index][src][dst]
        """
        split *= 60  # to seconds
        size = len(points)
        length = int(np.ceil(max_cost / split))

        async def executor(i, start):
            return i, await HereModule.get_matrix(session, points, modes, start, key, factor)

        f = [executor(i, start_t + (i * split)) for i in range(length)]
        done, _ = await asyncio.wait(f)

        if type(factor) is str:
            matrices = np.zeros(shape=(length, size, size), dtype=np.int64)
            for future in done:
                i, matrix = future.result()
                matrices[i] = matrix
        else:

            def return_matrices(num):  # очень стремно, но пофиг
                m_tmp = np.zeros(shape=(length, size, size), dtype=np.int64)
                for fut in done:
                    i, m = fut.result()
                    m_tmp[i] = m[num]
                return m_tmp

            matrices = [return_matrices(j) for j in range(len(factor))]

        return matrices
