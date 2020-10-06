from rdflib import Graph, Namespace
from rdflib.namespace import RDF, SH

from rdf_metadata_properties import to_datatype, from_datatype

HSTERMS = Namespace("http://hydroshare.org/terms/")


class RDFNestedProperty:
    '''
    A property to allow us to do validation at assignment
    '''
    def __init__(self, property_name):
        '''
        :param property_name: The name of the property
        '''
        self.property_name = property_name
        self.private_property = "_" + property_name

    def __get__(self, instance, owner):
        return getattr(instance, self.private_property)

    def __set__(self, instance, value):
        return setattr(instance, self.private_property, value)

    def __delete__(self, instance):
        setattr(instance, self.private_property, None)


class RDFProperty:
    '''
    A property to allow us to do validation at assignment
    '''
    def __init__(self, property_name):
        '''
        :param property_name: The name of the property
        '''
        self.property_name = property_name
        self.private_property = "_" + property_name

    def __get__(self, instance, owner):
        return getattr(instance, self.private_property)

    def __set__(self, instance, value):
        return setattr(instance, self.private_property, value)

    def __delete__(self, instance):
        setattr(instance, self.private_property, None)

class AbstractRDFMetadata:
    _paths = None
    _data_types = None
    _max_counts = None
    _target_class = None

    def __init__(self, metadata_graph):
        target_class = self._target_class
        root_subject = metadata_graph.value(predicate=RDF.type, object=target_class)
        paths = self._paths
        for property_name, term in paths.items():
            data_type = self._data_types[property_name]
            value = [from_datatype(prop_value, data_type)
                        for prop_value in
                        metadata_graph.objects(subject=root_subject, predicate=term)]
            #attr = getattr(self, property_name)
            setattr(self, property_name, str(value))
            #attr = value

    @staticmethod
    def rdf_path(name):
        return AbstractRDFMetadata._paths[name]

    @staticmethod
    def rdf_datatype(name):
        return AbstractRDFMetadata._data_types[name]

    @staticmethod
    def rdf_maxCount(name):
        return AbstractRDFMetadata._max_counts[name]

shacl_graph = Graph().parse('tests/data/HSResource_SHACL.ttl', format='turtle')

shape_by_targetClass = {}
property_by_path = {}
# class names
for subject in shacl_graph.subjects(RDF.type, SH.NodeShape):
    schema_name = shacl_graph.value(subject, SH.name)
    target_class = shacl_graph.value(subject, SH.targetClass)

    paths = {}
    data_types = {}
    max_counts = {}
    attributes = {}
    for prop in shacl_graph.objects(subject, SH.property):
        name = shacl_graph.value(prop, SH.name).value
        path = shacl_graph.value(prop, SH.path)
        paths[name] = path
        max_count = shacl_graph.value(prop, SH.maxCount)
        max_counts[name] = max_count
        min_count = shacl_graph.value(prop, SH.minCount)
        attributes[name] = RDFProperty(name)
        data_type = shacl_graph.value(prop, SH.datatype)
        data_types[name] = data_type

    shape_class = type(schema_name, (AbstractRDFMetadata, ), {'_target_class': target_class,
                                                              '_paths': paths,
                                                              '_data_types': data_types,
                                                              '_max_counts': max_counts,
                                                              **attributes})
    shape_by_targetClass[target_class] = shape_class


metadata_graph = Graph().parse('tests/data/resource.ttl', format='turtle')

res_class = shape_by_targetClass[HSTERMS.resource]
res = res_class(metadata_graph)
print(dir(res))
print(res.title)
print(res.subject)
res.title = "changed"
print(res.title)