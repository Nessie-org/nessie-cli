from nessie_api.models import FilterExpression, FilterOperator


class Evaluator:
    def __init__(self, expression):
        self._expression = expression

    def _find_variables(self):
        variables = set()

        def _find_variables_recursive(exp):
            if type(exp).__name__ == "VariableName":
                variables.add(exp.name)
            elif hasattr(exp, "left"):
                _find_variables_recursive(exp.left)
                if hasattr(exp, "right") and exp.right is not None:
                    if isinstance(exp.right, list):
                        for e in exp.right:
                            _find_variables_recursive(e)
                    else:
                        _find_variables_recursive(exp.right)

        _find_variables_recursive(self._expression)
        return variables

    def simple_evaluate(self) -> list[FilterExpression]:
        if type(self._expression).__name__ == "AndExpression":
            left = self.simple_evaluate_comparison(self._expression.left)
            ret = None
            if isinstance(self._expression.right, list):
                right = [
                    self.simple_evaluate_comparison(e) for e in self._expression.right
                ]
                ret = [left] + right
            else:
                right = self.simple_evaluate_comparison(self._expression.right)
                ret = [left, right]
            return ret
        elif type(self._expression).__name__ == "ComparisonExpression":
            return [self.simple_evaluate_comparison(self._expression)]
        else:
            raise NotImplementedError(
                f"Simple evaluation not implemented for {type(self._expression)}"
            )

    def simple_evaluate_comparison(self, exp) -> FilterExpression:
        left = exp.left
        right = exp.right
        op = self._str_to_op(exp.op)
        return FilterExpression(left, op, right)

    def evaluate(self, context, exp=None):
        exp = exp if exp is not None else self._expression
        if type(exp).__name__ == "VariableName":
            try:
                return context[exp.name]
            except KeyError as e:
                raise ValueError(f"Variable '{exp.name}' not found in context") from e
        elif isinstance(exp, (int, float)):
            return exp
        elif isinstance(exp, str):
            return exp
        elif hasattr(exp, "op"):
            if hasattr(exp, "right") and isinstance(exp.right, list):
                right_vals = [self.evaluate(context, e) for e in exp.right]
                return self._eval_recursive(
                    self.evaluate(context, exp.left), right_vals, exp.op
                )
            else:
                left_val = self.evaluate(context, exp.left)
                right_val = (
                    self.evaluate(context, exp.right) if hasattr(exp, "right") else None
                )
            op = exp.op
            return self._eval_recursive(left_val, right_val, op)
        else:
            raise NotImplementedError(f'Expression type "{type(exp)}" not supported')

    def _eval_recursive(self, lhs, rhs, op):
        if isinstance(rhs, list):
            for i in range(len(rhs)):
                lhs = self._eval_operation(op, lhs, rhs[i])
            return lhs
        else:
            return self._eval_operation(op, lhs, rhs)

    def _str_to_op(self, op) -> FilterOperator:
        if op == "==":
            return FilterOperator.EQ
        elif op == "!=":
            return FilterOperator.NEQ
        elif op == ">":
            return FilterOperator.GT
        elif op == "<":
            return FilterOperator.LT
        elif op == ">=":
            return FilterOperator.GTE
        elif op == "<=":
            return FilterOperator.LTE

    def _eval_operation(self, op, left_val, right_val):
        if op == "==":
            return left_val == right_val
        elif op == "!=":
            return left_val != right_val
        elif op == ">":
            return left_val > right_val
        elif op == "<":
            return left_val < right_val
        elif op == ">=":
            return left_val >= right_val
        elif op == "<=":
            return left_val <= right_val
        elif op == "&&":
            return left_val and right_val
        elif op == "||":
            return left_val or right_val
        elif op == "+":
            return left_val + right_val
        elif op == "-":
            return left_val - right_val
        elif op == "*":
            return left_val * right_val
        elif op == "/":
            return left_val / right_val
        elif op == "!":
            return not left_val
        else:
            raise NotImplementedError(f"Operator {op} not implemented")
