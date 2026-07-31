from abc import ABC, abstractmethod


class ServiceClass(ABC):
    @abstractmethod
    def invoke(self, *args, **kwargs):
        pass
