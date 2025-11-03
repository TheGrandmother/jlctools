from csv import DictReader
from tools.client import get_by_code
from tools.models import Component

import argparse

parser = argparse.ArgumentParser(
    prog="jlcbomcheck",
    description="WARNING: THIS DOES A LOT OF GUESSWORK, GIVES FALSE POSITVES!!!"
    "Cross references a kicad bom CSV against the JLC catalog to attempt to check that"
    "the selected components matches those placed on the board",
)

parser.add_argument(
    "-l",
    "--lcsc_key",
    help="The column label for the LCSC part code",
    default="LCSC Part Number",
)

parser.add_argument(
    "-m",
    "--min_stock",
    help="Throw error if stock levels are lower than this",
    default=0,
)

parser.add_argument(
    "-k",
    "--link",
    help="Print link to part on error",
    default=False,
    action="store_true",
)


parser.add_argument(
    "--lax",
    help="Laxer checks, only warns",
    default=False,
    action="store_true",
)

parser.add_argument("file_path", help="Path to the CSV file to check")

ohm = "Ω"


args = parser.parse_args()


def either_prefixes(s1, s2):
    return s1.startswith(s2) or s2.startswith(s1)


def basic_check(footprint, value, lcsc_part: Component, strict=False):
    errors = 0
    lax = False
    if footprint != lcsc_part.componentSpecificationEn:
        if (
            either_prefixes(lcsc_part.componentSpecificationEn, footprint)
        ) and args.lax:
            lax = True
        else:
            print(
                f"Footprint missmatch, {lcsc_part.componentCode} has a {lcsc_part.componentSpecificationEn} footprint but bom specifies {footprint}"
            )
            errors += 1
    if strict and value not in lcsc_part.componentModelEn:
        if (
            either_prefixes(lcsc_part.componentSpecificationEn, footprint)
        ) and args.lax:
            lax = True
        else:
            print(
                f"Model missmatch. {lcsc_part.componentModelEn} does not match BOM comment {value}"
            )
            errors += 1
    if not strict and value not in lcsc_part.describe:
        print(
            f"Component value of {value} not found in description: {lcsc_part.describe}"
        )
        errors += 1
    if errors != 0 and args.link:
        print(f"{lcsc_part.lcscGoodsUrl}")
    return (errors, lax)


def run():
    thing = DictReader(open(args.file_path))
    lcsc_key = args.lcsc_key
    errors = 0
    exotic = []
    lax_allowances = False
    checks = 0
    for row in thing:
        lcsc_code = row.get(lcsc_key, "").strip()
        if lcsc_code == "":
            continue

        if row.get("DNP", "") != "":
            continue

        part = get_by_code(lcsc_code)
        if part.stockCount <= args.min_stock:
            print(
                f"Component {lcsc_code} only has {part.stockCount} units in stock."
            )
            errors += 1
        elif part.stockCount <= len(row["Designator"].split(",")):
            print(
                f"Component {lcsc_code} requires that {len(row["Designator"].split(","))} units in stock."
            )
            errors += 1
        if not part.is_basic():
            exotic.append(part)

        value = row.get("Comment", "")

        [category, footprint] = row.get("Footprint", ":").split(":")
        new_errors = 0
        lax = 0
        match category.split("_")[0]:

            case "Resistor":
                checks += 1
                new_errors, lax = basic_check(
                    footprint.split("_")[1], value + ohm, part
                )
            case "Capacitor":
                checks += 1
                new_errors, lax = basic_check(
                    footprint.split("_")[1], value + "F", part
                )
            case "LED":
                checks += 1
                new_errors, lax = basic_check(
                    footprint.split("_")[1], value, part
                )

            case "Diode":
                checks += 1
                new_errors, lax = basic_check(
                    footprint.split("_")[1],
                    value,
                    part,
                    strict=True,
                )

            case "Package":
                checks += 1
                new_errors, lax = basic_check(
                    footprint.split("_")[0],
                    value,
                    part,
                    strict=True,
                )

            case "JLCPCB":
                pass

            case _:
                print(f"Unknown category {category}")
                pass
        errors += new_errors
        lax_allowances |= lax

    print(f"Checked {checks} rows")
    print(f"Found {errors} errors")
    if lax_allowances:
        print(f"Some errors were ignored due to laxness")

    if len(exotic) > 0:
        print(f"Found {len(exotic)} non basic parts:")
        for e in exotic:
            print(f"    {e.componentCode}: {e.componentName}")


if __name__ == "__main__":
    run()
