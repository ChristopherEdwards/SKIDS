class mFunctions:
    @staticmethod
    def mExtract(string,position):
        chars = list(string)
        return chars[position-1]
    @staticmethod
    def mFind(string,substring):
        f = string.index(substring)
        return f + 1
    @staticmethod
    def mPiece(string,separator,number=1):
        pieces = string.split(separator)
        return pieces[number-1]
            
