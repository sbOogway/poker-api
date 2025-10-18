import sys
import argparse
import os

from jinja2 import Environment, FileSystemLoader

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="generate_crud_and_schema",
        description="Generate FastCRUD and basic schema from Model",
    )

    parser.add_argument("model", help="Model name, with Maiusc notation. example: User")

    args = parser.parse_args()

    env = Environment(loader=FileSystemLoader("templates/"))

    model_lower = args.model.lower()
    model = args.model

    crud_data = {
        "model_lower": model_lower,
        "model_upper": model
    }
    crud_path = f"src/app/crud/crud_{model_lower}.py"

    crud_template = env.get_template("crud_base.py.j2")

    crud_out = crud_template.render(crud_data)

    with open(crud_path, "w", encoding="utf-8") as f:
        f.write(crud_out)

    # os.system(f"cp templates/crud_base.py {crud_path}")
    # os.system(f"sed -i 's/base/{model_lower}/g'  {crud_path}")
    # os.system(f"sed -i 's/Base/{model}/g'  {crud_path}")

    print("debug")
