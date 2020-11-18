import re


RADICALS = ["meth", "eth", "prop", "but",   "pent",  "hex",  "hept",  "oct",  "non",  "dec",  "undec",  "dodec",  "tridec",  "tetradec",  "pentadec",  "hexadec",  "heptadec",  "octadec",  "nonadec"]
SUFFIX = ["ol", "al", "one", "oic acid", "carboxylic acid", "oate", "ether", "amide", "amine", "imine", "benzene", "thiol", "phosphine", "arsine"]

MULTIPLIERS = ["undef", "di",  "tri",  "tetra", "penta", "hexa", "hepta", "octa", "nona", "deca", "undeca", "dodeca", "trideca", "tetradeca", "pentadeca", "hexadeca", "heptadeca", "octadeca", "nonadeca"]
PREFIXES = ["cyclo", "hydroxy", "oxo", "carboxy", "oxycarbonyl", "anoyloxy", "formyl", "oxy", "amido", "amino", "imino", "phenyl",  "mercapto", "phosphino", "arsino", "fluoro", "chloro", "bromo", "iodo"]


pattern = "(" + "|".join([x for x in sorted(RADICALS, key=len, reverse=True)] + [x for x in sorted(SUFFIX+MULTIPLIERS+PREFIXES, key=len, reverse=True)]) + ")"


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
        self.functions = []

    def __str__(self):
        return self.type + ":" + self.name

    def complete_structure(self):
        return self.structure + [item for sublist in (structure.complete_structure() for structure in self.ramifications) for item in sublist] + self.functions

    def add_ramification(self, r):
        for pos in enumerate(r):
            if pos[1].type == "ALKYL" and r[pos[0]-1].type == "MULTIPLIER":
                if pos[0] >= 2 and r[pos[0]-2].type != "POSITION": positions = ["1" for x in range(MULTIPLIERS.index(r[pos[0]-1].name)+1)]
                else: positions = r[pos[0]-2].name.split(",")
                for pos in positions:
                    self.structure[int(pos)] = self.structure[int(pos)][:2] + str(int(self.structure[int(pos)][2:])-1)

    def decode(self, radical, positions=None, multiplier="undef"):
        self.structure = ["CH3"] + ["CH2" for x in range(RADICALS.index(radical.name)-1)] + ["CH3"]
        if positions is None: positions = ["1" for x in range(MULTIPLIERS.index(multiplier)+1)]
        if self.type in ["ALKANE", "ALKYL"]:
            if radical.name == "meth": self.structure = ["CH4"]
        elif self.type in ["ALKENE", "ALKYNE"]:
            a = (1 if self.type == "ALKENE" else 2)
            for pos in positions:
                self.structure[int(pos)-1] = self.structure[int(pos)-1][:2] + str(int(self.structure[int(pos)-1][2:])-a)
                self.structure[int(pos)] = self.structure[int(pos)][:2] + str(int(self.structure[int(pos)][2:])-a)
        self.name = multiplier + radical.name + self.name if multiplier != "undef" else radical.name + self.name

    def add_function(self, function, positions=None, multiplier="undef"):
        print("ADDING FUNCTION: " + function.name)
        if positions is None: positions = ["1" for x in range(MULTIPLIERS.index(multiplier)+1)]
        if function.name == "ol":
            for pos in positions:
                self.structure[int(pos)-1] = self.structure[int(pos)-1][:2] + str(int(self.structure[int(pos)-1][2:])-1)
                self.functions.append("OH")


def process_ramifications(_list):
    for item in enumerate(_list):
        for subitem in enumerate(item[1]):
            if subitem[1].type == "ALKYL" and subitem[0] == 0:
                if _list[item[0]-2][-1].type in ["POSITION", "MULTIPLIER"]:
                    subitem[1].ramifications = _list[item[0]-1]
                    subitem[1].add_ramification(_list[item[0]-1])
                    _list[item[0]] = _list[item[0]-2] + _list[item[0]]
                    del(_list[item[0]-2], _list[item[0]-2])
                    return _list


def tokenize(string):
    string = re.split("\[|\]", string)
    tokenized = []
    for item in string:
        tokenized += [([x for x in re.split(pattern, item) if x != ""])]

    tokenized = [(list(filter(None, a.split("-"))) for a in z) for z in tokenized]
    tokenized = [[item for sublist in a for item in sublist] for a in tokenized]

    for item in enumerate(tokenized):
        tokenized[item[0]] = [Token(x) for x in item[1]]

    for z in tokenized:
        # First pass - Creates hydrocarbon backbone
        for item in enumerate(z):
            if item[1].type in ["ALKANE", "ALKENE", "ALKYNE"]:
                # Combine elements
                if z[item[0]-1].type == "RADICAL": item[1].decode(z[item[0]-1])
                elif z[item[0]-1].type == "MULTIPLIER": item[1].decode(z[item[0]-3], z[item[0]-2].name.split(","), z[item[0]-1].name)
                elif z[item[0]-1].type == "POSITION": item[1].decode(z[item[0]-2], z[item[0]-1].name.split(","))

                # Clean up combined elements
                if z[item[0]-1].type == "POSITION": del(z[item[0]-1], z[item[0]-2])
                elif z[item[0]-1].type == "MULTIPLIER": del(z[item[0]-1], z[item[0]-2], z[item[0]-3])
                else: del(z[item[0]-1])
            elif item[1].type == "ALKYL":
                if z[item[0]-1].type == "RADICAL":
                    # Initial grouping of ramification backbone
                    item[1].decode(z[item[0]-1])
                    del(z[item[0]-1])

    # Seconds pass - Processing subramifications
    while len(tokenized) > 1: tokenized = process_ramifications(tokenized)
    tokenized = tokenized[0]

    # Third pass - prefixes and suffixes
    for item in enumerate(tokenized):
        if item[1].type == "SUFFIX":
            print("FOUND SUFFIX")
            if tokenized[item[0]-1].type in ["ALKANE", "ALKENE", "ALKYNE"]: tokenized[item[0]-1].add_function(item[1])
            elif tokenized[item[0]-1].type == "POSITION": tokenized[item[0]-2].add_function(item[1], tokenized[item[0]-1].name.split(","))
            elif tokenized[item[0]-1].type == "MULTIPLIER":
                if tokenized[item[0]-2].type == "POSITION": tokenized[item[0]-3].add_function(item[1], tokenized[item[0]-2].name.split(","), tokenized[item[0]-1].name)
                else: tokenized[item[0]-3].add_function(item[1], multiplier=tokenized[item[0]-1].name)

            if tokenized[item[0]-1].type in ["ALKANE", "ALKENE", "ALKYNE"]: del(tokenized[item[0]])
            elif tokenized[item[0]-1].type == "POSITION": del(tokenized[item[0]], tokenized[item[0]-1])
            elif tokenized[item[0]-1].type == "MULTIPLIER":
                if tokenized[item[0]-2].type == "POSITION": del(tokenized[item[0]], tokenized[item[0]-1], tokenized[item[0]-2])
                else: del(tokenized[item[0]], tokenized[item[0]-1])



    print([z.type for z in tokenized])
    print([z.name for z in tokenized])
    print(tokenized[0].complete_structure())

    # Forming Ramifications
    # for item in enumerate(tokenized):
    #     if item[1].type == "POSITION":
    #         if [x for x in tokenized[] if x.type == "ALKYL"]


if __name__ == "__main__":
    print(tokenize("hexan-2,3-diol"))
