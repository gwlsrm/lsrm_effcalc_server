from abc import ABC, abstractmethod

from utils.speparser import Spectrum

class IMCA(ABC):
    """MCA interface"""
    @abstractmethod
    def start(self) -> None:
        """Start spectrum acquiring"""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stop spectrum acquiring"""
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear spectrum"""
        pass

    @abstractmethod
    def get_data(self) -> Spectrum:
        """Get acquired spectrum"""
        pass

    @abstractmethod
    def is_running(self) -> bool:
        """Is spectrum acquiring"""
        pass

    @abstractmethod
    def get_channels(self) -> int:
        """get channel number"""
        pass