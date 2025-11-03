import ast
import importlib.util
import importlib.util
import os
import subprocess
import sys
import yaml

from Files import run_cmd


def export_conda_env():
    run_cmd("conda env export > packages.yml")


def create_exe(filename):
    cmd = "pyinstaller {} --onefile".format(filename)
    os.system("cmd /k \"{}\"".format(cmd))


def install_requirements(path_to_python_exe=None, _input="requirements.txt"):
    path = "--python " + path_to_python_exe + " " if path_to_python_exe is not None else ""
    cmd = "pip {}install -r {}".format(path, _input)
    run_cmd(cmd)


def upgrade_requirements(path_to_python_exe=None, _input="requirements.txt"):
    path = "--python " + path_to_python_exe + " " if path_to_python_exe is not None else ""
    cmd = "pip {}install -r {} --upgrade".format(path, _input)
    run_cmd(cmd)


def computer_name():
    import platform
    return platform.node()


def get_pid():
    return os.getpid()


def is_docker() -> bool:
    import os
    return os.path.exists('/.dockerenv')


def get_os() -> str:
    import platform
    if platform.system() == 'Darwin':
        return 'mac'
    elif platform.system() == 'Linux':
        return 'linux'
    elif platform.system() == 'Windows':
        return 'windows'
    else:
        raise NotImplementedError(f'Unsupported OS: "{platform.system()}"')


# def export_requirements(path_to_python_exe=None, output="requirements"):
#     path = "--python " + path_to_python_exe + " " if path_to_python_exe is not None else ""
#     cmd = "pip {}freeze > {}".format(path, output)
#     run_cmd(cmd)

def export_current_requirements():
    """Creates environment files using pip and conda commands."""
    os.makedirs('packages', exist_ok=True)

    # Generate requirements.txt
    output = subprocess.check_output(['pip', 'freeze']).decode('utf-8')
    lines = [l.strip() for l in output.splitlines() if l.strip() and not l.startswith('#')]
    reqs = [l.split('@')[0].strip() if '@' in l else l for l in lines]
    print("requirements.txt")
    with open('packages/requirements.txt', 'w') as f:
        f.write('\n'.join(reqs) + '\n')

    # Generate environment.yml
    try:
        result = subprocess.run(["conda", "env", "export"], capture_output=True, text=True, check=True)
        print("environment.yml")
        with open("packages/environment.yml", "w") as f:
            f.write('\n'.join(result.stdout.splitlines()[:-1]) + '\n')
    except subprocess.CalledProcessError as e:
        print(f"Error creating environment.yml: {e}")

    # Generate Dockerfile
    print("Dockerfile")
    with open('packages/Dockerfile', 'w') as f:
        f.write(
            'FROM continuumio/miniconda3\nWORKDIR /app_windows\nCOPY environment.yml .\nRUN conda env create -f environment.yml\nSHELL ["conda", "run", "-n", "myenv", "/bin/bash", "-c"]\nCOPY . .\nCMD ["conda", "run", "-n", "myenv", "python", "app_windows.py"]')

    # Generate Pipfile
    print("Pipfile")
    with open('packages/Pipfile', 'w') as f:
        pipfile = '[[source]]\nurl = "https://pypi.org/simple"\nverify_ssl = true\nname = "pypi"\n\n[packages]\n'
        pipfile += ''.join(f'{r.split("==")[0]} = "=={r.split("==")[1]}"\n' if '==' in r else f'{r} = "*"\n' for r in reqs)
        pipfile += '[dev-packages]\n\n[requires]\npython_version = "3.8"'
        f.write(pipfile)

    # Generate setup.py
    print("setup.py")
    with open('packages/setup.py', 'w') as f:
        f.write(f'from setuptools import setup\nsetup(name="my_package", version="0.1", packages=["my_package"], install_requires={reqs})')

    # Generate pyproject.toml
    print("pyproject.toml")
    with open('packages/pyproject.toml', 'w') as f:
        toml = '[tool.poetry]\nname = "my_package"\nversion = "0.1.0"\nauthors = ["Your Name <you@example.com>"]\n\n[tool.poetry.dependencies]\npython = "^3.8"\n'
        toml += '\n'.join(f'{r.split("==")[0]} = "^{r.split("==")[1]}"' if '==' in r else f'{r} = "*"' for r in reqs)
        toml += '\n\n[build-system]\nrequires = ["poetry-core"]\nbuild-backend = "poetry.core.masonry.api"'
        f.write(toml)


def export_script_requirements(script_path=__file__, superset_yml=None):
    r""" export_script_requirements(r"A:\Pycharm\Scrapping\test.py", r"A:\Pycharm\Util\packages\environment.yml") """
    processed = set()
    superset_packages = []

    # Load superset YAML with package specifications
    if superset_yml and os.path.exists(superset_yml):
        with open(superset_yml, 'r') as f:
            superset_data = yaml.safe_load(f)
            for item in superset_data.get('dependencies', []):
                if isinstance(item, dict) and 'pip' in item:
                    for pip_pkg in item['pip']:
                        pkg_name = pip_pkg.split('==')[0].split('@')[0]
                        superset_packages.append({
                            'name': pkg_name,
                            'spec': pip_pkg,
                            'source': 'pip'
                        })
                elif isinstance(item, str):
                    pkg_name = item.split('==')[0].split('@')[0]
                    superset_packages.append({
                        'name': pkg_name,
                        'spec': item,
                        'source': 'conda'
                    })

    def _find_best_match(module_name):
        candidates = []
        for pkg in superset_packages:
            if module_name in pkg['name']:
                candidates.append(pkg)
        if not candidates:
            return None
        # Select longest matching package name (most specific match)
        return max(candidates, key=lambda x: len(x['name']))

    def _export_script_requirements(script_path, processed):
        script_dir = os.path.dirname(os.path.abspath(script_path))

        with open(script_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(), filename=script_path)

        class ImportVisitor(ast.NodeVisitor):
            def __init__(self):
                self.imports = set()

            def visit_Import(self, node):
                for alias in node.names:
                    self.imports.add(alias.name.split('.')[0])

            def visit_ImportFrom(self, node):
                if node.module is not None:
                    self.imports.add(node.module.split('.')[0])

        visitor = ImportVisitor()
        visitor.visit(tree)
        initial_imports = visitor.imports

        conda_packages = set()
        pip_packages = set()
        queue = []

        def is_stdlib_module(module_name):
            return module_name in sys.stdlib_module_names

        def is_personal_module(origin):
            if not origin:
                return False
            return ('site-packages' not in origin) and ('dist-packages' not in origin)

        # Process initial imports
        for module in initial_imports:
            if not is_stdlib_module(module) and module not in processed:
                queue.append(module)

        while queue:
            current_module = queue.pop(0)
            if current_module in processed:
                continue
            processed.add(current_module)

            # Check for superset matches
            matched_pkg = _find_best_match(current_module)
            if matched_pkg:
                if matched_pkg['source'] == 'conda':
                    conda_packages.add(matched_pkg['spec'])
                else:
                    pip_packages.add(matched_pkg['spec'])
                continue

            # Standard package resolution
            spec = importlib.util.find_spec(current_module)
            if not spec:
                conda_packages.add(current_module)
                continue

            if is_personal_module(spec.origin):
                # Recursive processing for local modules
                module_file = spec.origin
                try:
                    sub_conda, sub_pip = _export_script_requirements(module_file, processed)
                    conda_packages.update(sub_conda)
                    pip_packages.update(sub_pip)
                except Exception as e:
                    conda_packages.add(current_module)
            else:
                conda_packages.add(current_module)

        return conda_packages, pip_packages

    # Create output directory
    packages_dir = 'packages'
    os.makedirs(packages_dir, exist_ok=True)

    # Generate package lists
    conda_pkgs, pip_pkgs = _export_script_requirements(script_path, processed)

    # Write YAML file
    yaml_path = os.path.join(packages_dir, 'script.yml')
    with open(yaml_path, 'w') as f:
        f.write("name: myenv\n")
        f.write("channels:\n  - defaults\n")
        f.write("dependencies:\n")

        # Always include pip as a conda dependency if we have pip packages
        if pip_pkgs:
            f.write("  - pip\n")

        # Write conda packages
        for pkg in sorted(conda_pkgs):
            f.write(f"  - {pkg}\n")

        # Write pip packages if any
        if pip_pkgs:
            f.write("  - pip:\n")
            for pkg in sorted(pip_pkgs):
                f.write(f"    - {pkg}\n")

if __name__ == '__main__':
    export_conda_env()
    # export_requirements(r"A:\Programmes\Python\Python3.11\python.exe",
    #                     r"B:\_Documents\Pycharm\Util\util_requirements.txt")
    # install_requirements(r"A:\Programmes\Python\Python3.11\python.exe",
    #                      r"B:\_Documents\Pycharm\Util\util_requirements.txt")
    # upgrade_requirements(r"A:\Programmes\Python\Python3.11\python.exe",
    #                      r"B:\_Documents\Pycharm\Util\util_requirements.txt")
    # print(encrypt_string(""))
    # export_current_requirements()
    # export_script_requirements(r"/PlayrightBrowser.py", r"A:\Pycharm\Util\packages\environment.yml")
    # conda env create --name temp --file script.yml
