class Evaluator:
    def __init__(self, expression):
        self._expression = expression

    def evaluate(self, context, exp=None):
        exp = exp if exp else self._expression
        if type(exp).__name__ == "VariableName":
            return context.get(exp.name)
        elif isinstance(exp, (int, float)):
            return exp
        elif isinstance(exp, str):
            return exp
        elif hasattr(exp, "op"):
            if isinstance(exp.right, list):
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
