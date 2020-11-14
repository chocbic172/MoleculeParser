import re


def extract_ramifications(string):
    for a in string:
        d = [r.span() for r in re.finditer("(\[(?:\[??[^\[]*?\]))", a)]
        z = [a[:d[0][0]]]
        for i in range(len(d)):
            z.append(a[d[i][0]:d[i][1]])
            if i != len(d)-1: z.append(a[d[i][1]:d[i+1][0]])
        z.append(a[d[-1][1]:])
    if len([r for r in re.finditer("\[|\]", a)]) > 0: extract_ramifications(z)
    return z


print(re.split('\[|\]', "1,2-di[1-ethyl-3-[2-methyl]propyl]heptylcyclobutane") )
