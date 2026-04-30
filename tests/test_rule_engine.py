from app.services.rule_engine import RuleEngine


def test_rule_expression_true():
    context = {"amount": 7000, "country": "GB", "user_home_country": "US", "balance": 5000}
    assert RuleEngine._eval_expression("amount > 5000 and country != user_home_country", context)


def test_rule_expression_false_for_bad_syntax():
    context = {"amount": 7000}
    assert RuleEngine._eval_expression("amount >>> 500", context) is False
