try:
    import MetaTrader5 as mt5
except ImportError:
    from . import mock_metatrader5 as mt5

class TradeExecutor:
    def __init__(self, mt5_connection):
        self.mt5 = mt5_connection

    def execute_trade(self, symbol, trade_type, volume, price, sl, tp, comment=""):
        """
        Executes a trade on the MT5 terminal.
        """
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": trade_type,
            "price": price,
            "sl": sl,
            "tp": tp,
            "deviation": 20,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = self.mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order send failed, retcode={result.retcode}")
            return None

        print(f"Order sent successfully, order ticket: {result.order}")
        return result

    def close_trade(self, ticket):
        """
        Closes a trade on the MT5 terminal.
        """
        position_info = self.mt5.positions_get(ticket=ticket)
        if position_info is None or len(position_info) == 0:
            print(f"No position found with ticket {ticket}")
            return False

        position = position_info[0]

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": position.volume,
            "type": mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY,
            "position": position.ticket,
            "deviation": 20,
            "magic": 234000,
            "comment": "Closing trade",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = self.mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Close order failed, retcode={result.retcode}")
            return False

        print(f"Position {ticket} closed successfully.")
        return True
