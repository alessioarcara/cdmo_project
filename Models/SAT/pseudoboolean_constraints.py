from z3 import *

def encode(lits, coeffs, rhs):
    simplified_lits = [] 
    simplified_coeffs = []
    result = []

    if rhs == 0:
        for i in range(len(lits)):
            result.append(Not(lits[i]))

    for i in range(len(lits)):
        if coeffs[i] <= rhs:
            simplified_lits.append(lits[i])
            simplified_coeffs.append(coeffs[i])
        else:
            result.append(Not(lits[i]))
            
    return simplified_lits, simplified_coeffs, result
    
def Pb_seq_counter(bool_vars, coeffs, k, name):
    bool_vars, coeffs, precondition = encode(bool_vars, coeffs, k)
    
    constraints = []
    n = len(bool_vars)
    seq_auxiliary = [[Bool(f"s_{name}_{i}_{j}") for j in range(k + 1)] for i in range(n + 1)]
    for i in range(1, n + 1):
        wi = coeffs[i - 1]
        for j in range(1, k + 1):
            if i >= 2 and i <= n and j <= k:
                constraints.append(Or(Not(seq_auxiliary[i - 1][j]), seq_auxiliary[i][j]))
            if i <= n and j <= wi:
                constraints.append(Or(Not(bool_vars[i - 1]), seq_auxiliary[i][j]))
            if i >= 2 and i <= n and j <= k - wi:
                constraints.append(Or(Not(seq_auxiliary[i - 1][j]), Not(bool_vars[i - 1]), seq_auxiliary[i][j + wi]))
        if i >= 2:
            constraints.append(Or(Not(seq_auxiliary[i - 1][k + 1 - wi]), Not(bool_vars[i - 1])))

    constraints.extend(precondition)
    return constraints

def Pb_adder_networks(bool_vars, coeffs, k):
    def ld_int(x):
        ld_return = 0
        for i in range(31):
            if (x & (1 << i)) > 0:
                ld_return = i + 1
        return ld_return
        
    def adder_tree(buckets, result):
        i = 0
        while i < len(buckets):
            if len(buckets[i]) == 0:
                i += 1
                continue
            if i == len(buckets) - 1 and len(buckets[i]) >= 2:
                buckets.append([])
                result.append(None)
            while len(buckets[i]) >= 3:
                x = buckets[i].pop(0)
                y = buckets[i].pop(0)
                z = buckets[i].pop(0)
                xs = fa_sum(x, y, z)
                xc = fa_carry(x, y, z)
                buckets[i].append(xs)
                buckets[i + 1].append(xc)
                fa_extra(xc, xs, x, y, z)
            if len(buckets[i]) == 2:
                x = buckets[i].pop(0)
                y = buckets[i].pop(0)
                buckets[i].append(ha_sum(x, y))
                buckets[i + 1].append(ha_carry(x, y))
            result[i] = buckets[i].pop(0)
            i += 1
            
    def num_to_bits(n, num):
        number = num
        bits = []
        for i in range(n - 1, -1, -1):
            tmp = 1 << i
            if number < tmp:
                bits.append(False)
            else:
                bits.append(True)
                number -= tmp
        bits.reverse()
        return bits

    def less_than_or_equal(xs, ys):
        assert len(xs) == len(ys)
        constraints = []
        for i in range(len(xs)):
            if ys[i] or xs[i] is None:
                continue
            clause = []
            skip = False
            for j in range(i + 1, len(xs)):
                if ys[j]:
                    if xs[j] is None:
                        skip = True
                        break
                    clause.append(Not(xs[j]))
                else:
                    if xs[j] is None:
                        continue
                    clause.append(xs[j])
            if skip:
                continue
            clause.append(Not(xs[i]))
            constraints.append(Or(clause))
        return constraints

    def fa_extra(xc, xs, a, b, c):
        formula.append(Or(Not(xc), Not(xs), a))
        formula.append(Or(Not(xc), Not(xs), b))
        formula.append(Or(Not(xc), Not(xs), c))
        formula.append(Or(xc, xs, Not(a)))
        formula.append(Or(xc, xs, Not(b)))
        formula.append(Or(xc, xs, Not(c)))

    def fa_carry(a, b, c):
        x = Bool(f"carry_{a}_{b}_{c}")
        formula.append(Or(b, c, Not(x)))
        formula.append(Or(a, c, Not(x)))
        formula.append(Or(a, b, Not(x)))
        formula.append(Or(Not(b), Not(c), x))
        formula.append(Or(Not(a), Not(c), x))
        formula.append(Or(Not(a), Not(b), x))
        return x

    def fa_sum(a, b, c):
        x = Bool(f"sum_{a}_{b}_{c}")
        formula.append(Or(a, b, c, Not(x)))
        formula.append(Or(a, Not(b), Not(c), Not(x)))
        formula.append(Or(Not(a), b, Not(c), Not(x)))
        formula.append(Or(Not(a), Not(b), c, Not(x)))
        formula.append(Or(Not(a), Not(b), Not(c), x))
        formula.append(Or(Not(a), b, c, x))
        formula.append(Or(a, Not(b), c, x))
        formula.append(Or(a, b, Not(c), x))
        return x

    def ha_carry(a, b):
        x = Bool(f"carry_{a}_{b}")
        formula.append(Or(a, Not(x)))
        formula.append(Or(b, Not(x)))
        formula.append(Or(Not(a), Not(b), x))
        return x

    def ha_sum(a, b):
        x = Bool(f"sum_{a}_{b}")
        formula.append(Or(Not(a), Not(b), Not(x)))
        formula.append(Or(a, b, Not(x)))
        formula.append(Or(Not(a), b, x))
        formula.append(Or(a, Not(b), x))
        return x

    bool_vars, coeffs, precondition = encode(bool_vars, coeffs, k)

    result = []
    formula = []
    buckets = []
    nb = ld_int(k)
    for iBit in range(nb):
        buckets.append([])
        result.append(None)
        for iVar in range(len(bool_vars)):
            if (1 << iBit) & coeffs[iVar] != 0:
                buckets[-1].append(bool_vars[iVar])
                
    adder_tree(buckets, result)
    kBits = num_to_bits(len(buckets), k)
    constraints = less_than_or_equal(result, kBits)
    formula.extend(constraints)
    formula.extend(precondition)
    return formula
