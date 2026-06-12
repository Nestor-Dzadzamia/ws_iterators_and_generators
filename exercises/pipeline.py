from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Iterator


@dataclass(frozen=True)
class Order:
    id: int
    order_id: str
    customer_name: str
    customer_email: str
    product: str
    category: str
    amount: int
    unit_price: float
    order_date: str
    country: str
    status: str
    line_error: bool = False


class Orders:
    """Reusable iterable that produces a fresh iterator for every iteration."""

    def __init__(self, lines: Iterator[str]) -> None:
        self._lines: list[str] = list(lines)

    def __iter__(self) -> Iterator[Order]:
         return OrdersIterator(iter(self._lines))

class OrdersIterator:
    """Stateful iterator over CSV-like lines."""

    def __init__(self, lines: Iterator[str]) -> None:
        self._lines = lines
        self._cursor: int = 0
    
    def __iter__(self) -> OrdersIterator:
        return self
        
    @staticmethod
    def _line_parser(line: str, index: int) -> Order:
        try:
            parts = [p.strip() for p in line.strip().split(",")]
            if len(parts) != 10:
                raise ValueError(
                    f"expected 10 fields, got {len(parts)}"
                )
            (
                order_id, customer_name, customer_email, product, category,
                amount_s, unit_price_s, order_date, country, status,
            ) = parts
 
            return Order(
                id=index,
                order_id=order_id,
                customer_name=customer_name,
                customer_email=customer_email,
                product=product,
                category=category,
                amount=int(amount_s),
                unit_price=float(unit_price_s),
                order_date=order_date,
                country=country,
                status=status,
            )
 
        except Exception as exc:
            print(f"Parse error on line {index}: {exc} — raw: {line!r}")
            return Order(
                id=index,
                order_id="", customer_name="", customer_email="",
                product="", category="",
                amount=0, unit_price=0.0,
                order_date="", country="", status="",
                line_error=True,
            )

    def __next__(self) -> Order:
        while True:
            line = next(self._lines)

            if not line.strip():
                continue

            order = self._line_parser(line, self._cursor)

            if order.line_error and self._cursor == 0:
                continue

            self._cursor += 1
            return order
                
            
    

def paid_sales(orders: Orders) -> Iterator[Order]:
    """Yield only paid orders."""
    for order in orders:
        if not order.line_error and order.status.casefold() == 'paid':
            yield order

def above_threshold(
    orders: Iterable[Order],
    threshold: int,
) -> Iterator[Order]:
    """Yield only orders with an <price * amount> greater than or equal to threshold."""
    for order in orders:
        if order.amount * order.unit_price >= threshold:
            yield order


def report_all_sales(
    orders: Orders,
    threshold: int,
) -> tuple[int, float]:
    """Report total amount and total revenue for paid orders above threshold."""
    selected: list[Order] = list(
        above_threshold(paid_sales(orders), threshold=threshold)
    )
    total_order_count = len(selected)
    total_sum = sum(order.amount * order.unit_price for order in selected)
    return (total_order_count, total_sum)
