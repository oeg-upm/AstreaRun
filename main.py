#!/usr/bin/env python

import os
import shutil
import requests

onto_dir = 'Ontologies'
shapes_dir = 'Shapes'


def create_folders(clean):

    if clean:
        if os.path.isdir(onto_dir):
            shutil.rmtree(onto_dir)
        if os.path.isdir(shapes_dir):
            shutil.rmtree(shapes_dir)

    if not os.path.exists(onto_dir):
        os.mkdir(onto_dir)
    if not os.path.exists(shapes_dir):
        os.mkdir(shapes_dir)


def divide(filename):

    with open(filename, 'r') as fid:
        fid_content = fid.read()
        # fid_content = fid_content.replace("\\", "\\\\")  # escape \
        # fid_content = fid_content.replace("\"", "\\\"")  # escape "

    statements = fid_content.split('> .\n')  # list of statements without '> .' at the end
    graph_labels = []
    for i in range(len(statements)-1):
        string = statements[i] + '> .'  # complete statement
        string_words = string.split()
        graph_label = string_words[-2]
        graph_labels.append(graph_label)
        graph_labels = list(dict.fromkeys(graph_labels))  # list of all graph labels
    # print(graph_labels)
    # print(len(graph_labels))  # number of vocabularies in file

    os.chdir(onto_dir)
    for i in range(len(statements)-1):
        statement = statements[i] + '> .\n'
        statement_words = statement.split()
        index = statement_words[-2]
        index = index.replace("/", "")  # '/' not allowed in folder's name
        f = open(index + '.nq', 'a')  # create ontology_name.nq files and append the corresponding statements
        f.write(statement)
        f.close()
    path_parent = os.path.dirname(os.getcwd())
    os.chdir(path_parent)


def convert_triple(filename):

    if filename != 'all':
        with open(filename, 'r') as file:
            content = file.read()
        statements = content.split('> .\n')
        for i in range(len(statements) - 1):
            string = statements[i] + '> .\n'
            words = string.split()
            graph_label = words[-2]
            string = string.replace(graph_label + " .\n", "")
            string = string + '.\n'
            with open(graph_label.replace("/", "") + '.nt', 'a') as file:
                file.write(string)

    if filename == 'all':
        for filename in os.listdir(onto_dir):
            os.chdir(onto_dir)
            with open(filename, 'r') as file:
                content = file.read()
            statements = content.split('> .\n')
            for i in range(len(statements) - 1):
                string = statements[i] + '> .\n'
                words = string.split()
                graph_label = words[-2]
                string = string.replace(graph_label + " .\n", "")
                string = string + '.\n'
                with open(graph_label.replace("/", "") + '.nt', 'a') as file:
                    file.write(string)
            path_parent = os.path.dirname(os.getcwd())
            os.chdir(path_parent)


def run_astrea(ontofile):

    url = 'https://astrea.linkeddata.es/api/shacl/document'

    if ontofile != 'all':
        with open(ontofile, 'r') as file:
            content = file.read()
        headers = {"content-type": "application/json"}
        input_file = {"ontology": content, "serialisation": "N-Triples"}
        x = requests.post(url, json=input_file, headers=headers)
        os.chdir(shapes_dir)
        with open(ontofile.replace(".nt", "")+'shape.ttl', 'w') as file:
            file.write(x.content.decode())
        path_parent = os.path.dirname(os.getcwd())
        os.chdir(path_parent)

    if ontofile == 'all':
        for filename in os.listdir(onto_dir):
            if filename.endswith('.nt'):
                os.chdir(onto_dir)
                with open(filename, 'r') as file:
                    content = file.read()
                headers = {"content-type": "application/json"}
                input_file = {"ontology": content, "serialisation": "N-Triples"}
                x = requests.post(url, json=input_file, headers=headers)
                path_parent = os.path.dirname(os.getcwd())
                os.chdir(path_parent)
                os.chdir(shapes_dir)
                with open(filename.replace(".nt", "") + 'shape.ttl', 'w') as file:
                    file.write(x.content.decode())
                path_parent = os.path.dirname(os.getcwd())
                os.chdir(path_parent)


def main():

    create_folders(clean=True)
    # input value clean = True to erase previous ontology and shapes folder before creating the new ones

    divide('lov.nq')
    # input filename to divide = "lov.nq" or "test.nq"...

    convert_triple(filename='all')
    # converts input file .nq to .nt (main.py folder level) or all files with ='all' (Ontologies folder)

    run_astrea(ontofile='all')
    # automatically generate shape files from filename or 'all' vocabularies with Astrea (same folder logic as above)


if __name__ == '__main__':
    main()
