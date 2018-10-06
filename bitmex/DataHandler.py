class Orderbook(object): 
    def __init__(self, symbol=None, bid1=None, bid1vol=None, ask1=None, ask1vol=None, timestamp=None):
        self.symbol = symbol
        self.bid1 = bid1
        self.bid1vol = bid1vol
        self.ask1 = ask1
        self.ask1vol = ask1vol
        self.timestamp = timestamp
        
    def __repr__(self):
        return self.__dict__.__repr__()
        

class Tick(object): 
    def __init__(self, symbol=None, price=None, volume=None, direction=None, timestamp=None):
        self.symbol = symbol
        self.price = price
        self.volume = volume
        self.direction = direction
        self.timestamp = timestamp
        
    def __repr__(self):
        return self.__dict__.__repr__()


class Bar(object):
    pass


class Snapshot(object):
    pass


from bitmexWSMarket2 import bitmexWSMarket2
from bitmexREST import bitmexREST
from utils import generate_logger, calculate_td_ts
import queue
import threading


class bitmexDataHandler(object):
    def __init__(self, g):
        self.g = g                            # global settings
        self.symbols = g.symbols              # 订阅的标的  ['XBTUSD', ...]
        self.market_data_q = queue.Queue()    # MarketData队列（带数据）        
        self.active = False
        self.logger = generate_logger('DataHandler', g.loglevel, g.logfile)  # 日志
        
    def add_event_q(self, event_q):
        self.event_q = event_q                # 全局事件队列
        
    def run(self):
        self.__construct_bm_ws_market()
        self.td = threading.Thread(target=self.__run)
        self.active = True
        self.td.start()


    def __run(self):  
        while self.active:
            try:
                data = self.market_data_q.get(timeout=10)
            except queue.Empty:
                self.logger.warning('no data in market_data_q for 10 seconds')
            else:
                if isinstance(data, Tick):
                    self.processTick(data)
                elif isinstance(data, Orderbook):
                    self.processOrderbook(data)
                else:
                    self.logger.warning('Invalid data type from market_data_q: %s' % data.__class__)
    
    def stop(self):
        self.logger.info('Stopping DataHandler ...')
        self.bm_ws_market.exit()
        if True:
            self.logger.info('Exiting Thread: _DataHandler.__run(), wait for less than 10 secs')
            self.active = False
            self.td.join()
        self.logger.info('DataHandler stopped')

        
    def __construct_bm_ws_market(self):
        self.bm_ws_market = bitmexWSMarket2(apiKey=None, apiSecret=None, 
                                            is_test=self.g.is_test, loglevel=self.g.loglevel, logfile=self.g.logfile)
        self.bm_ws_market.connect()
        self.bm_ws_market.add_market_data_q(self.market_data_q)
        for s in self.symbols:
            self.bm_ws_market.subscribe(s, trade=True, orderbook=True)
        self.bm_ws_market.wait_for_data()
        

    def processTick(self, tick):
        self.logger.debug('💛 Processing Tick... %s' % tick)
        self.event_q.put(tick)   # temp, for test
        
        # 1. 更新tick(last_price)
        self.__update_tick(tick)
        
        # 2. if 该symbol订阅了tick事件，推送（全局事件队列）
        if False:
            self.__push_tick_event(tick.symbol)
        
        # 3. 生成bar
        self.__bar(tick)
        
    def __update_tick(self, tick):
        pass
    
    def __push_tick_event(self):
        pass
    
    def __bar(self, tick):
        pass
    
    def processOrderbook(self, ob):
        self.logger.debug('✡️ Processing Orderbook... %s' % ob)
        self.event_q.put(ob)    # temp, for test
        
        # 1. 更新Orderbook
        self.__update_orderbook(ob)
        
        # 2. if 该symbol订阅了orderbook事件，推送（全局事件队列）
        if False:
            self.__push_orderbook_event(tick.symbol)
        
    def __update_orderbook(self, ob):
        pass
    
    def __push_orderbook_event(self, symbol):
        pass
    
    def register_bar_event(self, symbol, bar_type):
        pass
    
    def snapshot(self, symbol):
        """参照国内期货快照数据结构"""
        pass
    
    