from decimal import Decimal

def simplify_balances(balances):
    """
    balances = list of dicts:
    [
      {"user_id": X, "balance": Decimal},
      ...
    ]
    """

    creditors = []
    debtors = []

    for b in balances:
        if b["balance"] > 0:
            creditors.append(
                {"user_id": b["user_id"], "amount": b["balance"]}
            )
        elif b["balance"] < 0:
            debtors.append(
                {"user_id": b["user_id"], "amount": -b["balance"]}
            )

    settlements = []

    i = j = 0
    while i < len(debtors) and j < len(creditors):
        debtor = debtors[i]
        creditor = creditors[j]

        pay = min(debtor["amount"], creditor["amount"])

        settlements.append({
            "from": debtor["user_id"],
            "to": creditor["user_id"],
            "amount": pay
        })

        debtor["amount"] -= pay
        creditor["amount"] -= pay

        if debtor["amount"] == 0:
            i += 1
        if creditor["amount"] == 0:
            j += 1

    return settlements
