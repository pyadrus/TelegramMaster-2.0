import yaml

def load_translations():
    with open("src/locales/translations.yaml", "r", encoding="utf-8") as file:
        return yaml.safe_load(file)

translations = load_translations()