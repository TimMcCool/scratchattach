"""Abstract class for all classes describing a Scratch entity, like Session, Project etc.
In v2, all of these classes are inheriting from this abstract class"""

from abc import ABC, abstractmethod

class AbstractScratch(ABC):

    def update(self):
        """
        Updates the attributes of the object. Returns True if the update was successful.
        """
        response = self.update_function(
            self.update_API,
            headers = self._headers,
            cookies = self._cookies, timeout=10
        )
        # Check for 429 error:
        if "429" in str(response):
            return "429"
        if response.text == '{\n  "response": "Too many requests"\n}':
            return "429"
        # If no error: Parse JSON:
        response = response.json()
        return self._update_from_dict(response)
    
    @abstractmethod
    def _update_from_dict(self, data) -> bool:
        pass
