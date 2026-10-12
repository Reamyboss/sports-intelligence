from abc import ABC, abstractmethod


class BaseCollector(ABC):
    """Base class for all data collectors."""

    @abstractmethod
    async def collect(self):
        """Return raw data from a source."""
        raise NotImplementedError
