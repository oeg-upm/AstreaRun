#!/usr/bin/env python

import os
import shutil
import requests
import rdflib
import rdfextras
rdfextras.registerplugins()

onto_dir = 'Ontologies'
shapes_dir = 'Shapes'


def create_folders(clean):

    if clean:
        print('Cleaning folders...')
        if os.path.isdir(onto_dir):
            shutil.rmtree(onto_dir)
        if os.path.isdir(shapes_dir):
            shutil.rmtree(shapes_dir)

    if not os.path.exists(onto_dir):
        os.mkdir(onto_dir)
    if not os.path.exists(shapes_dir):
        os.mkdir(shapes_dir)
    print('Folders ready')


def divide(filename):

    print('Dividing file...')
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
    print('File successfully divided')


def convert_triple(filename):

    print('Converting quads to triples...')
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
    print('Conversion successfully concluded')


def run_astrea(ontofile):

    url = 'https://astrea.linkeddata.es/api/shacl/document'

    print('Running Astrea...')
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
    print('Shapes built successfully')


def analysis(shape):

    shape_number = 0
    count_subjects = 0
    count_predicates = 0
    count_objects = 0
    count_total_shapeaxioms = 0
    count_total_nodeshape = 0
    count_total_propertyshape = 0
    count_total_maxcount = 0
    count_total_mincount = 0
    count_total_nodekind = 0
    count_total_path = 0
    count_total_label = 0
    count_total_datatype = 0
    count_total_description = 0
    count_total_maxinclusive = 0
    count_total_mininclusive = 0
    count_total_pattern = 0
    count_total_class = 0
    count_total_targetclass = 0
    count_total_not = 0
    count_total_property = 0

    if shape != 'all':
        print('Shape analysis...')
        for filename in os.listdir(shapes_dir):
            if filename == shape:
                os.chdir(shapes_dir)
                g = rdflib.Graph()
                g.parse(filename, format="turtle")
                # print(g.serialize(format="turtle").decode("utf-8"))

                shape_size = g.query("""
                    SELECT (COUNT (?p) AS ?count)
                    WHERE {
                    ?s ?p ?o .
                    }
                """)
                for row in shape_size:
                    shape_size = "%s" % row
                print("Axioms " + shape_size)

                subjects = g.query("""
                    SELECT DISTINCT ?s
                    WHERE {
                    ?s ?p ?o .
                    }
                """)
                for row in subjects:
                    # print("%s" % row)
                    count_subjects += 1
                print("Subjects " + str(count_subjects))

                predicates = g.query("""
                    SELECT DISTINCT ?p
                    WHERE {
                    ?s ?p ?o .
                    }
                """)
                for row in predicates:
                    # print("%s" % row)
                    count_predicates += 1
                print("Predicates " + str(count_predicates))

                objects = g.query("""
                    SELECT DISTINCT ?o
                    WHERE {
                    ?s ?p ?o .
                    }
                """)
                for row in objects:
                    # print("%s" % row)
                    count_objects += 1
                print("Objects " + str(count_objects))

                count_nodeshape = g.query("""
                    SELECT (COUNT (?s) AS ?count)
                    WHERE {
                    ?s a sh:NodeShape .
                    }
                """)
                for row in count_nodeshape:
                    count_nodeshape = "%s" % row
                print("Property datatype Node " + count_nodeshape)

                count_propertyshape = g.query("""
                    SELECT (COUNT (?s) AS ?count)
                    WHERE {
                    ?s a sh:PropertyShape .
                    }
                """)
                for row in count_propertyshape:
                    count_propertyshape = "%s" % row
                print("Property datatype Property " + count_propertyshape)

                count_maxcount = g.query("""
                    SELECT (COUNT (?s) AS ?count)
                    WHERE {
                    ?s sh:maxCount ?o .
                    }
                """)
                for row in count_maxcount:
                    count_maxcount = "%s" % row
                print("Property maxCount " + count_maxcount)

                count_mincount = g.query("""
                    SELECT (COUNT (?s) AS ?count)
                    WHERE {
                    ?s sh:minCount ?o .
                    }
                """)
                for row in count_mincount:
                    count_mincount = "%s" % row
                print("Property minCount " + count_mincount)

                count_nodekind = g.query("""
                    SELECT (COUNT (?s) AS ?count)
                    WHERE {
                    ?s sh:nodeKind ?o .
                    }
                """)
                for row in count_nodekind:
                    count_nodekind = "%s" % row
                print("Property nodeKind " + count_nodekind)

                count_path = g.query("""
                    SELECT (COUNT (?s) AS ?count)
                    WHERE {
                    ?s sh:path ?o .
                    }
                """)
                for row in count_path:
                    count_path = "%s" % row
                print("Property path " + count_path)

                count_label = g.query("""
                    SELECT (COUNT (?s) AS ?count)
                    WHERE {
                    ?s rdfs:label ?o .
                    }
                """)
                for row in count_label:
                    count_label = "%s" % row
                print("Property label " + count_label)

                count_datatype = g.query("""
                    SELECT (COUNT (?s) AS ?count)
                    WHERE {
                    ?s sh:datatype ?o .
                    }
                """)
                for row in count_datatype:
                    count_datatype = "%s" % row
                print("Property datatype " + count_datatype)

                count_description = g.query("""
                    SELECT (COUNT (?s) AS ?count)
                    WHERE {
                    ?s sh:description ?o .
                    }
                """)
                for row in count_description:
                    count_description = "%s" % row
                print("Property description " + count_description)

                count_maxinclusive = g.query("""
                    SELECT (COUNT (?s) AS ?count)
                    WHERE {
                    ?s sh:maxInclusive ?o .
                    }
                """)
                for row in count_maxinclusive:
                    count_maxinclusive = "%s" % row
                print("Property maxInclusive " + count_maxinclusive)

                count_mininclusive = g.query("""
                    SELECT (COUNT (?s) AS ?count)
                    WHERE {
                    ?s sh:minInclusive ?o .
                    }
                """)
                for row in count_mininclusive:
                    count_mininclusive = "%s" % row
                print("Property minInclusive " + count_mininclusive)

                count_pattern = g.query("""
                    SELECT (COUNT (?s) AS ?count)
                    WHERE {
                    ?s sh:pattern ?o .
                    }
                """)
                for row in count_pattern:
                    count_pattern = "%s" % row
                print("Property pattern " + count_pattern)

                count_class = g.query("""
                    SELECT (COUNT (?s) AS ?count)
                    WHERE {
                    ?s sh:class ?o .
                    }
                """)
                for row in count_class:
                    count_class = "%s" % row
                print("Property class " + count_class)

                count_targetclass = g.query("""
                    SELECT (COUNT (?s) AS ?count)
                    WHERE {
                    ?s sh:targetClass ?o .
                    }
                """)
                for row in count_targetclass:
                    count_targetclass = "%s" % row
                print("Property targetclass " + count_targetclass)

                count_not = g.query("""
                    SELECT (COUNT (?s) AS ?count)
                    WHERE {
                    ?s sh:not ?o .
                    }
                """)
                for row in count_not:
                    count_not = "%s" % row
                print("Property not " + count_not)

                count_property = g.query("""
                    SELECT (COUNT (?s) AS ?count)
                    WHERE {
                    ?s sh:property ?o .
                    }
                """)
                for row in count_property:
                    count_property = "%s" % row
                print("Property property " + count_property)

                path_parent = os.path.dirname(os.getcwd())
                os.chdir(path_parent)
        print('Analysis successfully concluded')

    if shape == 'all':
        print('Shapes analysis...')
        for filename in os.listdir(shapes_dir):
            shape_number += 1
            print(str(shape_number) + ' ' + filename)
            os.chdir(shapes_dir)
            g = rdflib.Graph()
            g.parse(filename, format="turtle")
            # print(g.serialize(format="turtle").decode("utf-8"))

            shape_size = g.query("""
                SELECT (COUNT (?p) AS ?count)
                WHERE {
                ?s ?p ?o .
                }
            """)
            for row in shape_size:
                count_shapeaxioms = "%s" % row
                # print("Axioms " + count_shapeaxioms)
                count_total_shapeaxioms += int(count_shapeaxioms)

            subjects = g.query("""
                SELECT DISTINCT ?s
                WHERE {
                ?s ?p ?o .
                }
            """)
            for row in subjects:
                # print("%s" % row)
                count_subjects += 1
            # print("Subjects " + str(count_subjects))

            predicates = g.query("""
                SELECT DISTINCT ?p
                WHERE {
                ?s ?p ?o .
                }
            """)
            for row in predicates:
                # print("%s" % row)
                count_predicates += 1
            # print("Predicates " + str(count_predicates))

            objects = g.query("""
                SELECT DISTINCT ?o
                WHERE {
                ?s ?p ?o .
                }
            """)
            for row in objects:
                # print("%s" % row)
                count_objects += 1
            # print("Objects " + str(count_objects))

            count_nodeshape = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                }
            """)
            for row in count_nodeshape:
                count_nodeshape = "%s" % row
                count_total_nodeshape += int(count_nodeshape)
            # print("Property datatype Node " + count_nodeshape)

            count_propertyshape = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                }
            """)
            for row in count_propertyshape:
                count_propertyshape = "%s" % row
                count_total_propertyshape += int(count_propertyshape)
            # print("Property datatype Property " + count_propertyshape)

            count_maxcount = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:maxCount ?o .
                }
            """)
            for row in count_maxcount:
                count_maxcount = "%s" % row
                count_total_maxcount += int(count_maxcount)
            # print("Property maxCount " + count_maxcount)

            count_mincount = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:minCount ?o .
                }
            """)
            for row in count_mincount:
                count_mincount = "%s" % row
                count_total_mincount += int(count_mincount)
            # print("Property minCount " + count_mincount)

            count_nodekind = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:nodeKind ?o .
                }
            """)
            for row in count_nodekind:
                count_nodekind = "%s" % row
                count_total_nodekind += int(count_nodekind)
            # print("Property nodeKind " + count_nodekind)

            count_path = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:path ?o .
                }
            """)
            for row in count_path:
                count_path = "%s" % row
                count_total_path += int(count_path)
            # print("Property path " + count_path)

            count_label = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s rdfs:label ?o .
                }
            """)
            for row in count_label:
                count_label = "%s" % row
                count_total_label += int(count_label)
            # print("Property label " + count_label)

            count_datatype = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:datatype ?o .
                }
            """)
            for row in count_datatype:
                count_datatype = "%s" % row
                count_total_datatype += int(count_datatype)
            # print("Property datatype " + count_datatype)

            count_description = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:description ?o .
                }
            """)
            for row in count_description:
                count_description = "%s" % row
                count_total_description += int(count_description)
            # print("Property description " + count_description)

            count_maxinclusive = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:maxInclusive ?o .
                }
            """)
            for row in count_maxinclusive:
                count_maxinclusive = "%s" % row
                count_total_maxinclusive += int(count_maxinclusive)
            # print("Property maxInclusive " + count_maxinclusive)

            count_mininclusive = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:minInclusive ?o .
                }
            """)
            for row in count_mininclusive:
                count_mininclusive = "%s" % row
                count_total_mininclusive += int(count_mininclusive)
            # print("Property minInclusive " + count_mininclusive)

            count_pattern = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:pattern ?o .
                }
            """)
            for row in count_pattern:
                count_pattern = "%s" % row
                count_total_pattern += int(count_pattern)
            # print("Property pattern " + count_pattern)

            count_class = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:class ?o .
                }
            """)
            for row in count_class:
                count_class = "%s" % row
                count_total_class += int(count_class)
            # print("Property class " + count_class)

            count_targetclass = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:targetClass ?o .
                }
            """)
            for row in count_targetclass:
                count_targetclass = "%s" % row
                count_total_targetclass += int(count_targetclass)
            # print("Property targetclass " + count_targetclass)

            count_not = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:not ?o .
                }
            """)
            for row in count_not:
                count_not = "%s" % row
                count_total_not += int(count_not)
            # print("Property not " + count_not)

            count_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:property ?o .
                }
            """)
            for row in count_property:
                count_property = "%s" % row
                count_total_property += int(count_property)
            # print("Property property " + count_property)

            path_parent = os.path.dirname(os.getcwd())
            os.chdir(path_parent)

        print("Total Axioms " + str(count_total_shapeaxioms))
        print("Total Subjects " + str(count_subjects))
        print("Total Predicates " + str(count_predicates))
        print("Total Objects " + str(count_objects))
        print("Total property Datatype Node " + str(count_total_nodeshape))
        print("Total property Datatype Property " + str(count_total_propertyshape))
        print("Total property maxCount " + str(count_total_maxcount))
        print("Total property minCount " + str(count_total_mincount))
        print("Total property nodeKind " + str(count_total_nodekind))
        print("Total property path " + str(count_total_path))
        print("Total property label " + str(count_total_label))
        print("Total property datatype " + str(count_total_datatype))
        print("Total property description " + str(count_total_description))
        print("Total property maxInclusive " + str(count_total_maxinclusive))
        print("Total property minInclusive " + str(count_total_mininclusive))
        print("Total property pattern " + str(count_total_pattern))
        print("Total property class " + str(count_total_class))
        print("Total property targetclass " + str(count_total_targetclass))
        print("Total property not " + str(count_total_not))
        print("Total property property " + str(count_total_property))
        print("Analysis successfully concluded")


def main():

    # create_folders(clean=True)
    # input value clean = True to erase previous ontology and shapes folder before creating the new ones

    # divide('lov.nq')
    # input filename to divide = "lov.nq" or "test.nq"...

    # convert_triple(filename='all')
    # converts input file .nq to .nt (main.py folder level) or all files with ='all' (Ontologies folder)

    # run_astrea(ontofile='all')
    # automatically generate shape files from filename or 'all' vocabularies with Astrea (same folder logic as above)

    analysis(shape='all')


if __name__ == '__main__':
    main()
