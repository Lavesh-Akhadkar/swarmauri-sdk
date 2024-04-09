from abc import ABC, abstractmethod
from typing import List, Any, Dict
from swarmauri.core.chains.IChainStep import IChainStep

class IChain(ABC):
    """
    Interface for managing execution chains within the system.
    """

    @abstractmethod
    def __init__(self, steps: List[IChainStep] = None, **configs):
        pass

    @abstractmethod
    def add_step(self, step: IChainStep):
        pass
    

    @abstractmethod
    def invoke(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    async def ainvoke(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    def batch(self, requests: List[Dict[str, Any]]) -> List[Any]:
        pass

    @abstractmethod
    async def abatch(self, requests: List[Dict[str, Any]]) -> List[Any]:
        pass

    @abstractmethod
    def stream(self, *args, **kwargs) -> Any:
        pass

    @abstractmethod
    def get_schema_info(self) -> Dict[str, Any]:
        pass