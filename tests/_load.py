"""Load a tool script from the canonical skill tree (folder names have hyphens)."""

import importlib.util
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = os.path.join(ROOT, ".agents", "skills")


def load(folder, name):
    path = os.path.join(SKILLS, folder, name + ".py")
    spec = importlib.util.spec_from_file_location("clonekit_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
