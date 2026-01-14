from datetime import datetime


class Guess:
    def __init__(self, mot: str, timestamp: datetime):
        self.mot = mot
        self.timestamp = timestamp
        self.id = 0
    
    def correctionGuess(self, mot: str) -> str:
        pass
