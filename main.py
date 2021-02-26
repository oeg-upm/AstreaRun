#!/usr/bin/env python

import os
import shutil
import requests
import rdflib
import rdfextras
rdfextras.registerplugins()

onto_dir = 'Ontologies'
shapes_dir = 'Shapes'
results_dir = 'Results'


def create_folders(clean):

    if clean:
        print('Cleaning folders...')
        if os.path.isdir(onto_dir):
            shutil.rmtree(onto_dir)
        if os.path.isdir(shapes_dir):
            shutil.rmtree(shapes_dir)
        if os.path.isdir(results_dir):
            shutil.rmtree(results_dir)

    if not os.path.exists(onto_dir):
        os.mkdir(onto_dir)
    if not os.path.exists(shapes_dir):
        os.mkdir(shapes_dir)
    if not os.path.exists(results_dir):
        os.mkdir(results_dir)
    print('Folders ready')


def divide(filename):

    print('Dividing file into ontologies...')
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
    count_total_shapeaxioms = 0
    subjectslist = []
    predicateslist = []
    objectslist = []
    count_different_subjects = 0
    count_different_predicates = 0
    count_different_objects = 0
    category_list = []
    count_total_nodeshape = 0
    count_total_propertyshape = 0
    count_total_class = 0
    count_total_class_nested = 0
    count_total_class_node = 0
    count_total_class_node_nested = 0
    count_total_class_property = 0
    count_total_class_property_nested = 0
    count_total_datatype = 0
    count_total_datatype_node = 0
    count_total_datatype_property = 0
    count_total_nodekind = 0
    nodekind_list = []
    count_total_nodekind_node = 0
    count_total_nodekind_node_iri = 0
    count_total_nodekind_node_literal = 0
    count_total_nodekind_node_blanknodeoriri = 0
    count_total_nodekind_node_iriorliteral = 0
    count_total_nodekind_property_iri = 0
    count_total_nodekind_property_literal = 0
    count_total_nodekind_property_blanknodeoriri = 0
    count_total_nodekind_property_iriorliteral = 0
    count_total_nodekind_property = 0
    count_total_mincount = 0
    count_total_mincount_node = 0
    count_total_mincount_property = 0
    count_total_maxcount = 0
    count_total_maxcount_node = 0
    count_total_maxcount_property = 0
    count_total_minexclusive = 0
    count_total_minexclusive_node = 0
    count_total_minexclusive_property = 0
    count_total_mininclusive = 0
    count_total_mininclusive_node = 0
    count_total_mininclusive_property = 0
    count_total_maxexclusive = 0
    count_total_maxexclusive_node = 0
    count_total_maxexclusive_property = 0
    count_total_maxinclusive = 0
    count_total_maxinclusive_node = 0
    count_total_maxinclusive_property = 0
    count_total_minlength = 0
    count_total_minlength_node = 0
    count_total_minlength_property = 0
    count_total_maxlength = 0
    count_total_maxlength_node = 0
    count_total_maxlength_property = 0
    count_total_pattern = 0
    count_total_pattern_node = 0
    count_total_pattern_property = 0
    count_total_languagein = 0
    count_total_languagein_node = 0
    count_total_languagein_property = 0
    count_total_uniquelang = 0
    count_total_uniquelang_node = 0
    count_total_uniquelang_property = 0
    count_total_equals = 0
    count_total_equals_node = 0
    count_total_equals_property = 0
    count_total_disjoint = 0
    count_total_disjoint_node = 0
    count_total_disjoint_property = 0
    count_total_lessthan = 0
    count_total_lessthan_node = 0
    count_total_lessthan_property = 0
    count_total_lessthanorequal = 0
    count_total_lessthanorequal_node = 0
    count_total_lessthanorequal_property = 0
    count_total_not = 0
    count_total_not_node = 0
    count_total_not_property = 0
    count_total_and = 0
    count_total_and_node = 0
    count_total_and_property = 0
    count_total_or = 0
    count_total_or_node = 0
    count_total_or_property = 0
    count_total_xone = 0
    count_total_xone_node = 0
    count_total_xone_property = 0
    count_total_node = 0
    count_total_node_node = 0
    count_total_node_property = 0
    count_total_property = 0
    count_total_property_node = 0
    count_total_property_property = 0
    count_total_qualifiedvalueshape = 0
    count_total_qualifiedvalueshape_node = 0
    count_total_qualifiedvalueshape_property = 0
    count_total_qualifiedmincount = 0
    count_total_qualifiedmincount_node = 0
    count_total_qualifiedmincount_property = 0
    count_total_qualifiedmaxcount = 0
    count_total_qualifiedmaxcount_node = 0
    count_total_qualifiedmaxcount_property = 0
    count_total_closed = 0
    count_total_closed_node = 0
    count_total_closed_property = 0
    count_total_ignoredproperties = 0
    count_total_ignoredproperties_node = 0
    count_total_ignoredproperties_property = 0
    count_total_hasvalue = 0
    count_total_hasvalue_node = 0
    count_total_hasvalue_property = 0
    count_total_in = 0
    count_total_in_node = 0
    count_total_in_property = 0
    count_total_targetclass = 0
    count_total_targetclass_node = 0
    count_total_targetclass_property = 0
    count_total_name = 0
    count_total_name_node = 0
    count_total_name_property = 0
    count_total_path = 0
    count_total_path_nested = 0
    count_total_path_node = 0
    count_total_path_node_nested = 0
    count_total_path_property = 0
    count_total_path_property_nested = 0
    count_total_inversepath = 0
    count_total_inversepath_node = 0
    count_total_inversepath_property = 0
    count_total_description = 0
    count_total_description_node = 0
    count_total_description_property = 0
    count_total_label = 0
    count_total_label_node = 0
    count_total_label_property = 0
    count_total_seealso = 0
    count_total_seealso_node = 0
    count_total_seealso_property = 0
    count_total_isdefinedby = 0
    count_total_isdefinedby_node = 0
    count_total_isdefinedby_property = 0
    count_total_type = 0
    count_total_type_node = 0
    count_total_type_property = 0
    count_total_first = 0
    count_total_first_node = 0
    count_total_first_property = 0
    count_total_rest = 0
    count_total_rest_node = 0
    count_total_rest_property = 0
    count_total_contains = 0
    count_total_contains_node = 0
    count_total_contains_property = 0
    count_total_generatedshapesfrom = 0
    count_total_generatedshapesfrom_node = 0
    count_total_generatedshapesfrom_property = 0
    count_total_message = 0
    count_total_message_node = 0
    count_total_message_property = 0
    count_total_statuscode = 0
    count_total_statuscode_node = 0
    count_total_statuscode_property = 0
    count_total_source = 0
    count_total_source_node = 0
    count_total_source_property = 0

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
                    count_total_shapeaxioms = "%s" % row

                subjects = g.query("""
                                    SELECT DISTINCT ?s
                                    WHERE {
                                    ?s ?p ?o .
                                    }
                                """)
                for row in subjects:
                    # print("%s" % row)
                    count_different_subjects += 1

                predicates = g.query("""
                                    SELECT DISTINCT ?p
                                    WHERE {
                                    ?s ?p ?o .
                                    }
                                """)
                for row in predicates:
                    # print("%s" % row)
                    count_different_predicates += 1
                    predicateslist.append("%s" % row)

                objects = g.query("""
                                    SELECT DISTINCT ?o
                                    WHERE {
                                    ?s ?p ?o .
                                    }
                                """)
                for row in objects:
                    # print("%s" % row)
                    count_different_objects += 1

                count_nodeshape = g.query("""
                                    SELECT (COUNT (?s) AS ?count)
                                    WHERE {
                                    ?s a sh:NodeShape .
                                    }
                                """)
                for row in count_nodeshape:
                    count_total_nodeshape = "%s" % row

                count_propertyshape = g.query("""
                                    SELECT (COUNT (?s) AS ?count)
                                    WHERE {
                                    ?s a sh:PropertyShape .
                                    }
                                """)
                for row in count_propertyshape:
                    count_total_propertyshape = "%s" % row

                count_class_node = g.query("""
                                    SELECT (COUNT (?s) AS ?count)
                                    WHERE {
                                    ?s sh:class ?o .
                                    ?s a sh:NodeShape
                                    }
                                """)
                for row in count_class_node:
                    count_total_class_node = "%s" % row

                count_class_property = g.query("""
                                    SELECT (COUNT (?s) AS ?count)
                                    WHERE {
                                    ?s sh:class ?o .
                                    ?s a sh:PropertyShape
                                    }
                                """)
                for row in count_class_property:
                    count_total_class_property = "%s" % row

                count_datatype = g.query("""
                                    SELECT (COUNT (?s) AS ?count)
                                    WHERE {
                                    ?s sh:datatype ?o .
                                    }
                                """)
                for row in count_datatype:
                    count_total_datatype = "%s" % row

                count_nodekind = g.query("""
                                    SELECT (COUNT (?s) AS ?count)
                                    WHERE {
                                    ?s sh:nodeKind ?o .
                                    }
                                """)
                for row in count_nodekind:
                    count_total_nodekind = "%s" % row

                count_mincount = g.query("""
                                    SELECT (COUNT (?s) AS ?count)
                                    WHERE {
                                    ?s sh:minCount ?o .
                                    }
                                """)
                for row in count_mincount:
                    count_total_mincount = "%s" % row

                count_maxcount = g.query("""
                                    SELECT (COUNT (?s) AS ?count)
                                    WHERE {
                                    ?s sh:maxCount ?o .
                                    }
                                """)
                for row in count_maxcount:
                    count_total_maxcount = "%s" % row

                count_mininclusive = g.query("""
                                    SELECT (COUNT (?s) AS ?count)
                                    WHERE {
                                    ?s sh:minInclusive ?o .
                                    }
                                """)
                for row in count_mininclusive:
                    count_total_mininclusive = "%s" % row

                count_maxinclusive = g.query("""
                                    SELECT (COUNT (?s) AS ?count)
                                    WHERE {
                                    ?s sh:maxInclusive ?o .
                                    }
                                """)
                for row in count_maxinclusive:
                    count_total_maxinclusive = "%s" % row

                count_pattern = g.query("""
                                    SELECT (COUNT (?s) AS ?count)
                                    WHERE {
                                    ?s sh:pattern ?o .
                                    }
                                """)
                for row in count_pattern:
                    count_total_pattern = "%s" % row

                count_not = g.query("""
                                    SELECT (COUNT (?s) AS ?count)
                                    WHERE {
                                    ?s sh:not ?o .
                                    }
                                """)
                for row in count_not:
                    count_total_not = "%s" % row

                count_property = g.query("""
                                    SELECT (COUNT (?s) AS ?count)
                                    WHERE {
                                    ?s sh:property ?o .
                                    }
                                """)
                for row in count_property:
                    count_total_property = "%s" % row

                count_targetclass = g.query("""
                                    SELECT (COUNT (?s) AS ?count)
                                    WHERE {
                                    ?s sh:targetClass ?o .
                                    }
                                """)
                for row in count_targetclass:
                    count_total_targetclass = "%s" % row

                count_path = g.query("""
                                    SELECT (COUNT (?s) AS ?count)
                                    WHERE {
                                    ?s sh:path ?o .
                                    }
                                """)
                for row in count_path:
                    count_total_path = "%s" % row

                count_description = g.query("""
                                    SELECT (COUNT (?s) AS ?count)
                                    WHERE {
                                    ?s sh:description ?o .
                                    }
                                """)
                for row in count_description:
                    count_total_description = "%s" % row

                count_label = g.query("""
                                    SELECT (COUNT (?s) AS ?count)
                                    WHERE {
                                    ?s rdfs:label ?o .
                                    }
                                """)
                for row in count_label:
                    count_total_label = "%s" % row

                path_parent = os.path.dirname(os.getcwd())
                os.chdir(path_parent)

    if shape == 'all':

        exceptions = ['<http:semanticturkey.uniroma2.itnsmdr>shape.ttl', '<http:purl.orgeem>shape.ttl',
        '<http:purl.orgmedia>shape.ttl', '<https:w3id.orgeepsa>shape.ttl', '<http:softeng.polito.itrsctx>shape.ttl']

        print('Shapes analysis...')
        for filename in os.listdir(shapes_dir):
            if filename in exceptions:
                continue
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
                count_different_subjects += 1
                subjectslist.append("%s" % row)
            # print("Subjects " + str(count_subjects))

            predicates = g.query("""
                            SELECT DISTINCT ?p
                            WHERE {
                            ?s ?p ?o .
                            }
                        """)
            for row in predicates:
                # print("%s" % row)
                count_different_predicates += 1
                predicateslist.append("%s" % row)
            # print("Predicates " + str(count_predicates))

            objects = g.query("""
                            SELECT DISTINCT ?o
                            WHERE {
                            ?s ?p ?o .
                            }
                        """)
            for row in objects:
                # print("%s" % row)
                count_different_objects += 1
                objectslist.append("%s" % row)
            # print("Objects " + str(count_objects))

            category = g.query("""
                            SELECT DISTINCT ?o
                            WHERE {
                            ?s a ?o .
                            }
                        """)
            for row in category:
                category_list.append("%s" % row)

            count_nodeshape = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            }
                        """)
            for row in count_nodeshape:
                count_nodeshape = "%s" % row
                count_total_nodeshape += int(count_nodeshape)

            count_propertyshape = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            }
                        """)
            for row in count_propertyshape:
                count_propertyshape = "%s" % row
                count_total_propertyshape += int(count_propertyshape)

            count_class = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:class ?o .
                            }
                        """)
            for row in count_class:
                count_class = "%s" % row
                count_total_class += int(count_class)

            count_class_nested = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:or ?typesList .
                            ?typesList rdf:rest* ?typesListRest .
                            ?typesListRest rdf:first [ sh:class ?o] .
                            }
                        """)
            for row in count_class_nested:
                count_class_nested = "%s" % row
                count_total_class_nested += int(count_class_nested)

            count_class_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:class ?o .
                            }
                        """)
            for row in count_class_node:
                count_class_node = "%s" % row
                count_total_class_node += int(count_class_node)

            count_class_node_nested = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:or ?typesList .
                            ?typesList rdf:rest* ?typesListRest .
                            ?typesListRest rdf:first [ sh:class ?o] .
                            }
                        """)
            for row in count_class_node_nested:
                count_class_node_nested = "%s" % row
                count_total_class_node_nested += int(count_class_node_nested)

            count_class_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:class ?o .
                            }
                        """)
            for row in count_class_property:
                count_class_property = "%s" % row
                count_total_class_property += int(count_class_property)

            count_class_property_nested = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:or ?typesList .
                            ?typesList rdf:rest* ?typesListRest .
                            ?typesListRest rdf:first [ sh:class ?o] .
                            }
                        """)
            for row in count_class_property_nested:
                count_class_property_nested = "%s" % row
                count_total_class_property_nested += int(count_class_property_nested)

            count_datatype = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:datatype ?o .
                            }
                        """)
            for row in count_datatype:
                count_datatype = "%s" % row
                count_total_datatype += int(count_datatype)

            count_datatype_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:datatype ?o .
                            }
                        """)
            for row in count_datatype_node:
                count_datatype_node = "%s" % row
                count_total_datatype_node += int(count_datatype_node)

            count_datatype_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:datatype ?o .
                            }
                        """)
            for row in count_datatype_property:
                count_datatype_property = "%s" % row
                count_total_datatype_property += int(count_datatype_property)

            count_nodekind = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:nodeKind ?o .
                            }
                        """)
            for row in count_nodekind:
                count_nodekind = "%s" % row
                count_total_nodekind += int(count_nodekind)

            nodekind = g.query("""
                            SELECT DISTINCT ?o
                            WHERE {
                            ?s sh:nodeKind ?o .
                            }
                        """)
            for row in nodekind:
                nodekind_list.append("%s" % row)

            count_nodekind_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:nodeKind ?o .
                            }
                        """)
            for row in count_nodekind_node:
                count_nodekind_node = "%s" % row
                count_total_nodekind_node += int(count_nodekind_node)

            count_nodekind_node_iri = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:nodeKind sh:IRI .
                            }
                        """)
            for row in count_nodekind_node_iri:
                count_nodekind_node_iri = "%s" % row
                count_total_nodekind_node_iri += int(count_nodekind_node_iri)

            count_nodekind_node_literal = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:nodeKind sh:Literal .
                            }
                        """)
            for row in count_nodekind_node_literal:
                count_nodekind_node_literal = "%s" % row
                count_total_nodekind_node_literal += int(count_nodekind_node_literal)

            count_nodekind_node_blanknodeoriri = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:nodeKind sh:BlankNodeOrIRI .
                            }
                        """)
            for row in count_nodekind_node_blanknodeoriri:
                count_nodekind_node_blanknodeoriri = "%s" % row
                count_total_nodekind_node_blanknodeoriri += int(count_nodekind_node_blanknodeoriri)

            count_nodekind_node_iriorliteral = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:nodeKind sh:IRIOrLiteral .
                            }
                        """)
            for row in count_nodekind_node_iriorliteral:
                count_nodekind_node_iriorliteral = "%s" % row
                count_total_nodekind_node_iriorliteral += int(count_nodekind_node_iriorliteral)

            count_nodekind_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:nodeKind ?o .
                            }
                        """)
            for row in count_nodekind_property:
                count_nodekind_property = "%s" % row
                count_total_nodekind_property += int(count_nodekind_property)

            count_nodekind_property_iri = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:nodeKind sh:IRI .
                            }
                        """)
            for row in count_nodekind_property_iri:
                count_nodekind_property_iri = "%s" % row
                count_total_nodekind_property_iri += int(count_nodekind_property_iri)

            count_nodekind_property_literal = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:nodeKind sh:Literal .
                            }
                        """)
            for row in count_nodekind_property_literal:
                count_nodekind_property_literal = "%s" % row
                count_total_nodekind_property_literal += int(count_nodekind_property_literal)

            count_nodekind_property_blanknodeoriri = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:nodeKind sh:BlankNodeOrIRI .
                            }
                        """)
            for row in count_nodekind_property_blanknodeoriri:
                count_nodekind_property_blanknodeoriri = "%s" % row
                count_total_nodekind_property_blanknodeoriri += int(count_nodekind_property_blanknodeoriri)

            count_nodekind_property_iriorliteral = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:nodeKind sh:IRIOrLiteral .
                            }
                        """)
            for row in count_nodekind_property_iriorliteral:
                count_nodekind_property_iriorliteral = "%s" % row
                count_total_nodekind_property_iriorliteral += int(count_nodekind_property_iriorliteral)

            count_mincount = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:minCount ?o .
                            }
                        """)
            for row in count_mincount:
                count_mincount = "%s" % row
                count_total_mincount += int(count_mincount)

            count_mincount_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:minCount ?o .
                            }
                        """)
            for row in count_mincount_node:
                count_mincount_node = "%s" % row
                count_total_mincount_node += int(count_mincount_node)

            count_mincount_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:minCount ?o .
                            }
                        """)
            for row in count_mincount_property:
                count_mincount_property = "%s" % row
                count_total_mincount_property += int(count_mincount_property)

            count_maxcount = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:maxCount ?o .
                            }
                        """)
            for row in count_maxcount:
                count_maxcount = "%s" % row
                count_total_maxcount += int(count_maxcount)

            count_maxcount_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:maxCount ?o .
                            }
                        """)
            for row in count_maxcount_node:
                count_maxcount_node = "%s" % row
                count_total_maxcount_node += int(count_maxcount_node)

            count_maxcount_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:maxCount ?o .
                            }
                        """)
            for row in count_maxcount_property:
                count_maxcount_property = "%s" % row
                count_total_maxcount_property += int(count_maxcount_property)

            count_minexclusive = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:minExclusive ?o .
                            }
                        """)
            for row in count_minexclusive:
                count_minexclusive = "%s" % row
                count_total_minexclusive += int(count_minexclusive)

            count_minexclusive_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:minExclusive ?o .
                            }
                        """)
            for row in count_minexclusive_node:
                count_minexclusive_node = "%s" % row
                count_total_minexclusive_node += int(count_minexclusive_node)

            count_minexclusive_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:minExclusive ?o .
                            }
                        """)
            for row in count_minexclusive_property:
                count_minexclusive_property = "%s" % row
                count_total_minexclusive_property += int(count_minexclusive_property)

            count_mininclusive = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:minInclusive ?o .
                            }
                        """)
            for row in count_mininclusive:
                count_mininclusive = "%s" % row
                count_total_mininclusive += int(count_mininclusive)

            count_mininclusive_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:minInclusive ?o .
                            }
                        """)
            for row in count_mininclusive_node:
                count_mininclusive_node = "%s" % row
                count_total_mininclusive_node += int(count_mininclusive_node)

            count_mininclusive_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:minInclusive ?o .
                            }
                        """)
            for row in count_mininclusive_property:
                count_mininclusive_property = "%s" % row
                count_total_mininclusive_property += int(count_mininclusive_property)

            count_maxexclusive = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:maxExclusive ?o .
                            }
                        """)
            for row in count_maxexclusive:
                count_maxexclusive = "%s" % row
                count_total_maxexclusive += int(count_maxexclusive)

            count_maxexclusive_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:maxExclusive ?o .
                            }
                        """)
            for row in count_maxexclusive_node:
                count_maxexclusive_node = "%s" % row
                count_total_maxexclusive_node += int(count_maxexclusive_node)

            count_maxexclusive_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:maxExclusive ?o .
                            }
                        """)
            for row in count_maxexclusive_property:
                count_maxexclusive_property = "%s" % row
                count_total_maxexclusive_property += int(count_maxexclusive_property)

            count_maxinclusive = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:maxInclusive ?o .
                            }
                        """)
            for row in count_maxinclusive:
                count_maxinclusive = "%s" % row
                count_total_maxinclusive += int(count_maxinclusive)

            count_maxinclusive_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:maxInclusive ?o .
                            }
                        """)
            for row in count_maxinclusive_node:
                count_maxinclusive_node = "%s" % row
                count_total_maxinclusive_node += int(count_maxinclusive_node)

            count_maxinclusive_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:maxInclusive ?o .
                            }
                        """)
            for row in count_maxinclusive_property:
                count_maxinclusive_property = "%s" % row
                count_total_maxinclusive_property += int(count_maxinclusive_property)

            count_minlength = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:minLength ?o .
                            }
                        """)
            for row in count_minlength:
                count_minlength = "%s" % row
                count_total_minlength += int(count_minlength)

            count_minlength_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:minLength ?o .
                            }
                        """)
            for row in count_minlength_node:
                count_minlength_node = "%s" % row
                count_total_minlength_node += int(count_minlength_node)

            count_minlength_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:minLength ?o .
                            }
                        """)
            for row in count_minlength_property:
                count_minlength_property = "%s" % row
                count_total_minlength_property += int(count_minlength_property)

            count_maxlength = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:maxLength ?o .
                }
            """)
            for row in count_maxlength:
                count_maxlength = "%s" % row
                count_total_maxlength += int(count_maxlength)

            count_maxlength_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s sh:maxLength ?o .
                }
            """)
            for row in count_maxlength_node:
                count_maxlength_node = "%s" % row
                count_total_maxlength_node += int(count_maxlength_node)

            count_maxlength_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s sh:maxLength ?o .
                }
            """)
            for row in count_maxlength_property:
                count_maxlength_property = "%s" % row
                count_total_maxlength_property += int(count_maxlength_property)

            count_pattern = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:pattern ?o .
                            }
                        """)
            for row in count_pattern:
                count_pattern = "%s" % row
                count_total_pattern += int(count_pattern)

            count_pattern_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:pattern ?o .
                            }
                        """)
            for row in count_pattern_node:
                count_pattern_node = "%s" % row
                count_total_pattern_node += int(count_pattern_node)

            count_pattern_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:pattern ?o .
                            }
                        """)
            for row in count_pattern_property:
                count_pattern_property = "%s" % row
                count_total_pattern_property += int(count_pattern_property)

            count_languagein = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:languageIn ?o .
                            }
                        """)
            for row in count_languagein:
                count_languagein = "%s" % row
                count_total_languagein += int(count_languagein)

            count_languagein_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:languageIn ?o .
                            }
                        """)
            for row in count_languagein_node:
                count_languagein_node = "%s" % row
                count_total_languagein_node += int(count_languagein_node)

            count_languagein_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:languageIn ?o .
                            }
                        """)
            for row in count_languagein_property:
                count_languagein_property = "%s" % row
                count_total_languagein_property += int(count_languagein_property)

            count_uniquelang = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:uniqueLang ?o .
                            }
                        """)
            for row in count_uniquelang:
                count_uniquelang = "%s" % row
                count_total_uniquelang += int(count_uniquelang)

            count_uniquelang_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:uniqueLang ?o .
                            }
                        """)
            for row in count_uniquelang_node:
                count_uniquelang_node = "%s" % row
                count_total_uniquelang_node += int(count_uniquelang_node)

            count_uniquelang_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:uniqueLang ?o .
                            }
                        """)
            for row in count_uniquelang_property:
                count_uniquelang_property = "%s" % row
                count_total_uniquelang_property += int(count_uniquelang_property)

            count_equals = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:equals ?o .
                            }
                        """)
            for row in count_equals:
                count_equals = "%s" % row
                count_total_equals += int(count_equals)

            count_equals_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:equals ?o .
                            }
                        """)
            for row in count_equals_node:
                count_equals_node = "%s" % row
                count_total_equals_node += int(count_equals_node)

            count_equals_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:equals ?o .
                            }
                        """)
            for row in count_equals_property:
                count_equals_property = "%s" % row
                count_total_equals_property += int(count_equals_property)

            count_disjoint = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:disjoint ?o .
                            }
                        """)
            for row in count_disjoint:
                count_disjoint = "%s" % row
                count_total_disjoint += int(count_disjoint)

            count_disjoint_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:disjoint ?o .
                            }
                        """)
            for row in count_disjoint_node:
                count_disjoint_node = "%s" % row
                count_total_disjoint_node += int(count_disjoint_node)

            count_disjoint_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:disjoint ?o .
                            }
                        """)
            for row in count_disjoint_property:
                count_disjoint_property = "%s" % row
                count_total_disjoint_property += int(count_disjoint_property)

            count_lessthan = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:lessThan ?o .
                            }
                        """)
            for row in count_lessthan:
                count_lessthan = "%s" % row
                count_total_lessthan += int(count_lessthan)

            count_lessthan_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:lessThan ?o .
                            }
                        """)
            for row in count_lessthan_node:
                count_lessthan_node = "%s" % row
                count_total_lessthan_node += int(count_lessthan_node)

            count_lessthan_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:lessThan ?o .
                            }
                        """)
            for row in count_lessthan_property:
                count_lessthan_property = "%s" % row
                count_total_lessthan_property += int(count_lessthan_property)

            count_lessthanorequal = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:lessThanOrEqual ?o .
                            }
                        """)
            for row in count_lessthanorequal:
                count_lessthanorequal = "%s" % row
                count_total_lessthanorequal += int(count_lessthanorequal)

            count_lessthanorequal_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:lessThanOrEqual ?o .
                            }
                        """)
            for row in count_lessthanorequal_node:
                count_lessthanorequal_node = "%s" % row
                count_total_lessthanorequal_node += int(count_lessthanorequal_node)

            count_lessthanorequal_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:lessThanOrEqual ?o .
                            }
                        """)
            for row in count_lessthanorequal_property:
                count_lessthanorequal_property = "%s" % row
                count_total_lessthanorequal_property += int(count_lessthanorequal_property)

            count_not = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:not ?o .
                            }
                        """)
            for row in count_not:
                count_not = "%s" % row
                count_total_not += int(count_not)

            count_not_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:not ?o .
                            }
                        """)
            for row in count_not_node:
                count_not_node = "%s" % row
                count_total_not_node += int(count_not_node)

            count_not_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:not ?o .
                            }
                        """)
            for row in count_not_property:
                count_not_property = "%s" % row
                count_total_not_property += int(count_not_property)

            count_and = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:and ?o .
                            }
                        """)
            for row in count_and:
                count_and = "%s" % row
                count_total_and += int(count_and)

            count_and_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:and ?o .
                            }
                        """)
            for row in count_and_node:
                count_and_node = "%s" % row
                count_total_and_node += int(count_and_node)

            count_and_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:and ?o .
                            }
                        """)
            for row in count_and_property:
                count_and_property = "%s" % row
                count_total_and_property += int(count_and_property)

            count_or = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:or ?o .
                            }
                        """)
            for row in count_or:
                count_or = "%s" % row
                count_total_or += int(count_or)

            count_or_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:or ?o .
                            }
                        """)
            for row in count_or_node:
                count_or_node = "%s" % row
                count_total_or_node += int(count_or_node)

            count_or_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:or ?o .
                            }
                        """)
            for row in count_or_property:
                count_or_property = "%s" % row
                count_total_or_property += int(count_or_property)

            count_xone = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:xone ?o .
                            }
                        """)
            for row in count_xone:
                count_xone = "%s" % row
                count_total_xone += int(count_xone)

            count_xone_node = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:NodeShape .
                            ?s sh:xone ?o .
                            }
                        """)
            for row in count_xone_node:
                count_xone_node = "%s" % row
                count_total_xone_node += int(count_xone_node)

            count_xone_property = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s a sh:PropertyShape .
                            ?s sh:xone ?o .
                            }
                        """)
            for row in count_xone_property:
                count_xone_property = "%s" % row
                count_total_xone_property += int(count_xone_property)

            count_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:node ?o .
                }
            """)
            for row in count_node:
                count_node = "%s" % row
                count_total_node += int(count_node)

            count_node_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s sh:node ?o .
                }
            """)
            for row in count_node_node:
                count_node_node = "%s" % row
                count_total_node_node += int(count_node_node)

            count_node_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s sh:node ?o .
                }
            """)
            for row in count_node_property:
                count_node_property = "%s" % row
                count_total_node_property += int(count_node_property)

            count_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:property ?o .
                }
            """)
            for row in count_property:
                count_property = "%s" % row
                count_total_property += int(count_property)

            count_property_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s sh:property ?o .
                }
            """)
            for row in count_property_node:
                count_property_node = "%s" % row
                count_total_property_node += int(count_property_node)

            count_property_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s sh:property ?o .
                }
            """)
            for row in count_property_property:
                count_property_property = "%s" % row
                count_total_property_property += int(count_property_property)

            count_qualifiedvalueshape = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:qualifiedValueShape ?o .
                }
            """)
            for row in count_qualifiedvalueshape:
                count_qualifiedvalueshape = "%s" % row
                count_total_qualifiedvalueshape += int(count_qualifiedvalueshape)

            count_qualifiedvalueshape_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s sh:qualifiedValueShape ?o .
                }
            """)
            for row in count_qualifiedvalueshape_node:
                count_qualifiedvalueshape_node = "%s" % row
                count_total_qualifiedvalueshape_node += int(count_qualifiedvalueshape_node)

            count_qualifiedvalueshape_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s sh:qualifiedValueShape ?o .
                }
            """)
            for row in count_qualifiedvalueshape_property:
                count_qualifiedvalueshape_property = "%s" % row
                count_total_qualifiedvalueshape_property += int(count_qualifiedvalueshape_property)

            count_qualifiedmincount = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:qualifiedMinCount ?o .
                }
            """)
            for row in count_qualifiedmincount:
                count_qualifiedmincount = "%s" % row
                count_total_qualifiedmincount += int(count_qualifiedmincount)

            count_qualifiedmincount_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s sh:qualifiedMinCount ?o .
                }
            """)
            for row in count_qualifiedmincount_node:
                count_qualifiedmincount_node = "%s" % row
                count_total_qualifiedmincount_node += int(count_qualifiedmincount_node)

            count_qualifiedmincount_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s sh:qualifiedMinCount ?o .
                }
            """)
            for row in count_qualifiedmincount_property:
                count_qualifiedmincount_property = "%s" % row
                count_total_qualifiedmincount_property += int(count_qualifiedmincount_property)

            count_qualifiedmaxcount = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:qualifiedMaxCount ?o .
                }
            """)
            for row in count_qualifiedmaxcount:
                count_qualifiedmaxcount = "%s" % row
                count_total_qualifiedmaxcount += int(count_qualifiedmaxcount)

            count_qualifiedmaxcount_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s sh:qualifiedMaxCount ?o .
                }
            """)
            for row in count_qualifiedmaxcount_node:
                count_qualifiedmaxcount_node = "%s" % row
                count_total_qualifiedmaxcount_node += int(count_qualifiedmaxcount_node)

            count_qualifiedmaxcount_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s sh:qualifiedMaxCount ?o .
                }
            """)
            for row in count_qualifiedmaxcount_property:
                count_qualifiedmaxcount_property = "%s" % row
                count_total_qualifiedmaxcount_property += int(count_qualifiedmaxcount_property)

            count_closed = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:closed ?o .
                }
            """)
            for row in count_closed:
                count_closed = "%s" % row
                count_total_closed += int(count_closed)

            count_closed_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s sh:closed ?o .
                }
            """)
            for row in count_closed_node:
                count_closed_node = "%s" % row
                count_total_closed_node += int(count_closed_node)

            count_closed_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s sh:closed ?o .
                }
            """)
            for row in count_closed_property:
                count_closed_property = "%s" % row
                count_total_closed_property += int(count_closed_property)

            count_ignoredproperties = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:ignoredProperties ?o .
                }
            """)
            for row in count_ignoredproperties:
                count_ignoredproperties = "%s" % row
                count_total_ignoredproperties += int(count_ignoredproperties)

            count_ignoredproperties_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s sh:ignoredProperties ?o .
                }
            """)
            for row in count_ignoredproperties_node:
                count_ignoredproperties_node = "%s" % row
                count_total_ignoredproperties_node += int(count_ignoredproperties_node)

            count_ignoredproperties_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s sh:ignoredProperties ?o .
                }
            """)
            for row in count_ignoredproperties_property:
                count_ignoredproperties_property = "%s" % row
                count_total_ignoredproperties_property += int(count_ignoredproperties_property)

            count_hasvalue = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:hasValue ?o .
                }
            """)
            for row in count_hasvalue:
                count_hasvalue = "%s" % row
                count_total_hasvalue += int(count_hasvalue)

            count_hasvalue_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s sh:hasValue ?o .
                }
            """)
            for row in count_hasvalue_node:
                count_hasvalue_node = "%s" % row
                count_total_hasvalue_node += int(count_hasvalue_node)

            count_hasvalue_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s sh:hasValue ?o .
                }
            """)
            for row in count_hasvalue_property:
                count_hasvalue_property = "%s" % row
                count_total_hasvalue_property += int(count_hasvalue_property)

            count_in = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:in ?o .
                }
            """)
            for row in count_in:
                count_in = "%s" % row
                count_total_in += int(count_in)

            count_in_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s sh:in ?o .
                }
            """)
            for row in count_in_node:
                count_in_node = "%s" % row
                count_total_in_node += int(count_in_node)

            count_in_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s sh:in ?o .
                }
            """)
            for row in count_in_property:
                count_in_property = "%s" % row
                count_total_in_property += int(count_in_property)

            count_targetclass = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:targetClass ?o .
                }
            """)
            for row in count_targetclass:
                count_targetclass = "%s" % row
                count_total_targetclass += int(count_targetclass)

            count_targetclass_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s sh:targetClass ?o .
                }
            """)
            for row in count_targetclass_node:
                count_targetclass_node = "%s" % row
                count_total_targetclass_node += int(count_targetclass_node)

            count_targetclass_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s sh:targetClass ?o .
                }
            """)
            for row in count_targetclass_property:
                count_targetclass_property = "%s" % row
                count_total_targetclass_property += int(count_targetclass_property)

            count_name = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:name ?o .
                }
            """)
            for row in count_name:
                count_name = "%s" % row
                count_total_name += int(count_name)

            count_name_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s sh:name ?o .
                }
            """)
            for row in count_name_node:
                count_name_node = "%s" % row
                count_total_name_node += int(count_name_node)

            count_name_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s sh:name ?o .
                }
            """)
            for row in count_name_property:
                count_name_property = "%s" % row
                count_total_name_property += int(count_name_property)

            count_path = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:path ?o .
                }
            """)
            for row in count_path:
                count_path = "%s" % row
                count_total_path += int(count_path)

            count_path_nested = g.query("""
                            SELECT (COUNT (?s) AS ?count)
                            WHERE {
                            ?s sh:or ?typesList .
                            ?typesList rdf:rest* ?typesListRest .
                            ?typesListRest rdf:first [ sh:path ?o] .
                            }
                        """)
            for row in count_path_nested:
                count_path_nested = "%s" % row
                count_total_path_nested += int(count_path_nested)

            count_path_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s sh:path ?o .
                }
            """)
            for row in count_path_node:
                count_path_node = "%s" % row
                count_total_path_node += int(count_path_node)

            count_path_node_nested = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s sh:or ?typesList .
                ?typesList rdf:rest* ?typesListRest .
                ?typesListRest rdf:first [ sh:path ?o] .
                }
            """)
            for row in count_path_node_nested:
                count_path_node_nested = "%s" % row
                count_total_path_node_nested += int(count_path_node_nested)

            count_path_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s sh:path ?o .
                }
            """)
            for row in count_path_property:
                count_path_property = "%s" % row
                count_total_path_property += int(count_path_property)

            count_path_property_nested = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s sh:or ?typesList .
                ?typesList rdf:rest* ?typesListRest .
                ?typesListRest rdf:first [ sh:path ?o] .
                }
            """)
            for row in count_path_property_nested:
                count_path_property_nested = "%s" % row
                count_total_path_property_nested += int(count_path_property_nested)

            count_inversepath = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:inversePath ?o .
                }
            """)
            for row in count_inversepath:
                count_inversepath = "%s" % row
                count_total_inversepath += int(count_inversepath)

            count_inversepath_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s sh:inversePath ?o .
                }
            """)
            for row in count_inversepath_node:
                count_inversepath_node = "%s" % row
                count_total_inversepath_node += int(count_inversepath_node)

            count_inversepath_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s sh:inversePath ?o .
                }
            """)
            for row in count_inversepath_property:
                count_inversepath_property = "%s" % row
                count_total_inversepath_property += int(count_inversepath_property)

            count_description = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s sh:description ?o .
                }
            """)
            for row in count_description:
                count_description = "%s" % row
                count_total_description += int(count_description)

            count_description_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s sh:description ?o .
                }
            """)
            for row in count_description_node:
                count_description_node = "%s" % row
                count_total_description_node += int(count_description_node)

            count_description_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s sh:description ?o .
                }
            """)
            for row in count_description_property:
                count_description_property = "%s" % row
                count_total_description_property += int(count_description_property)

            count_label = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s rdfs:label ?o .
                }
            """)
            for row in count_label:
                count_label = "%s" % row
                count_total_label += int(count_label)

            count_label_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s rdfs:label ?o .
                }
            """)
            for row in count_label_node:
                count_label_node = "%s" % row
                count_total_label_node += int(count_label_node)

            count_label_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s rdfs:label ?o .
                }
            """)
            for row in count_label_property:
                count_label_property = "%s" % row
                count_total_label_property += int(count_label_property)

            count_seealso = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s rdfs:seeAlso ?o .
                }
            """)
            for row in count_seealso:
                count_seealso = "%s" % row
                count_total_seealso += int(count_seealso)

            count_seealso_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s rdfs:seeAlso ?o .
                }
            """)
            for row in count_seealso_node:
                count_seealso_node = "%s" % row
                count_total_seealso_node += int(count_seealso_node)

            count_seealso_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s rdfs:seeAlso ?o .
                }
            """)
            for row in count_seealso_property:
                count_seealso_property = "%s" % row
                count_total_seealso_property += int(count_seealso_property)

            count_isdefinedby = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s rdfs:isDefinedBy ?o .
                }
            """)
            for row in count_isdefinedby:
                count_isdefinedby = "%s" % row
                count_total_isdefinedby += int(count_isdefinedby)

            count_isdefinedby_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s rdfs:isDefinedBy ?o .
                }
            """)
            for row in count_isdefinedby_node:
                count_isdefinedby_node = "%s" % row
                count_total_isdefinedby_node += int(count_isdefinedby_node)

            count_isdefinedby_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s rdfs:isDefinedBy ?o .
                }
            """)
            for row in count_isdefinedby_property:
                count_isdefinedby_property = "%s" % row
                count_total_isdefinedby_property += int(count_isdefinedby_property)

            count_type = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s rdf:type ?o .
                }
            """)
            for row in count_type:
                count_type = "%s" % row
                count_total_type += int(count_type)

            count_type_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s rdf:type ?o .
                }
            """)
            for row in count_type_node:
                count_type_node = "%s" % row
                count_total_type_node += int(count_type_node)

            count_type_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s rdf:type ?o .
                }
            """)
            for row in count_type_property:
                count_type_property = "%s" % row
                count_total_type_property += int(count_type_property)

            count_first = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s rdf:first ?o .
                }
            """)
            for row in count_first:
                count_first = "%s" % row
                count_total_first += int(count_first)

            count_first_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s rdf:first ?o .
                }
            """)
            for row in count_first_node:
                count_first_node = "%s" % row
                count_total_first_node += int(count_first_node)

            count_first_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s rdf:first ?o .
                }
            """)
            for row in count_first_property:
                count_first_property = "%s" % row
                count_total_first_property += int(count_first_property)

            count_rest = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s rdf:rest ?o 
                }
            """)
            for row in count_rest:
                count_rest = "%s" % row
                count_total_rest += int(count_rest)

            count_rest_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s rdf:rest ?o .
                }
            """)
            for row in count_rest_node:
                count_rest_node = "%s" % row
                count_total_rest_node += int(count_rest_node)

            count_rest_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s rdf:rest ?o .
                }
            """)
            for row in count_rest_property:
                count_rest_property = "%s" % row
                count_total_rest_property += int(count_rest_property)

            count_contains = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s <https://w3id.org/def/astrea#contains> ?o .
                }
            """)
            for row in count_contains:
                count_contains = "%s" % row
                count_total_contains += int(count_contains)

            count_contains_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s <https://w3id.org/def/astrea#contains> ?o .
                }
            """)
            for row in count_contains_node:
                count_contains_node = "%s" % row
                count_total_contains_node += int(count_contains_node)

            count_contains_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s <https://w3id.org/def/astrea#contains> ?o .
                }
            """)
            for row in count_contains_property:
                count_contains_property = "%s" % row
                count_total_contains_property += int(count_contains_property)

            count_generatedshapesfrom = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s <https://w3id.org/def/astrea#generatedShapesFrom> ?o .
                }
            """)
            for row in count_generatedshapesfrom:
                count_generatedshapesfrom = "%s" % row
                count_total_generatedshapesfrom += int(count_generatedshapesfrom)

            count_generatedshapesfrom_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s <https://w3id.org/def/astrea#generatedShapesFrom> ?o .
                }
            """)
            for row in count_generatedshapesfrom_node:
                count_generatedshapesfrom_node = "%s" % row
                count_total_generatedshapesfrom_node += int(count_generatedshapesfrom_node)

            count_generatedshapesfrom_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s <https://w3id.org/def/astrea#generatedShapesFrom> ?o .
                }
            """)
            for row in count_generatedshapesfrom_property:
                count_generatedshapesfrom_property = "%s" % row
                count_total_generatedshapesfrom_property += int(count_generatedshapesfrom_property)

            count_message = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s <https://w3id.org/def/astrea#message> ?o .
                }
            """)
            for row in count_message:
                count_message = "%s" % row
                count_total_message += int(count_message)

            count_message_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s <https://w3id.org/def/astrea#message> ?o .
                }
            """)
            for row in count_message_node:
                count_message_node = "%s" % row
                count_total_message_node += int(count_message_node)

            count_message_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s <https://w3id.org/def/astrea#message> ?o .
                }
            """)
            for row in count_message_property:
                count_message_property = "%s" % row
                count_total_message_property += int(count_message_property)

            count_statuscode = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s <https://w3id.org/def/astrea#statusCode> ?o .
                }
            """)
            for row in count_statuscode:
                count_statuscode = "%s" % row
                count_total_statuscode += int(count_statuscode)

            count_statuscode_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s <https://w3id.org/def/astrea#statusCode> ?o .
                }
            """)
            for row in count_statuscode_node:
                count_statuscode_node = "%s" % row
                count_total_statuscode_node += int(count_statuscode_node)

            count_statuscode_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s <https://w3id.org/def/astrea#statusCode> ?o .
                }
            """)
            for row in count_statuscode_property:
                count_statuscode_property = "%s" % row
                count_total_statuscode_property += int(count_statuscode_property)

            count_source = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s <https://w3id.org/def/astrea#source> ?o .
                }
            """)
            for row in count_source:
                count_source = "%s" % row
                count_total_source += int(count_source)

            count_source_node = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:NodeShape .
                ?s <https://w3id.org/def/astrea#source> ?o .
                }
            """)
            for row in count_source_node:
                count_source_node = "%s" % row
                count_total_source_node += int(count_source_node)

            count_source_property = g.query("""
                SELECT (COUNT (?s) AS ?count)
                WHERE {
                ?s a sh:PropertyShape .
                ?s <https://w3id.org/def/astrea#source> ?o .
                }
            """)
            for row in count_source_property:
                count_source_property = "%s" % row
                count_total_source_property += int(count_source_property)

            path_parent = os.path.dirname(os.getcwd())
            os.chdir(path_parent)

            os.chdir(results_dir)
            with open('results', 'w') as file:
                file.write("(1): Excluding repeated elements from a same shape " + "\n" +
                           "(2): Only unnested " + "\n" +
                           "Total Axioms " + str(count_total_shapeaxioms) + "\n" +
                           "Total Subjects (1) " + str(count_different_subjects) + "\n" +
                           "Total different Subjects " + str(len(dict.fromkeys(subjectslist))) + "\n" +
                           "Total Predicates (1) " + str(count_different_predicates) + "\n" +
                           "Total different Predicates " + str(len(dict.fromkeys(predicateslist))) + "\n" +
                           "Total Objects (1) " + str(count_different_objects) + "\n" +
                           "Total different Objects " + str(len(dict.fromkeys(objectslist))) + "\n" +
                           "List total different categories " + str(list(dict.fromkeys(category_list))) + "\n" +
                           "Total Node Shapes " + str(count_total_nodeshape) + "\n" +
                           "Total Property Shapes " + str(count_total_propertyshape) + "\n" +
                           "Present constraint components list: " + str(list(dict.fromkeys(predicateslist))) + "\n" +
                           "Total sh:class " + str(count_total_class) + "\n" +
                           "Total sh:class nested " + str(count_total_class_nested) + "\n" +
                           "Total sh:class node " + str(count_total_class_node) + "\n" +
                           "Total sh:class node nested " + str(count_total_class_node_nested) + "\n" +
                           "Total sh:class property " + str(count_total_class_property) + "\n" +
                           "Total sh:class property nested " + str(count_total_class_property_nested) + "\n" +
                           "Total sh:datatype " + str(count_total_datatype) + "\n" +
                           "Total sh:datatype node " + str(count_total_datatype_node) + "\n" +
                           "Total sh:datatype property " + str(count_total_datatype_property) + "\n" +
                           "Total sh:nodeKind " + str(count_total_nodekind) + "\n" +
                           "sh:nodeKind types list " + str(list(dict.fromkeys(nodekind_list))) + "\n" +
                           "Total sh:nodeKind node " + str(count_total_nodekind_node) + "\n" +
                           "Total sh:nodeKind node IRI " + str(count_total_nodekind_node_iri) + "\n" +
                           "Total sh:nodeKind node Literal " + str(count_total_nodekind_node_literal) + "\n" +
                           "Total sh:nodeKind node Blank node or IRI " + str(count_total_nodekind_node_blanknodeoriri) + "\n" +
                           "Total sh:nodeKind node IRI or literal  " + str(count_total_nodekind_node_iriorliteral) + "\n" +
                           "Total sh:nodeKind property " + str(count_total_nodekind_property) + "\n" +
                           "Total sh:nodeKind property IRI " + str(count_total_nodekind_property_iri) + "\n" +
                           "Total sh:nodeKind property Literal " + str(count_total_nodekind_property_literal) + "\n" +
                           "Total sh:nodeKind property Blank node or IRI " + str(count_total_nodekind_property_blanknodeoriri) + "\n" +
                           "Total sh:nodeKind property IRI or literal  " + str(count_total_nodekind_property_iriorliteral) + "\n" +
                           "Total sh:minCount " + str(count_total_mincount) + "\n" +
                           "Total sh:minCount node " + str(count_total_mincount_node) + "\n" +
                           "Total sh:minCount property " + str(count_total_mincount_property) + "\n" +
                           "Total sh:maxCount " + str(count_total_maxcount) + "\n" +
                           "Total sh:maxCount node " + str(count_total_maxcount_node) + "\n" +
                           "Total sh:maxCount property " + str(count_total_maxcount_property) + "\n" +
                           "Total sh:minExclusive " + str(count_total_minexclusive) + "\n" +
                           "Total sh:minExclusive node " + str(count_total_minexclusive_node) + "\n" +
                           "Total sh:minExclusive property " + str(count_total_minexclusive_property) + "\n" +
                           "Total sh:minInclusive " + str(count_total_mininclusive) + "\n" +
                           "Total sh:minInclusive node " + str(count_total_mininclusive_node) + "\n" +
                           "Total sh:minInclusive property " + str(count_total_mininclusive_property) + "\n" +
                           "Total sh:maxExclusive " + str(count_total_maxexclusive) + "\n" +
                           "Total sh:maxExclusive node " + str(count_total_maxexclusive_node) + "\n" +
                           "Total sh:maxExclusive property " + str(count_total_maxexclusive_property) + "\n" +
                           "Total sh:maxInclusive " + str(count_total_maxinclusive) + "\n" +
                           "Total sh:maxInclusive node " + str(count_total_maxinclusive_node) + "\n" +
                           "Total sh:maxInclusive property " + str(count_total_maxinclusive_property) + "\n" +
                           "Total sh:minLength " + str(count_total_minlength) + "\n" +
                           "Total sh:minLength node " + str(count_total_minlength_node) + "\n" +
                           "Total sh:minLength property " + str(count_total_minlength_property) + "\n" +
                           "Total sh:maxLength " + str(count_total_maxlength) + "\n" +
                           "Total sh:maxLength node " + str(count_total_maxlength_node) + "\n" +
                           "Total sh:maxLength property " + str(count_total_maxlength_property) + "\n" +
                           "Total sh:pattern " + str(count_total_pattern) + "\n" +
                           "Total sh:pattern node " + str(count_total_pattern_node) + "\n" +
                           "Total sh:pattern property " + str(count_total_pattern_property) + "\n" +
                           "Total sh:languageIn " + str(count_total_languagein) + "\n" +
                           "Total sh:languageIn node " + str(count_total_languagein_node) + "\n" +
                           "Total sh:languageIn property " + str(count_total_languagein_property) + "\n" +
                           "Total sh:uniqueLang " + str(count_total_uniquelang) + "\n" +
                           "Total sh:uniqueLang node " + str(count_total_uniquelang_node) + "\n" +
                           "Total sh:uniqueLang property " + str(count_total_uniquelang_property) + "\n" +
                           "Total sh:equals " + str(count_total_equals) + "\n" +
                           "Total sh:equals node " + str(count_total_equals_node) + "\n" +
                           "Total sh:equals property " + str(count_total_equals_property) + "\n" +
                           "Total sh:disjoint " + str(count_total_disjoint) + "\n" +
                           "Total sh:disjoint node " + str(count_total_disjoint_node) + "\n" +
                           "Total sh:disjoint property " + str(count_total_disjoint_property) + "\n" +
                           "Total sh:lessThan " + str(count_total_lessthan) + "\n" +
                           "Total sh:lessThan node " + str(count_total_lessthan_node) + "\n" +
                           "Total sh:lessThan property " + str(count_total_lessthan_property) + "\n" +
                           "Total sh:lessThanOrEqual " + str(count_total_lessthanorequal) + "\n" +
                           "Total sh:lessThanOrEqual node " + str(count_total_lessthanorequal_node) + "\n" +
                           "Total sh:lessThanOrEqual property " + str(count_total_lessthanorequal_property) + "\n" +
                           "Total sh:not " + str(count_total_not) + "\n" +
                           "Total sh:not node " + str(count_total_not_node) + "\n" +
                           "Total sh:not property " + str(count_total_not_property) + "\n" +
                           "Total sh:and " + str(count_total_and) + "\n" +
                           "Total sh:and node " + str(count_total_and_node) + "\n" +
                           "Total sh:and property " + str(count_total_and_property) + "\n" +
                           "Total sh:or " + str(count_total_or) + "\n" +
                           "Total sh:or node " + str(count_total_or_node) + "\n" +
                           "Total sh:or property " + str(count_total_or_property) + "\n" +
                           "Total sh:xone " + str(count_total_xone) + "\n" +
                           "Total sh:xone node " + str(count_total_xone_node) + "\n" +
                           "Total sh:xone property " + str(count_total_xone_property) + "\n" +
                           "Total sh:node " + str(count_total_node) + "\n" +
                           "Total sh:node node " + str(count_total_node_node) + "\n" +
                           "Total sh:node property " + str(count_total_node_property) + "\n" +
                           "Total sh:property " + str(count_total_property) + "\n" +
                           "Total sh:property node " + str(count_total_property_node) + "\n" +
                           "Total sh:property property " + str(count_total_property_property) + "\n" +
                           "Total sh:qualifiedValueShape " + str(count_total_qualifiedvalueshape) + "\n" +
                           "Total sh:qualifiedValueShape node " + str(count_total_qualifiedvalueshape_node) + "\n" +
                           "Total sh:qualifiedValueShape property " + str(count_total_qualifiedvalueshape_property) + "\n" +
                           "Total sh:qualifiedMinCount " + str(count_total_qualifiedmincount) + "\n" +
                           "Total sh:qualifiedMinCount node " + str(count_total_qualifiedmincount_node) + "\n" +
                           "Total sh:qualifiedMinCount property " + str(count_total_qualifiedmincount_property) + "\n" +
                           "Total sh:qualifiedMaxCount " + str(count_total_qualifiedmaxcount) + "\n" +
                           "Total sh:qualifiedMaxCount node " + str(count_total_qualifiedmaxcount_node) + "\n" +
                           "Total sh:qualifiedMaxCount property " + str(count_total_qualifiedmaxcount_property) + "\n" +
                           "Total sh:closed " + str(count_total_closed) + "\n" +
                           "Total sh:closed node " + str(count_total_closed_node) + "\n" +
                           "Total sh:closed property " + str(count_total_closed_property) + "\n" +
                           "Total sh:ignoredProperties " + str(count_total_ignoredproperties) + "\n" +
                           "Total sh:ignoredProperties node " + str(count_total_ignoredproperties_node) + "\n" +
                           "Total sh:ignoredProperties property " + str(count_total_ignoredproperties_property) + "\n" +
                           "Total sh:hasValue " + str(count_total_hasvalue) + "\n" +
                           "Total sh:hasValue node " + str(count_total_hasvalue_node) + "\n" +
                           "Total sh:hasValue property " + str(count_total_hasvalue_property) + "\n" +
                           "Total sh:in " + str(count_total_in) + "\n" +
                           "Total sh:in node " + str(count_total_in_node) + "\n" +
                           "Total sh:in property " + str(count_total_in_property) + "\n" +
                           "Total sh:targetclass " + str(count_total_targetclass) + "\n" +
                           "Total sh:targetclass node " + str(count_total_targetclass_node) + "\n" +
                           "Total sh:targetclass property " + str(count_total_targetclass_property) + "\n" +
                           "Total sh:name " + str(count_total_name) + "\n" +
                           "Total sh:name node " + str(count_total_name_node) + "\n" +
                           "Total sh:name property " + str(count_total_name_property) + "\n" +
                           "Total sh:path " + str(count_total_path) + "\n" +
                           "Total sh:path nested " + str(count_total_path_nested) + "\n" +
                           "Total sh:path node " + str(count_total_path_node) + "\n" +
                           "Total sh:path node nested " + str(count_total_path_node_nested) + "\n" +
                           "Total sh:path property " + str(count_total_path_property) + "\n" +
                           "Total sh:path property nested " + str(count_total_path_property_nested) + "\n" +
                           "Total sh:inversePath " + str(count_total_inversepath) + "\n" +
                           "Total sh:inversePath node " + str(count_total_inversepath_node) + "\n" +
                           "Total sh:inversePath property " + str(count_total_inversepath_property) + "\n" +
                           "Total sh:description " + str(count_total_description) + "\n" +
                           "Total sh:description node " + str(count_total_description_node) + "\n" +
                           "Total sh:description property " + str(count_total_description_property) + "\n" +
                           "Total rdfs:label " + str(count_total_label) + "\n" +
                           "Total rdfs:label node " + str(count_total_label_node) + "\n" +
                           "Total rdfs:label property " + str(count_total_label_property) + "\n" +
                           "Total rdfs:seeAlso " + str(count_total_seealso) + "\n" +
                           "Total rdfs:seeAlso node " + str(count_total_seealso_node) + "\n" +
                           "Total rdfs:seeAlso property " + str(count_total_seealso_property) + "\n" +
                           "Total rdfs:isDefinedBy " + str(count_total_isdefinedby) + "\n" +
                           "Total rdfs:isDefinedBy node " + str(count_total_isdefinedby_node) + "\n" +
                           "Total rdfs:isDefinedBy property " + str(count_total_isdefinedby_property) + "\n" +
                           "Total rdf:type " + str(count_total_type) + "\n" +
                           "Total rdf:type node " + str(count_total_type_node) + "\n" +
                           "Total rdf:type property " + str(count_total_type_property) + "\n" +
                           "Total rdf:first (2) " + str(count_total_first) + "\n" +
                           "Total rdf:first node (2) " + str(count_total_first_node) + "\n" +
                           "Total rdf:first property (2) " + str(count_total_first_property) + "\n" +
                           "Total rdf:rest (2) " + str(count_total_rest) + "\n" +
                           "Total rdf:rest node (2) " + str(count_total_rest_node) + "\n" +
                           "Total rdf:rest property (2) " + str(count_total_rest_property) + "\n" +
                           "Total https://w3id.org/def/astrea#contains " + str(count_total_contains) + "\n" +
                           "Total https://w3id.org/def/astrea#contains node " + str(count_total_contains_node) + "\n" +
                           "Total https://w3id.org/def/astrea#contains property " + str(count_total_contains_property) + "\n" +
                           "Total https://w3id.org/def/astrea#generatedShapesFrom " + str(count_total_generatedshapesfrom) + "\n" +
                           "Total https://w3id.org/def/astrea#generatedShapesFrom node " + str(count_total_generatedshapesfrom_node) + "\n" +
                           "Total https://w3id.org/def/astrea#generatedShapesFrom property " + str(count_total_generatedshapesfrom_property) + "\n" +
                           "Total https://w3id.org/def/astrea#message " + str(count_total_message) + "\n" +
                           "Total https://w3id.org/def/astrea#message node " + str(count_total_message_node) + "\n" +
                           "Total https://w3id.org/def/astrea#message property " + str(count_total_message_property) + "\n" +
                           "Total https://w3id.org/def/astrea#statusCode " + str(count_total_statuscode) + "\n" +
                           "Total https://w3id.org/def/astrea#statusCode node " + str(count_total_statuscode_node) + "\n" +
                           "Total https://w3id.org/def/astrea#statusCode property " + str(count_total_statuscode_property) + "\n" +
                           "Total https://w3id.org/def/astrea#source " + str(count_total_source) + "\n" +
                           "Total https://w3id.org/def/astrea#source node " + str(count_total_source_node) + "\n" +
                           "Total https://w3id.org/def/astrea#source property " + str(count_total_source_property))
            path_parent = os.path.dirname(os.getcwd())
            os.chdir(path_parent)
    print("Analysis successfully concluded")


def main():

    # create_folders(clean=True)
    # input value clean = True to erase previous ontology and shapes folder before creating the new ones

    # divide('lov.nq')
    # input filename to divide into ontologies = "lov.nq" or "test.nq"...

    # convert_triple(filename='all')
    # converts input file .nq to .nt (main.py folder level) or all files with ='all' (Ontologies folder)

    # run_astrea(ontofile='all')
    # automatically generate shape files from filename or 'all' vocabularies with Astrea (same folder logic as above)

    analysis(shape='all')

    # TODO query all constraints for single file
    # TODO advanced calculations with results and graphs


if __name__ == '__main__':
    main()
