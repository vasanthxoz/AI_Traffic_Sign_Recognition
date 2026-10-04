"""
rules.py - IF-THEN rule engine (forward chaining)
-------------------------------------------------
Rules are plain data:
    {"rule_id": ..., "if": [{"field","op","value"}, ...], "then": {...}, "text": ...}
The engine repeatedly fires every rule whose IF-conditions hold for the
current facts, adds the THEN-part to the facts, and stops when nothing new
can fire.  Example chain:
    SIGN-STOP  ->  status=RECOGNIZED, instruction
    CAT-PRIORITY -> group=Regulatory
    GROUP-REGULATORY -> legal_note
"""
OPS = {
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "in": lambda a, b: a in b,
}


def condition_holds(cond, facts):
    value = facts.get(cond["field"])
    return value is not None and OPS[cond["op"]](value, cond["value"])


def infer(facts, rules):
    """Return (final_facts, fired_rules)."""
    facts, fired, done = dict(facts), [], set()
    changed = True
    while changed:
        changed = False
        for r in rules:
            if r["rule_id"] in done:
                continue
            if all(condition_holds(c, facts) for c in r["if"]):
                done.add(r["rule_id"])
                fired.append(r)
                facts.update(r["then"])
                changed = True
    return facts, fired
