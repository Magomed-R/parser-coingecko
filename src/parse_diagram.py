"""
? Парсинг диаграммы:
* Поочерёдная замена формул
* Расчёт значения диаграммы
* Возвращение значения
"""

from typing import Dict


def parse_diagram(diagram: str, formulas: Dict) -> int:
    is_formula = False
    curr_formula = ""
    formula_end = 0

    for c in range(len(diagram) - 1, -1, -1):
        if diagram[c] == "}":
            is_formula = True
            formula_end = c
            continue

        if diagram[c] == "{":
            is_formula = False

            diagram = (
                diagram[0:c] + str(formulas[curr_formula]) + diagram[formula_end + 1 :]
            )
            curr_formula = ""

        if is_formula:
            curr_formula = diagram[c] + curr_formula

    return eval(diagram)


if __name__ == "__main__":
    print(
        parse_diagram(
            "({price_1h} - {price_0h}) * 100", {"price_1h": 100, "price_0h": 98}
        )
    )
