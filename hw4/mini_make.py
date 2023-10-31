import hashlib
import os
import json


# Функция для вычисления хеша содержимого файла
def calculate_hash(file_path):
    sha256 = hashlib.sha256()
    with open(f"files/{file_path}", 'rb') as f:
        while True:
            data = f.read(65536)  # Чтение блоками
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()


# Функция для парсинга файла и создания списка задач
def parse_makefile(filename):
    tasks = {}
    current_task = None

    with open(filename, 'r') as file:
        for line in file:

            if len(''.join(line.split())) == 0:
                continue

            if not line[0] == ' ' and not line[0] == "\t":
                # Новая задача
                task_name, deps = line.split(':')[0], line.split(':')[1].split()
                current_task = Task(task_name.strip(), [], deps)
                tasks[task_name] = current_task
            else:
                # Команда
                current_task.commands.append(line.lstrip().rstrip("\n"))

    return list(tasks.values())


# Класс, представляющий задачу сборки
class Task:
    def __init__(self, name, commands=None, dependencies=None):
        self.name = name
        self.commands = commands or []
        self.dependencies = dependencies or []
        self.output_hash = None

    def run(self, tasks):
        # Проверяем, нужно ли выполнить задачу
        if not self.should_run(tasks):
            return

        # Выполняем команду
        for command in self.commands:
            os.system(command)

        # Обновляем хеш вывода
        self.update_output_hash()

    def should_run(self, tasks):
        # Проверяем, нужно ли выполнить задачу
        if not self.output_hash or self.output_hash != calculate_hash(self.name):
            return True
        for dep in self.dependencies:
            if tasks[dep].output_hash is None or tasks[dep].output_hash != calculate_hash(tasks[dep].name):
                return True

        return False

    def update_output_hash(self):
        # Обновляем хеш вывода
        self.output_hash = calculate_hash(self.name)


# Класс, представляющий систему сборки
class BuildSystem:
    def __init__(self):
        self.tasks = {}

    def add_task(self, task):
        self.tasks[task.name] = task

    def build(self):
        # Создаем список всех задач
        all_tasks = list(self.tasks.values())

        # Выполняем топологическую сортировку
        sorted_tasks = []
        visited = set()

        def visit(task):
            if task.name not in visited:
                visited.add(task.name)
                for dep in task.dependencies:
                    if self.tasks[dep].name in self.tasks:
                        visit(self.tasks[dep])
                sorted_tasks.append(task)

        for t in all_tasks:
            visit(t)

        # Запускаем задачи в отсортированном порядке
        for t in reversed(sorted_tasks):
            t.run(self.tasks)

    # def topological_sort(self, task_name):
    #     sorted_tasks = []
    #     visited = set()
    #
    #     def visit(task):
    #         if task.name not in visited:
    #             visited.add(task.name)
    #             for dep in task.dependencies:
    #                 if dep.name in self.tasks:
    #                     visit(self.tasks[dep.name])
    #             sorted_tasks.append(task)
    #
    #     visit(self.tasks[task_name])
    #     return reversed(sorted_tasks)

    def save_state(self, state_file):
        # Сохраняем состояние системы сборки в JSON
        state = {}
        for task_name, task in self.tasks.items():
            state[task_name] = {
                "output_hash": task.output_hash
            }
        with open(state_file, 'w') as f:
            json.dump(state, f, indent=4)

    def load_state(self, state_file):
        # Загружаем состояние системы сборки из JSON
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                state = json.load(f)
                for task_name, task_state in state.items():
                    if task_name in self.tasks:
                        self.tasks[task_name].output_hash = task_state["output_hash"]


if __name__ == "__main__":
    # Создаем экземпляр системы сборки
    build_system = BuildSystem()

    # Создаем экземпляры задач
    makefile = parse_makefile('makefile')

    # Добавляем задачи в систему сборки
    for task in makefile:
        build_system.add_task(task)

    # Загружаем предыдущее состояние (если существует)
    build_system.load_state("database/build_state.json")

    # Запускаем сборку
    build_system.build()

    # Сохраняем состояние
    build_system.save_state("database/build_state.json")
