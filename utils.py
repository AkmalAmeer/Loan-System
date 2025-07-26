def calculate_interest(p, n, r):
    return (p * n * r) / 100

def calculate_total_amount(p, interest):
    return p + interest

def calculate_emi(a, n):
    return round(a / (n * 12), 2)
