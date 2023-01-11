R_BEGIN = 1.8
R_END = 1.748
POS_END = 90
POS_BEGIN = 10
print(R_END)

def to_machine(real):
    r = R_BEGIN - (R_BEGIN - R_END) * (real / (POS_END - POS_BEGIN))
    print(r)
    return real * r