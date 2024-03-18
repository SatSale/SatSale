from abc import ABC, abstractmethod
from decimal import Decimal
from typing import Tuple


class node(ABC):

    def __init__(self, node_config: dict, is_onchain: bool) -> None:
        self.config = node_config
        self.is_onchain = is_onchain

    @abstractmethod
    def get_info(self):
        pass

    @abstractmethod
    def get_address(self, amount: Decimal, label: str,
                    expiry: int) -> Tuple[str, str, str]:
        pass

    @abstractmethod
    def check_payment(self, uuid: str) -> Tuple[Decimal, Decimal]:
        pass
