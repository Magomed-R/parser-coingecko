""" 
? Подставление формул в текст:
* Поочерёдная замена формул
* Возвращение изменённого текста
"""


def parse_text(text, formulas) -> str:
    is_formula = False
    curr_formula = ""
    formula_end = 0

    for c in range(len(text)-1, -1, -1):
        if text[c] == "}":
            is_formula = True
            formula_end = c
            continue
            
        if text[c] == "{":
            is_formula = False

            text = text[0:c] + str(formulas[curr_formula]) + text[formula_end+1:]
            curr_formula = ""

        if is_formula:
            curr_formula = text[c] + curr_formula
    
    return text

if __name__ == "__main__":
    print(parse_text("Тест {test_formula}\nother formula {price}", {"test_formula": 111, "price": 1000}))