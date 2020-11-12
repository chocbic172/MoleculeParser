import re


RADICALS = ["meth", "eth", "prop", "but",   "pent",  "hex",  "hept",  "oct",  "non",  "dec",  "undec",  "dodec",  "tridec",  "tetradec",  "pentadec",  "hexadec",  "heptadec",  "octadec",  "nonadec"]
SUFFIX = ["ol", "al", "one", "oic acid", "carboxylic acid", "oate", "ether", "amide", "amine", "imine", "benzene", "thiol", "phosphine", "arsine"]

MULTIPLIERS = ["undef", "di",  "tri",  "tetra", "penta", "hexa", "hepta", "octa", "nona", "deca", "undeca", "dodeca", "trideca", "tetradeca", "pentadeca", "hexadeca", "heptadeca", "octadeca", "nonadeca"]
PREFIXES = ["cyclo", "hydroxy", "oxo", "carboxy", "oxycarbonyl", "anoyloxy", "formyl", "oxy", "amido", "amino", "imino", "phenyl",  "mercapto", "phosphino", "arsino", "fluoro", "chloro", "bromo", "iodo"]


pattern = "(" + "|".join([x for x in RADICALS[::-1]+SUFFIX+MULTIPLIERS+PREFIXES]) + ")"


class Token:
    def __init__(self, string):
        self.name = string
        self.type = "RADICAL" if string in RADICALS else "SUFFIX" if string in SUFFIX else "MULTIPLIER" if string in \
                    MULTIPLIERS else "PREFIX" if string in PREFIXES else "UNDEFINED"

        if self.type == "UNDEFINED":
            if self.name in ["an", "ane"]: self.type = "ALKANE"
            elif self.name in ["en", "ene"]: self.type = "ALKENE"
            elif self.name in ["yne"]: self.type = "ALKYNE"
            elif self.name in ["yl"]: self.type = "ALKYL"
            else: self.type = "POSITION"

        self.structure = []
        self.ramifications = []

    def __str__(self):
        return self.type + ":" + self.name

    def decode(self, radical, positions=None, multiplier="undef"):
        self.structure = self.structure = ["CH3"] + ["CH2" for x in range(RADICALS.index(radical.name)-1)] + ["CH3"]
        if positions is None: positions = ["1" for x in range(MULTIPLIERS.index(multiplier)+1)]
        if self.type == "ALKANE":
            if radical.name == "meth": self.structure = ["CH4"]
        elif self.type in ["ALKENE", "ALKYNE"]:
            a = (1 if self.type == "ALKENE" else 2)
            for pos in positions:
                self.structure[int(pos)-1] = self.structure[int(pos)-1][:2] + str(int(self.structure[int(pos)-1][2:])-a)
                self.structure[int(pos)] = self.structure[int(pos)][:2] + str(int(self.structure[int(pos)][2:])-a)


def extract_ramifications(tokens):
    for item in enumerate(tokens):
        if item[1].type == "ALKYL":
            b, c = 0, 0
            for i in enumerate(list("1,2-di[1-ethyl-3-[2-methyl]propyl]heptylcyclobutane")):
                if i[1] == "[": b += 1
                if i[1] == "[" and b == 0:
                    b += 1
                    c = i[0]
                if i[1] == "]": b -= 1
                print(b)
                if i[1] == "]" and b == 0: print(str(i[0]),str(c))


def tokenize(string):
    string = string.split("-")
    tokenized = []
    for item in string:
        tokenized += ([x for x in re.split(pattern, item) if x != ""])

    for item in enumerate(tokenized):
        tokenized[item[0]] = Token(item[1])

    types = [a.name for a in tokenized]

    print(types)

    # First pass - Creates hydrocarbon backbone
    for item in enumerate(tokenized):
        if item[1].type in ["ALKANE", "ALKENE", "ALKYNE"]:
            # Combine elements
            if tokenized[item[0]-1].type == "RADICAL": item[1].decode(tokenized[item[0]-1])
            elif tokenized[item[0]-1].type == "MULTIPLIER": item[1].decode(tokenized[item[0]-3], tokenized[item[0]-2].name.split(","), tokenized[item[0]-1].name)
            elif tokenized[item[0]-1].type == "POSITION": item[1].decode(tokenized[item[0]-2], tokenized[item[0]-1].name.split(","))

            # Clean up combined elements
            if tokenized[item[0]-1].type == "POSITION": del(tokenized[item[0]-1], tokenized[item[0]-2])
            elif tokenized[item[0]-1].type == "MULTIPLIER": del(tokenized[item[0]-1], tokenized[item[0]-2], tokenized[item[0]-3])
            else: del(tokenized[item[0]-1])

    types = [a.type for a in tokenized]
    print(types)
    print(tokenized[0].structure)

    # Forming Ramifications
    # for item in enumerate(tokenized):
    #     if item[1].type == "POSITION":
    #         if [x for x in tokenized[] if x.type == "ALKYL"]


if __name__ == "__main__":
    print(tokenize("1,2-di[1-ethyl-3-[2-methyl]propyl]heptylcyclobutane"))
