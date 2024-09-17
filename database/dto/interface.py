from typing import List, Dict
from abc import abstractclassmethod


class InterfaceDTO:

    @abstractclassmethod
    async def all(self) -> List[Dict]:
        raise NotImplementedError("Method not implemented!")

    @abstractclassmethod
    async def get(self, id: int) -> Dict:
        raise NotImplementedError("Method not implemented!")
    
    @abstractclassmethod
    async def filter(self, **kwargs) -> List[Dict]:
        raise NotImplementedError("Method not implemented!")
    
    @abstractclassmethod
    async def delete(self, id: int) -> Dict:
        raise NotImplementedError("Method not implemented!")