import pandas as pd
from ichi_api import D, W2


class Filter:
    def __init__(self, col1: str, col2: str):
        self.col1 = col1
        self.col2 = col2

    def get_values(self, df) -> tuple:
        i = -D if "CK" in [self.col1, self.col2] else -1
        return df.iloc[i][self.col1], df.iloc[i][self.col2]

    def analyze(self, df: pd.DataFrame, parameter: str) -> bool:
        return self.col1 == self.col2


class AboveBelowFilter(Filter):
    def __init__(self, col1: str, col2: str):
        super().__init__(col1, col2)

    def analyze(self, df: pd.DataFrame, parameter: str) -> bool:
        # value = 0 to below
        # value = 1 to above
        a, b = self.get_values(df)
        if (a >= b) == (parameter == "1"):
            return True
        return False


class DistanceFilter(Filter):
    def __init__(self, col1: str, col2: str, near: bool):
        super().__init__(col1, col2)
        self.near = near

    def analyze(self, df: pd.DataFrame, parameter: str) -> bool:
        n = float(parameter)    # distance in percentage
        a, b = self.get_values(df)
        if abs((a - b)/a) < n/100 == self.near:
            return True
        return False


class CloseFilter(Filter):
    def __init__(self, col1: str, col2: str):
        super().__init__(col1, col2)

    def analyze(self, df: pd.DataFrame, parameter: str) -> bool:
        days = int(parameter)
        for i in range(days):
            row = df.iloc[-i]
            if row[self.col1] > row[self.col2]:
                return False
        return True


class StockFilter:
    def __init__(self):
        self.k = 14

    def analyze(self, df: pd.DataFrame, parameter: str) -> bool:
        smin = df['LOW'].rolling(self.k).min()
        smax = df['HIGH'].rolling(self.k).max()
        stoch_k = 100 * (df['PRICE'] - smin) / (smax - smin)
        return stoch_k.iloc[-1] <= float(parameter)


class TwistFilter:
    def __init__(self):
        self.position = {'C': -D, 'D': -1}

    def analyze(self, df: pd.DataFrame, parameter: str) -> bool:
        options = parameter.split()
        for option in options:
            valid = False
            interval, ref = option[:-1], self.position[option[-1]]
            ref_index = df.index[ref]
            start, end = (int(i) for i in interval.split('-'))
            for i in range(start + ref_index, end + ref_index):
                nex = df.loc[i + 1 - W2]
                row = df.loc[i - W2]
                if (nex['SSAF'] > nex['SSBF']) != (row['SSAF'] > row['SSBF']):
                    valid = True
            if not valid:
                return False
        return True


FILTERS = {
    'F1': AboveBelowFilter("PRICE", "TK"),
    'F2': AboveBelowFilter("PRICE", "KJ"),
    'F3': AboveBelowFilter("PRICE", "SSA"),
    'F4': AboveBelowFilter("PRICE", "SSB"),
    'F5': AboveBelowFilter("TK", "KJ"),
    'F6': AboveBelowFilter("CK", "TK"),
    'F7': AboveBelowFilter("CK", "KJ"),
    'F8': AboveBelowFilter("CK", "PRICE"),
    'F9': AboveBelowFilter("CK", "SSA"),
    'F10': AboveBelowFilter("CK", "SSB"),
    'F11': AboveBelowFilter("KJ", "PRICE"),
    'F12': DistanceFilter("CK", "PRICE", False),
    'F13': DistanceFilter("PRICE", "SSB", True),
    'F14': StockFilter(),
    'F15': CloseFilter("PRICE", "KJ"),
    'F16': TwistFilter(),
    'F17': DistanceFilter("TK", "KJ", False)
}
