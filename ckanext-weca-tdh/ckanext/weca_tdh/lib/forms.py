import json
import os

_forms_cache = None


def load_forms():
    global _forms_cache
    if _forms_cache is None:
        path = os.path.join(os.path.dirname(__file__), "..", "config", "forms.json")
        with open(path, "r") as f:
            _forms_cache = json.load(f)
    return _forms_cache


def get_form(form_name):
    forms = load_forms()
    return next((f for f in forms if f["name"] == form_name), None)
