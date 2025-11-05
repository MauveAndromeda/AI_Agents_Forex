"""
Order Execution Module for MT5
Handles order placement, modification, and position management
"""

import MetaTrader5 as mt5
from typing import Optional, Dict, Tuple
from enum import Enum
import logging
from dataclasses import dataclass

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OrderType(Enum):
    """Order types"""
    BUY = mt5.ORDER_TYPE_BUY
    SELL = mt5.ORDER_TYPE_SELL
    BUY_LIMIT = mt5.ORDER_TYPE_BUY_LIMIT
    SELL_LIMIT = mt5.ORDER_TYPE_SELL_LIMIT
    BUY_STOP = mt5.ORDER_TYPE_BUY_STOP
    SELL_STOP = mt5.ORDER_TYPE_SELL_STOP


@dataclass
class OrderResult:
    """Order execution result"""
    success: bool
    order_id: Optional[int]
    price: Optional[float]
    error_code: Optional[int]
    error_message: Optional[str]
    comment: str = ""


class MT5OrderExecutor:
    """
    Handles order execution for MT5
    Includes slippage protection and retry logic
    """

    def __init__(self, magic_number: int = 234000, max_retries: int = 3):
        """
        Initialize order executor

        Args:
            magic_number: Magic number for order identification
            max_retries: Maximum retry attempts for failed orders
        """
        self.magic_number = magic_number
        self.max_retries = max_retries

    def place_market_order(self,
                          symbol: str,
                          order_type: OrderType,
                          lot_size: float,
                          stop_loss: Optional[float] = None,
                          take_profit: Optional[float] = None,
                          comment: str = "",
                          max_slippage: int = 10) -> OrderResult:
        """
        Place market order

        Args:
            symbol: Trading symbol
            order_type: BUY or SELL
            lot_size: Position size in lots
            stop_loss: Stop loss price
            take_profit: Take profit price
            comment: Order comment
            max_slippage: Maximum acceptable slippage in points

        Returns:
            OrderResult
        """
        # Get current price
        tick = mt5.symbol_info_tick(symbol)
        if tick is None:
            return OrderResult(
                success=False,
                order_id=None,
                price=None,
                error_code=None,
                error_message=f"Failed to get tick for {symbol}"
            )

        # Set price based on order type
        price = tick.ask if order_type == OrderType.BUY else tick.bid

        # Prepare request
        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": symbol,
            "volume": lot_size,
            "type": order_type.value,
            "price": price,
            "deviation": max_slippage,
            "magic": self.magic_number,
            "comment": comment,
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        # Add SL/TP if provided
        if stop_loss is not None:
            request["sl"] = stop_loss
        if take_profit is not None:
            request["tp"] = take_profit

        # Execute order with retries
        for attempt in range(self.max_retries):
            result = mt5.order_send(request)

            if result is None:
                logger.warning(f"Order attempt {attempt + 1} failed: No result")
                continue

            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"Order executed: {symbol} {order_type.name} "
                          f"{lot_size} lots @ {result.price}")
                return OrderResult(
                    success=True,
                    order_id=result.order,
                    price=result.price,
                    error_code=None,
                    error_message=None,
                    comment=f"Executed at {result.price}"
                )

            logger.warning(f"Order attempt {attempt + 1} failed: "
                         f"Code {result.retcode}, {result.comment}")

        # All attempts failed
        return OrderResult(
            success=False,
            order_id=None,
            price=None,
            error_code=result.retcode if result else None,
            error_message=result.comment if result else "Unknown error"
        )

    def modify_position(self,
                       ticket: int,
                       stop_loss: Optional[float] = None,
                       take_profit: Optional[float] = None) -> OrderResult:
        """
        Modify existing position SL/TP

        Args:
            ticket: Position ticket number
            stop_loss: New stop loss price
            take_profit: New take profit price

        Returns:
            OrderResult
        """
        # Get position info
        position = mt5.positions_get(ticket=ticket)
        if position is None or len(position) == 0:
            return OrderResult(
                success=False,
                order_id=None,
                price=None,
                error_code=None,
                error_message=f"Position {ticket} not found"
            )

        position = position[0]

        request = {
            "action": mt5.TRADE_ACTION_SLTP,
            "symbol": position.symbol,
            "position": ticket,
            "magic": self.magic_number,
        }

        if stop_loss is not None:
            request["sl"] = stop_loss
        else:
            request["sl"] = position.sl

        if take_profit is not None:
            request["tp"] = take_profit
        else:
            request["tp"] = position.tp

        result = mt5.order_send(request)

        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info(f"Position {ticket} modified: SL={request['sl']}, TP={request['tp']}")
            return OrderResult(
                success=True,
                order_id=ticket,
                price=None,
                error_code=None,
                error_message=None,
                comment="Position modified"
            )

        return OrderResult(
            success=False,
            order_id=ticket,
            price=None,
            error_code=result.retcode if result else None,
            error_message=result.comment if result else "Unknown error"
        )

    def close_position(self, ticket: int, lot_size: Optional[float] = None) -> OrderResult:
        """
        Close position

        Args:
            ticket: Position ticket number
            lot_size: Partial close size (None for full close)

        Returns:
            OrderResult
        """
        # Get position info
        positions = mt5.positions_get(ticket=ticket)
        if positions is None or len(positions) == 0:
            return OrderResult(
                success=False,
                order_id=None,
                price=None,
                error_code=None,
                error_message=f"Position {ticket} not found"
            )

        position = positions[0]

        # Determine close volume
        volume = lot_size if lot_size else position.volume

        # Determine close type (opposite of position type)
        close_type = mt5.ORDER_TYPE_SELL if position.type == mt5.ORDER_TYPE_BUY else mt5.ORDER_TYPE_BUY

        # Get current price
        tick = mt5.symbol_info_tick(position.symbol)
        if tick is None:
            return OrderResult(
                success=False,
                order_id=None,
                price=None,
                error_code=None,
                error_message=f"Failed to get tick for {position.symbol}"
            )

        price = tick.bid if close_type == mt5.ORDER_TYPE_SELL else tick.ask

        request = {
            "action": mt5.TRADE_ACTION_DEAL,
            "symbol": position.symbol,
            "volume": volume,
            "type": close_type,
            "position": ticket,
            "price": price,
            "deviation": 10,
            "magic": self.magic_number,
            "comment": "Close position",
            "type_time": mt5.ORDER_TIME_GTC,
            "type_filling": mt5.ORDER_FILLING_IOC,
        }

        result = mt5.order_send(request)

        if result and result.retcode == mt5.TRADE_RETCODE_DONE:
            logger.info(f"Position {ticket} closed: {volume} lots @ {result.price}")
            return OrderResult(
                success=True,
                order_id=ticket,
                price=result.price,
                error_code=None,
                error_message=None,
                comment=f"Closed at {result.price}"
            )

        return OrderResult(
            success=False,
            order_id=ticket,
            price=None,
            error_code=result.retcode if result else None,
            error_message=result.comment if result else "Unknown error"
        )

    def close_all_positions(self, symbol: Optional[str] = None) -> Dict[int, OrderResult]:
        """
        Close all positions

        Args:
            symbol: Close positions for specific symbol (None for all)

        Returns:
            Dict of ticket -> OrderResult
        """
        positions = mt5.positions_get(symbol=symbol) if symbol else mt5.positions_get()

        if positions is None or len(positions) == 0:
            logger.info("No positions to close")
            return {}

        results = {}
        for position in positions:
            result = self.close_position(position.ticket)
            results[position.ticket] = result

        return results

    def get_open_positions(self, symbol: Optional[str] = None) -> list:
        """Get all open positions"""
        positions = mt5.positions_get(symbol=symbol) if symbol else mt5.positions_get()
        return list(positions) if positions else []

    def get_position_info(self, ticket: int) -> Optional[Dict]:
        """Get position information"""
        positions = mt5.positions_get(ticket=ticket)
        if positions is None or len(positions) == 0:
            return None

        pos = positions[0]
        return {
            'ticket': pos.ticket,
            'symbol': pos.symbol,
            'type': 'BUY' if pos.type == mt5.ORDER_TYPE_BUY else 'SELL',
            'volume': pos.volume,
            'price_open': pos.price_open,
            'price_current': pos.price_current,
            'sl': pos.sl,
            'tp': pos.tp,
            'profit': pos.profit,
            'swap': pos.swap,
            'comment': pos.comment,
        }


# Example usage
if __name__ == "__main__":
    if not mt5.initialize():
        print("MT5 initialization failed")
    else:
        executor = MT5OrderExecutor()

        # Example: Place buy order
        # result = executor.place_market_order(
        #     symbol="EURUSD",
        #     order_type=OrderType.BUY,
        #     lot_size=0.01,
        #     stop_loss=1.0800,
        #     take_profit=1.0900,
        #     comment="Test order"
        # )
        # print(f"Order result: {result}")

        # Get open positions
        positions = executor.get_open_positions()
        print(f"Open positions: {len(positions)}")

        mt5.shutdown()
