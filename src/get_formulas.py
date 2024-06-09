from configparser import ConfigParser
from parse_macroses import parse_macroses


def get_formulas(coin_id: str, config_file_path: str) -> dict:
    config = ConfigParser()
    config.read(config_file_path)

    formulas = {}
    for formula_key in config["formula"].keys():
        formula = config["formula"][formula_key]
        formula = parse_macroses(formula, coin_id, config_file_path)
        result = eval(formula)

        if result == "":
            result = 0


        if isinstance(result, float):
            if "e" in str(result):
                result = f"{result:.16f}"  

                if formula_key.startswith("*"):
                    formula_key = formula_key[1:]
            else:
                if formula_key.startswith("*"):
                    result = "{:,}".format(float(result))
                    formula_key = formula_key[1:]
        elif isinstance(result, int):
            if formula_key.startswith("*"):
                result = "{:,}".format(int(result))
                formula_key = formula_key[1:]

        result = str(result)

        while "." in result and (result.endswith("0") or result.endswith(".")):
            if result[-1] == ".":
                result = result[:-1]
                break
            elif result[-1] == "0":
                result = result[:-1]

        if result == "":
            result = 0

        formulas[formula_key] = result

    return formulas


if __name__ == "__main__":
    print(get_formulas("tron", "module-1.ini")["price_1h"])
