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


def tokenize(string):
    string = ['1,2-di', '1-ethyl-3-', '2-methyl', 'propyl', 'heptylcyclobutane']
    tokenized = []
    for item in string:
        tokenized += [([x for x in re.split(pattern, item) if x != ""])]

    tokenized = [(a.split("-")[0] for a in z) for z in tokenized]

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

    print([[a.type for a in z] for z in tokenized])
    print([[a.name for a in z] for z in tokenized])
    print(tokenized[-1][-1].structure)

    # Forming Ramifications
    # for item in enumerate(tokenized):
    #     if item[1].type == "POSITION":
    #         if [x for x in tokenized[] if x.type == "ALKYL"]


if __name__ == "__main__":
    print(tokenize("1,2-dimethylethane"))
