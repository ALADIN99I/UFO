try:
    import MetaTrader5 as mt5
except ImportError:
    from . import mock_metatrader5 as mt5

class TradeExecutor:
    def __init__(self, mt5_connection):
        self.mt5_connection = mt5_connection

    def execute_trade(self, symbol, trade_type, volume, price, sl, tp, comment=""):
        """
        Executes a trade on the MT5 terminal.
        """
        if not self.mt5_connection.connect():
            return None

        # Get symbol info to check minimum stop level
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            print(f"Failed to get symbol info for {symbol}")
            return None
        
        # Get current tick data
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            print(f"Failed to get tick data for {symbol}")
            return None
        
        # Calculate minimum distances for stops
        stops_level = symbol_info.trade_stops_level
        point = symbol_info.point
        min_distance = stops_level * point
        
        # Validate stop loss and take profit placement logic
        if trade_type == mt5.ORDER_TYPE_BUY:
            # For BUY: SL should be below entry, TP should be above entry
            if sl > 0 and sl > price:
                print(f"Error: BUY trade SL ({sl}) is above entry price ({price}) - should be below")
                return None
            if tp > 0 and tp < price:
                print(f"Error: BUY trade TP ({tp}) is below entry price ({price}) - should be above")
                return None
        else:
            # For SELL: SL should be above entry, TP should be below entry
            if sl > 0 and sl < price:
                print(f"Error: SELL trade SL ({sl}) is below entry price ({price}) - should be above")
                return None
            if tp > 0 and tp > price:
                print(f"Error: SELL trade TP ({tp}) is above entry price ({price}) - should be below")
                return None

        # Adjust stop loss and take profit if they're too close
        current_price = tick.ask if trade_type == mt5.ORDER_TYPE_BUY else tick.bid
        
        adjusted_sl = sl
        adjusted_tp = tp
        
        if trade_type == mt5.ORDER_TYPE_BUY:
            # For BUY: SL must be below current price by min_distance, TP above
            if sl > 0 and (current_price - sl) < min_distance:
                adjusted_sl = current_price - min_distance
                print(f"Adjusted SL from {sl} to {adjusted_sl} (min distance: {min_distance})")
            if tp > 0 and (tp - current_price) < min_distance:
                adjusted_tp = current_price + min_distance
                print(f"Adjusted TP from {tp} to {adjusted_tp} (min distance: {min_distance})")
        else:
            # For SELL: SL must be above current price by min_distance, TP below
            if sl > 0 and (sl - current_price) < min_distance:
                adjusted_sl = current_price + min_distance
                print(f"Adjusted SL from {sl} to {adjusted_sl} (min distance: {min_distance})")
            if tp > 0 and (current_price - tp) < min_distance:
                adjusted_tp = current_price - min_distance
                print(f"Adjusted TP from {tp} to {adjusted_tp} (min distance: {min_distance})")

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": volume,
            "type": trade_type,
            "price": price,
            "sl": adjusted_sl,
            "tp": adjusted_tp,
            "deviation": 50,
            "magic": 234000,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Order send failed, retcode={result.retcode}")
            return None

        print(f"Order sent successfully, order ticket: {result.order}")
        self.mt5_connection.disconnect()
        return result

    def execute_portfolio(self, trades):
        """
        Executes a portfolio of trades.
        """
        results = []
        for trade in trades:
            result = self.execute_trade(
                symbol=trade['symbol'],
                trade_type=trade['trade_type'],
                volume=trade['volume'],
                price=trade['price'],
                sl=trade['sl'],
                tp=trade['tp'],
                comment=trade.get('comment', '')
            )
            results.append(result)
        return results

    def close_all_trades(self):
        """
        Closes all open trades.
        """
        if not self.mt5_connection.connect():
            return False

        positions = mt5.positions_get()
        if positions is None:
            print("No positions found.")
            return True

        for position in positions:
            self.close_trade(position.ticket)

        self.mt5_connection.disconnect()
        return True

    def close_trade(self, ticket):
        """
        Closes a trade on the MT5 terminal.
        """
        if not self.mt5_connection.connect():
            return False

        position_info = mt5.positions_get(ticket=ticket)
        if position_info is None or len(position_info) == 0:
            print(f"No position found with ticket {ticket}")
            self.mt5_connection.disconnect()
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

        result = mt5.order_send(request)

        if result.retcode != mt5.TRADE_RETCODE_DONE:
            print(f"Close order failed, retcode={result.retcode}")
            self.mt5_connection.disconnect()
            return False

        print(f"Position {ticket} closed successfully.")
        self.mt5_connection.disconnect()
        return True
