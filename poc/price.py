import asyncio
import builtins
import random
import time
from datetime import date, timedelta

import aiohttp
import tushare as ts
from bs4 import BeautifulSoup
from config import Config
from logger import logger


class Price:
    # cfg will not be None
    cfg = Config.config()

    @classmethod
    def tushare_token(cls):
        try:
            return cls.cfg['stock']['tushare']['token']
        except Exception:
            logger.error('Fail to get tushare token from config')
        return None

    '''
    Used when tushare API supports query multiple stocks as input
    @classmethod
    def tushare_code(cls, ids):
        codes = ''
        try:
            for _id in ids:
                _code = _id
                if (_id[0] == '0'):
                    _code += '.SZ'
                elif (_id[0] == '6'):
                    _code += '.SH'
                codes += f'{_code}, '
        except Exception as e:
            logger.error(f'Generate tushare code fail: {e}')
        return codes

    @classmethod
    @retry(tries=3, delay=1)
    def tushare_price(cls, codes, reqDate, stock_num):
        # --- Get token from memory
        token = cls.tushare_token()
        if not token:
            return None

        ts.set_token(token)

        tmpDays = 0
        if not reqDate:
            reqDate = date.today()

        retry_num = 3
        try:
            while retry_num > 0:
                delta = timedelta(days=tmpDays)
                day = (reqDate+delta).strftime('%Y%m%d')

                df = ts.pro_bar(ts_code=codes, start_date=day, end_date=day)
                if 'close' in df and len(df['close'] > 0):
                    if len(df['close'].to_dict()) == stock_num:
                        break
                    else:
                        logger.warning(f'Only get {len(df["close"].to_dict())} stock prices, target is {stock_num}. Retry!')
                        time.sleep(random.uniform(1, 2))
                        retry_num = retry_num - 1
                        continue
                else:
                    tmpDays -= 1
                    continue

            if retry_num == 0:
                logger.error('Get stock price failure!')
                raise

            close_data = df['close']
            close_data.index = [_code[:-3] for _code in df['ts_code'] if len(_code) > 6]
            return close_data.to_dict()
        except Exception as e:
            logger.error(f'Get tushare price fail: {e}')
            # Raise the same for @retry
            raise
        return None

    @classmethod
    def stock_price(cls, ids, reqDate=None):
        codes = cls.tushare_code(ids)
        if not codes:
            return None

        return cls.tushare_price(codes, reqDate, len(ids))
    '''

    @classmethod
    def tushare_code_list(cls, ids):
        codes = []
        try:
            for _id in ids:
                _code = _id
                if (_id[0] == '0'):
                    _code += '.SZ'
                elif (_id[0] == '6'):
                    _code += '.SH'
                codes.append(_code)
        except Exception as e:
            logger.error(f'Generate tushare code fail: {e}')
        return codes

    @classmethod
    def tushare_price(cls, codes, reqDate):
        # --- Get token from memory
        token = cls.tushare_token()
        if not token:
            return None

        ts.set_token(token)


        close_data_dict = {}

        tmpDays = 0
        if not reqDate:
            reqDate = date.today()
        delta = timedelta(days=tmpDays)
        day = (reqDate+delta).strftime('%Y%m%d')

        dayFound = False
        for code in codes:
            retry_num = 3
            try:
                while retry_num > 0:
                    if not dayFound:
                        delta = timedelta(days=tmpDays)
                        day = (reqDate+delta).strftime('%Y%m%d')

                    # df = ts.pro_bar(ts_code=code, start_date=day, end_date=day)
                    df = ts.pro_api().daily(ts_code=code, trade_date=day)
                    if 'close' in df and len(df['close'] > 0):
                        break
                    elif dayFound:
                        retry_num -= 1
                        continue
                    else:
                        tmpDays -= 1
                        continue

                if retry_num == 0:
                    logger.warning(f'Get stock price for {code} fail')
                    continue
                close_data = df['close']
                close_data.index = [_code[:-3] for _code in df['ts_code'] if len(_code) > 6]
                close_data_dict.update(close_data.to_dict())
            except Exception as e:
                logger.error(f'Get tushare price for {code} fail: {e}')
                # Raise the same for @retry
        return close_data_dict

    @classmethod
    def stock_price(cls, ids, reqDate=None):
        codes = cls.tushare_code_list(ids)
        if not codes:
            return None

        return cls.tushare_price(codes, reqDate)

    @classmethod
    async def async_download_coroutine(cls, session, url, retry=0):
        try:
            async with session.get(url) as response:
                ori_content = await response.read()
            soup = BeautifulSoup(ori_content, 'lxml')
            content = soup.find('td', attrs={'class' : 'tor bold'})
            # Means parse fail, server may encouter error or rate limit
            if not content:
                return None
            netVal = content.string
            return float(str(netVal))
        except Exception:
            retry += 1
            if retry > 10:
                raise builtins.TimeoutError
            await cls.async_download_coroutine(session, url, retry)

    @classmethod
    async def async_get_fund_net_val(cls, loop, id, reqDate, sem):
        async with sem:
            async with aiohttp.ClientSession(loop=loop) as session:
                if reqDate:
                    tmpDays = 0
                    while tmpDays > -20:
                        delta = timedelta(days=tmpDays)
                        day = date.isoformat(reqDate+delta)
                        url = f'https://fundf10.eastmoney.com/F10DataApi.aspx?type=lsjz&code={id}&page=1&per=1&sdate={day}&edate={day}'
                        time.sleep(random.uniform(0.2, 0.5))
                        netVal = await cls.async_download_coroutine(session, url)
                        if netVal:
                            break
                        tmpDays -= 1
                    if tmpDays == -20:
                        return 0
                else:
                    url = f'https://fundf10.eastmoney.com/F10DataApi.aspx?type=lsjz&code={id}&page=1&per=1'
                    netVal = await cls.async_download_coroutine(session, url)
                return netVal

    @classmethod
    async def async_func(cls, func, loop, ids, reqDate=None):
        sem = asyncio.Semaphore(cls.cfg['fund']['eastmoney']['aio_req_num'])
        coros = [func(loop, _id, reqDate, sem) for _id in ids]
        return await asyncio.gather(*coros)

    @classmethod
    def get_fund_net_val_dict(cls, ids, reqDate=None):
        try:
            loop = asyncio.get_event_loop()
        except Exception:
            loop = asyncio.new_event_loop()

        try:
            netVals = loop.run_until_complete(
                    cls.async_func(cls.async_get_fund_net_val, loop, ids, reqDate))
            result = dict(zip(ids, netVals))
            for key, value in result.items():
                if value == 0:
                    logger.error(f'Get fund net value fail: {key}, {reqDate}')
            return result
        except Exception as e:
            logger.error(f'Get fund net value fail: {e}')
        return None

    @classmethod
    def fund_price(cls, ids, reqDate=None):
        return cls.get_fund_net_val_dict(ids, reqDate)
