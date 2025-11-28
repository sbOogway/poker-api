import argparse

from jinja2 import Environment, FileSystemLoader

env = Environment(loader=FileSystemLoader("templates/"))


def write_template_to_file(template_path, template_data, out_path):
    template = env.get_template(template_path)
    out = template.render(template_data)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(out)

    print(f"✅ written {out_path} succesfully")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="generate_crud_and_schema",
        description="Generate FastCRUD and basic schema from Model",
    )

    parser.add_argument("model", help="Model name, with Maiusc notation. example: User")

    parser.add_argument(
        "--api",
        default=False,
        action="store_true",
        help="Generates api route. Remember to add it to router in src/app/api/v1/__init__.py",
    )
    args = parser.parse_args()
    print(args)

    model_lower = args.model.lower()
    model = args.model

    data = {"model_lower": model_lower, "model_upper": model}
    crud_path = f"src/app/crud/crud_{model_lower}.py"

    schema_path = f"src/app/schemas/{model_lower}.py"

    write_template_to_file("base_crud.py.j2", data, crud_path)
    write_template_to_file("base_schema.py.j2", data, schema_path)

    if args.api:
        api_path = f"src/app/api/v1/{model_lower}.py"
        write_template_to_file("base_api.py.j2", data, api_path)
