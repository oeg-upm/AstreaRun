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

    statements = fid_content.split('> .\n')  # list of statements without '> .' at the end
    # print(statements)
    graph_labels = []

    for i in range(len(statements)-1):
        string = statements[i] + '> .'  # complete statement
        string_words = string.split()
        # print(len(string_words))
        graph_label = string_words[-2]
        graph_labels.append(graph_label)
        graph_labels = list(dict.fromkeys(graph_labels))  # list of all graph labels

    # print(graph_labels)
    # print(len(graph_labels))

    os.chdir(onto_dir)

    for i in range(len(statements)-1):
        statement = statements[i] + '> .\n'
        statement_words = statement.split()
        index = statement_words[-2]
        index = index.replace("/", "")  # '/' not allowed in folder's name
        f = open(index + '.nq', 'a')  # create ontology_name.nq files and append the corresponding statements
        f.write(statement)
        f.close()


def run_astrea():

    url = 'https://astrea.linkeddata.es/api/shacl/document'

    with open('test.nq', 'r') as file:  # testing response for one ontology
        content = file.read()
        # print(content)
        input_file = {'ontology': content, 'serialisation': 'N-Quads'}
        print(input_file)
        x = requests.post(url, json=input_file)
        print(x)

    # for filename in os.listdir(onto_dir):  # response for all ontologies
    #    os.chdir(onto_dir)
    #    with open(filename, 'r') as file:
    #        content = file.read()
    #    print(content)
    #    input_file = {'ontology': content, 'serialisation': 'N-quads'}
    #    print(input_file)
    #    x = requests.post(url, json=input_file)
    #    print(x)
    #    path_parent = os.path.dirname(os.getcwd())
    #    os.chdir(path_parent)

    # put all resulting files in Shapes folder with matching names


def main():

    # create_folders(clean=True)  # input clean value = True to erase previous ontology and shapes folders
    # before creating the new ones

    # divide('lov.nq')  # input filename to divide = "lov.nq" or "test.nq"...

    run_astrea()  # automatically generate shape files from all vocabularies with Astrea
    # not implemented yet


if __name__ == '__main__':
    main()
