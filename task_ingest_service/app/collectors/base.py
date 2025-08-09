from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List
from ..schemas import CollectedItem


class Collector(ABC):
    id: str
    name: str
    interval_seconds: int

    @abstractmethod
    def collect(self) -> List[CollectedItem]:
        raise NotImplementedError