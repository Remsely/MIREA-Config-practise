import graphviz
import os
import sys

created_nodes = set()
global last_master_node


def build_graph(graph, branch_path):
    global last_master_node
    branch_file = open(branch_path, 'r', encoding='utf-8')
    current_git_branch = os.path.basename(branch_file.name)

    while True:
        commit_info = branch_file.readline()

        if not commit_info:
            break

        reformed_info = reform_commit_info(commit_info)

        commit_oneline_hash_from = reformed_info[0][:6]
        commit_oneline_hash_to = reformed_info[1][:6]

        if commit_oneline_hash_from == "000000":
            graph.node(commit_oneline_hash_to, label=get_node_label(reformed_info, current_git_branch))
            continue

        if commit_oneline_hash_to not in created_nodes:
            graph.node(commit_oneline_hash_to, label=get_node_label(reformed_info, current_git_branch))
            created_nodes.add(commit_oneline_hash_to)
            graph.edge(commit_oneline_hash_from, commit_oneline_hash_to)

            if current_git_branch == "master" or current_git_branch == "main":
                last_master_node = commit_oneline_hash_to

        commit_massage = reformed_info[6]

        if 'merge' in commit_massage:
            merged_branch = commit_massage.split()[1][:-1]
            merged_branch_path = branch_path[:branch_path.rfind('/') + 1] + merged_branch
            merged_branch_file = open(merged_branch_path, 'r', encoding='utf-8')

            for commit_info in merged_branch_file:
                reformed_info_ = reform_commit_info(commit_info)
                commit_oneline_hash_to_ = reformed_info_[1][:6]

                if commit_oneline_hash_to_ == commit_oneline_hash_to:
                    time = reformed_info_[4]
                    graph.node(time, label=get_node_label(reformed_info, current_git_branch))
                    created_nodes.add(commit_oneline_hash_to)

                    graph.edge(commit_oneline_hash_to_, time)
                    graph.edge(last_master_node, time)

                    last_master_node = time


def reform_commit_info(info):
    spited_info = info.replace('\t', '/').split('/')
    info = spited_info[0].split()
    info.append(spited_info[1][:-1])
    return info


def get_node_label(reformed_info, current_git_branch):
    commit_massage = reformed_info[6]
    commit_oneline_hash = reformed_info[1][:6]
    return f"{current_git_branch}\n{commit_massage}\n{commit_oneline_hash}"


def render_graph(path):
    graph_code = graphviz.Digraph('Graph')
    for branch in os.listdir(path):
        branch_path = path + "/" + branch

        if os.path.isfile(branch_path):
            build_graph(graph_code, branch_path)

    graph_code.format = "png"
    graph_code.render("commits_graph", view=False)


if __name__ == "__main__":
    branches_path = ''.join(sys.argv[1:]).replace("\\", "/") + '/.git/logs/refs/heads'
    render_graph(branches_path)
