"""
数据获取工具

从tushare或akshare获取A股K线数据。
"""
import pandas as pd
from typing import Optional, Literal
from datetime import datetime, timedelta
import time

from .exceptions import DataFetchError
from .logger import default_logger as logger


def get_klines(
    stock_code: str,
    market: str = 'SZ',
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    freq: str = 'D',
    data_source: Literal['tushare', 'akshare'] = 'akshare',
    tushare_token: Optional[str] = None,
    retry_times: int = 3,
    retry_delay: int = 2
) -> pd.DataFrame:
    """
    获取K线数据
    
    Args:
        stock_code: 股票代码（6位数字）
        market: 市场代码（SH或SZ）
        start_date: 开始日期（YYYY-MM-DD或YYYYMMDD）
        end_date: 结束日期（YYYY-MM-DD或YYYYMMDD）
        freq: K线频率（D=日线，W=周线，M=月线，5=5分钟，30=30分钟等）
        data_source: 数据源（tushare或akshare）
        tushare_token: Tushare API Token
        retry_times: 重试次数
        retry_delay: 重试延迟（秒）
    
    Returns:
        K线数据DataFrame，包含以下列：
        - datetime: 日期时间
        - open: 开盘价
        - high: 最高价
        - low: 最低价
        - close: 收盘价
        - volume: 成交量
        - amount: 成交额
    
    Raises:
        DataFetchError: 数据获取失败
    """
    # 格式化日期
    if start_date:
        start_date = start_date.replace('-', '')
    if end_date:
        end_date = end_date.replace('-', '')
    
    # 如果没有指定结束日期，使用今天
    if not end_date:
        end_date = datetime.now().strftime('%Y%m%d')
    
    # 如果没有指定开始日期，使用一年前
    if not start_date:
        start_date = (datetime.now() - timedelta(days=365)).strftime('%Y%m%d')
    
    logger.info(f"开始获取K线数据：股票={market}{stock_code}，开始日期={start_date}，结束日期={end_date}，频率={freq}，数据源={data_source}")
    
    # 尝试获取数据
    for attempt in range(retry_times):
        try:
            if data_source == 'tushare':
                df = _get_klines_from_tushare(
                    stock_code, market, start_date, end_date, freq, tushare_token
                )
            else:
                df = _get_klines_from_akshare(
                    stock_code, market, start_date, end_date, freq
                )
            
            if df is not None and len(df) > 0:
                logger.success(f"成功获取{len(df)}条K线数据")
                return df
            else:
                raise DataFetchError(
                    f"获取到的数据为空",
                    stock_code=f"{market}{stock_code}"
                )
        
        except Exception as e:
            logger.warning(f"第{attempt + 1}次尝试失败：{str(e)}")
            if attempt < retry_times - 1:
                time.sleep(retry_delay)
            else:
                raise DataFetchError(
                    f"获取K线数据失败，已重试{retry_times}次：{str(e)}",
                    stock_code=f"{market}{stock_code}"
                )
    
    raise DataFetchError(
        "获取K线数据失败",
        stock_code=f"{market}{stock_code}"
    )


def _get_klines_from_tushare(
    stock_code: str,
    market: str,
    start_date: str,
    end_date: str,
    freq: str,
    token: Optional[str]
) -> Optional[pd.DataFrame]:
    """
    从Tushare获取K线数据
    
    Args:
        stock_code: 股票代码
        market: 市场代码
        start_date: 开始日期
        end_date: 结束日期
        freq: K线频率
        token: Tushare Token
    
    Returns:
        K线数据DataFrame
    """
    try:
        import tushare as ts
        
        # 设置token
        if token:
            ts.set_token(token)
        
        pro = ts.pro_api()
        
        # 构建完整股票代码
        ts_code = f"{stock_code}.{market.lower()}"
        
        # 映射频率
        freq_map = {
            'D': 'daily',
            'W': 'weekly',
            'M': 'monthly',
            '5': '5min',
            '15': '15min',
            '30': '30min',
            '60': '60min'
        }
        
        api_freq = freq_map.get(freq, 'daily')
        
        # 获取数据
        if api_freq in ['daily', 'weekly', 'monthly']:
            df = pro.query(
                api_freq,
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
        else:
            df = pro.query(
                api_freq,
                ts_code=ts_code,
                start_date=start_date,
                end_date=end_date
            )
        
        if df is None or len(df) == 0:
            return None
        
        # 标准化列名
        df = df.rename(columns={
            'trade_date': 'datetime',
            'vol': 'volume'
        })
        
        # 转换日期格式
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # 按日期排序
        df = df.sort_values('datetime').reset_index(drop=True)
        
        # 选择需要的列
        columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount']
        df = df[columns]
        
        return df
    
    except ImportError:
        logger.error("未安装tushare，请执行：pip install tushare")
        raise
    except Exception as e:
        logger.error(f"Tushare获取数据失败：{str(e)}")
        raise


def _get_klines_from_akshare(
    stock_code: str,
    market: str,
    start_date: str,
    end_date: str,
    freq: str
) -> Optional[pd.DataFrame]:
    """
    从Akshare获取K线数据
    
    Args:
        stock_code: 股票代码
        market: 市场代码
        start_date: 开始日期
        end_date: 结束日期
        freq: K线频率
    
    Returns:
        K线数据DataFrame
    """
    try:
        import akshare as ak
        
        # 映射频率
        freq_map = {
            'D': 'daily',
            'W': 'weekly',
            'M': 'monthly',
            '5': '5',
            '15': '15',
            '30': '30',
            '60': '60'
        }
        
        api_freq = freq_map.get(freq, 'daily')
        
        # 获取数据
        if api_freq == 'daily':
            # 日线数据
            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"  # 前复权
            )
        elif api_freq == 'weekly':
            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period="weekly",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
        elif api_freq == 'monthly':
            df = ak.stock_zh_a_hist(
                symbol=stock_code,
                period="monthly",
                start_date=start_date,
                end_date=end_date,
                adjust="qfq"
            )
        else:
            # 分钟线数据
            df = ak.stock_zh_a_hist_min_em(
                symbol=stock_code,
                period=api_freq,
                adjust="qfq"
            )
        
        if df is None or len(df) == 0:
            return None
        
        # 标准化列名
        column_map = {
            '日期': 'datetime',
            '开盘': 'open',
            '最高': 'high',
            '最低': 'low',
            '收盘': 'close',
            '成交量': 'volume',
            '成交额': 'amount',
            '时间': 'datetime'
        }
        
        df = df.rename(columns=column_map)
        
        # 转换日期格式
        df['datetime'] = pd.to_datetime(df['datetime'])
        
        # 过滤日期范围
        start_dt = pd.to_datetime(start_date)
        end_dt = pd.to_datetime(end_date)
        df = df[(df['datetime'] >= start_dt) & (df['datetime'] <= end_dt)]
        
        # 按日期排序
        df = df.sort_values('datetime').reset_index(drop=True)
        
        # 选择需要的列
        columns = ['datetime', 'open', 'high', 'low', 'close', 'volume', 'amount']
        df = df[[col for col in columns if col in df.columns]]
        
        # 如果没有amount列，计算
        if 'amount' not in df.columns:
            df['amount'] = df['close'] * df['volume']
        
        return df
    
    except ImportError:
        logger.error("未安装akshare，请执行：pip install akshare")
        raise
    except Exception as e:
        logger.error(f"Akshare获取数据失败：{str(e)}")
        raise
