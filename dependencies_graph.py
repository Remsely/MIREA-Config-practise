import sys
import re
import requests
from graphviz import Digraph


def get_dependencies(package_name):
    dependencies = set()
    try:
        response = requests.get(f"https://pypi.org/pypi/{package_name}/json")
        if response.status_code == 200:
            data = response.json()
            info = data.get("info")
            requires_dist = info.get("requires_dist", [])

            for dist in requires_dist:
                if 'extra' not in dist:
                    dependency = extract_package_name(dist)
                    dependencies.add(dependency)
        else:
            print(f"Пакет {package_name} не найден на PyPI!")
            sys.exit(1)
    except Exception:
        print("", end="")

    return dependencies


def extract_package_name(dependency):

    match = re.match(r"([a-zA-Z0-9._-]+)", dependency)
    if match:
        return match.group(1).strip()
    return None


def create_dependency_graph(package_name):
    graph = Digraph(format='png')
    visited = set()

    def add_dependencies(package_name):
        dependencies = get_dependencies(package_name)
        for dependency in dependencies:
            if dependency not in visited:
                visited.add(dependency)
                graph.node(dependency)
                graph.edge(package_name, dependency)
                add_dependencies(dependency)

    graph.node(package_name)
    add_dependencies(package_name)
    return graph


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Incorrect arguments!")
        sys.exit(1)

    print("Running dependency_graph.py...")
    package_name = sys.argv[1]
    dependency_graph = create_dependency_graph(package_name)
    print(dependency_graph.source)
    dependency_graph.render('dependencies_graph')

