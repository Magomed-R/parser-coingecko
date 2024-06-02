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

        if isinstance(result, float):
            result = f"{result:.16f}"
            result = result.rstrip("0.")

            if formula_key.startswith("*"):
                result = "{:,}".format(float(result))
                formula_key = formula_key[1:]
        else:
            if formula_key.startswith("*"):
                result = "{:,}".format(int(result))
                formula_key = formula_key[1:]

        result = result.rstrip("0.")
        formulas[formula_key] = result

    return formulas

if __name__ == "__main__":
    print(get_formulas("tron", "module-1.ini"))