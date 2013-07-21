
try:
    import cElementTree as etree
except ImportError:
    try:
        import xml.etree.ElementTree as etree
    except ImportError:
        from elementtree import ElementTree as etree

import re
import types
import inspect
import logging


def get_string(value):
    """This function is used to parse text that could either be ASCII or unicode."""
    try:
        return str(value)
    except UnicodeEncodeError:
        return unicode(value)
        
class ObjectDef(object):
    """
    ObjectDef is a format-neutral way of storing object definition information. It includes
    a handle for the actual ObjectFactory that should be used to utilize this information when
    creating an instance of a object.
    """
    def __init__(self, id, props=None, factory=None, scope=context.SINGLETON,
                 lazy_init=False, abstract=False, parent=None):
        super(ObjectDef, self).__init__()
        self.id = id
        self.factory = factory
        if props is None:
            self.props = []
        else:
            self.props = props
        self.scope = scope
        self.lazy_init = lazy_init
        self.abstract = abstract
        self.parent = parent
        self.pos_constr = []
        self.named_constr = {}

    def __str__(self):
        return "id=%s props=%s scope=%s factory=%s" % (self.id, self.props, self.scope, self.factory)

class ReferenceDef(object):
    """
    This class represents a definition that is referencing another object.
    """
    def __init__(self, name, ref):
        self.name = name
        self.ref = ref

    def prefetch(self, container):
        self.get_value(container)

    def get_value(self, container):
        return container.get_object(self.ref)

    def set_value(self, obj, container):
        setattr(obj, self.name, container.objects[self.ref])

    def __str__(self):
        return "name=%s ref=%s" % (self.name, self.ref)

class InnerObjectDef(object):
    """
    This class represents an inner object. It is optional whether or not the object
    has its own name.
    """
    def __init__(self, name, inner_comp):
        self.name = name
        self.inner_comp = inner_comp

    def prefetch(self, container):
        self.get_value(container)

    def get_value(self, container):
        return container.get_object(self.inner_comp.id)

    def set_value(self, obj, container):
        setattr(obj, self.name, self.get_value(container))

    def __str__(self):
        return "name=%s inner_comp=%s" % (self.name, self.inner_comp)

class ValueDef(object):
    """
    This class represents a property that holds a value. The value can be simple value, or
    it can be a complex container which internally holds references, inner objects, or
    any other type.
    """
    def __init__(self, name, value):
        self.name = name
        if value == "True":
            self.value = True
        elif value == "False":
            self.value= False
        else:
            self.value = value
        self.logger = logging.getLogger(__name__)

    def scan_value(self, container, value):
        if hasattr(value, "get_value"):
            return value.get_value(container)
        elif isinstance(value, tuple):
            new_list = [self.scan_value(container, item) for item in value]
            results = tuple(new_list)
            return results
        elif isinstance(value, list):
            new_list = [self.scan_value(container, item) for item in value]
            return new_list
        elif isinstance(value, set):
            results = set([self.scan_value(container, item) for item in value])
            return results
        elif isinstance(value, frozenset):
            results = frozenset([self.scan_value(container, item) for item in value])
            return results
        else:
            if value == "True":
                return True
            elif value == "False":
                return False
            else:
                return value

    def get_value(self, container):
        val = self._replace_refs_with_actuals(self.value, container)
        if val is None:
            return self.value
        else:
            return val

    def set_value(self, obj, container):
        setattr(obj, self.name, self.value)
        val = self._replace_refs_with_actuals(obj, container)

    def _replace_refs_with_actuals(self, obj, container):
        """Normal values do nothing for this step. However, sub-classes are defined for
        the various containers, like lists, set, dictionaries, etc., to handle iterating
        through and pre-fetching items."""
        pass

    def __str__(self):
        return "name=%s value=%s" % (self.name, self.value)

class DictDef(ValueDef):
    """Handles behavior for a dictionary-based value."""
    def __init__(self, name, value):
        super(DictDef, self).__init__(name, value)

    def _replace_refs_with_actuals(self, obj, container):
        for key in self.value.keys():
            if hasattr(self.value[key], "ref"):
                self.value[key] = container.get_object(self.value[key].ref)
            else:
                self.value[key] = self.scan_value(container, self.value[key])

class ListDef(ValueDef):
    """Handles behavior for a list-based value."""
    def __init__(self, name, value):
        super(ListDef, self).__init__(name, value)
        self.logger = logging.getLogger(__name__)

    def _replace_refs_with_actuals(self, obj, container):
        for i in range(0, len(self.value)):
            self.logger.debug("Checking out %s, wondering if I need to do any replacement..." % get_string(self.value[i]))
            if hasattr(self.value[i], "ref"):
                self.value[i] = container.get_object(self.value[i].ref)
            else:
                self.value[i] = self.scan_value(container, self.value[i])

class TupleDef(ValueDef):
    """Handles behavior for a tuple-based value."""

    def __init__(self, name, value):
        super(TupleDef, self).__init__(name, value)

    def _replace_refs_with_actuals(self, obj, container):
        new_value = list(self.value)
        for i in range(0, len(new_value)):
            if hasattr(new_value[i], "ref"):
                new_value[i] = container.get_object(new_value[i].ref)
            else:
                new_value[i] = self.scan_value(container, new_value[i])
        try:
            setattr(obj, self.name, tuple(new_value))
        except AttributeError:
            pass
        return tuple(new_value)

class SetDef(ValueDef):
    """Handles behavior for a set-based value."""
    def __init__(self, name, value):
        super(SetDef, self).__init__(name, value)
        self.logger = logging.getLogger(__name__)

    def _replace_refs_with_actuals(self, obj, container):
        self.logger.debug("Replacing refs with actuals...")
        self.logger.debug("set before changes = %s" % self.value)
        new_set = set()
        for item in self.value:
            if hasattr(item, "ref"):
                self.logger.debug("Item !!!%s!!! is a ref, trying to replace with actual object !!!%s!!!" % (item, item.ref))
                #self.value.remove(item)
                #self.value.add(container.get_object(item.ref))
                newly_fetched_value = container.get_object(item.ref)
                new_set.add(newly_fetched_value)
                self.logger.debug("Item !!!%s!!! was removed, and newly fetched value !!!%s!!! was added." % (item, newly_fetched_value))
                #new_set.add(container.get_object(item.ref))
            else:
                self.logger.debug("Item !!!%s!!! is NOT a ref, trying to replace with scanned value" % get_string(item))
                #self.value.remove(item)
                #self.value.add(self.scan_value(container, item))
                newly_scanned_value = self.scan_value(container, item)
                new_set.add(newly_scanned_value)
                self.logger.debug("Item !!!%s!!! was removed, and newly scanned value !!!%s!!! was added." % (item, newly_scanned_value))
                #new_set.add(self.scan_value(container, item))
        #self.value = new_set
        self.logger.debug("set after changes = %s" % new_set)
        #return self.value
        try:
            setattr(obj, self.name, new_set)
        except AttributeError:
            pass
        return new_set

class FrozenSetDef(ValueDef):
    """Handles behavior for a frozen-set-based value."""
    def __init__(self, name, value):
        super(FrozenSetDef, self).__init__(name, value)
        self.logger = logging.getLogger(__name__)

    def _replace_refs_with_actuals(self, obj, container):
        self.logger.debug("Replacing refs with actuals...")
        self.logger.debug("set before changes = %s" % self.value)
        new_set = set()
        for item in self.value:
            if hasattr(item, "ref"):
                self.logger.debug("Item <<<%s>>> is a ref, trying to replace with actual object <<<%s>>>" % (item, item.ref))
                #new_set.remove(item)
                #debug begin
                newly_fetched_value = container.get_object(item.ref)
                new_set.add(newly_fetched_value)
                self.logger.debug("Item <<<%s>>> was removed, and newly fetched value <<<%s>>> was added." % (item, newly_fetched_value))
                #debug end
                #new_set.add(container.get_object(item.ref))
            else:
                self.logger.debug("Item <<<%s>>> is NOT a ref, trying to replace with scanned value" % get_string(item))
                #new_set.remove(item)
                #debug begin
                newly_scanned_value = self.scan_value(container, item)
                new_set.add(newly_scanned_value)
                self.logger.debug("Item <<<%s>>> was removed, and newly scanned value <<<%s>>> was added." % (item, newly_scanned_value))
                #debug end
                #new_set.add(self.scan_value(container, item))
        #self.logger.debug("Newly built set = %s" % new_set)
        #self.value = frozenset(new_set)
        new_frozen_set = frozenset(new_set)
        self.logger.debug("set after changes = %s" % new_frozen_set)
        #return self.value
        try:
            setattr(obj, self.name, new_frozen_set)
        except AttributeError:
            pass
        except TypeError:
            pass
        return new_frozen_set
        
        
class Config(object):
    """
    Config is an interface that defines how to read object definitions from an input source.
    """
    def read_object_defs(self):
        """Abstract method definition - should return an array of Object objects"""
        raise NotImplementedError()
        
        
xml_mappings = {
    "str":"types.StringType", "unicode":"types.UnicodeType",
    "int":"types.IntType", "long":"types.LongType",
    "float":"types.FloatType", "decimal":"decimal.Decimal",
    "bool":"types.BooleanType", "complex":"types.ComplexType",
}

class XMLConfig(Config):
    """
    XMLConfig supports current Spring Python format of XML object definitions.
    """

    NS = ''#"{http://www.springframework.org/springpython/schema/objects}"
    NS_11 = ''#"{http://www.springframework.org/springpython/schema/objects/1.1}"

    def __init__(self, config_location):
        if isinstance(config_location, list):
            self.config_location = config_location
        else:
            self.config_location = [config_location]
        self.logger = logging.getLogger(__name__)

        # By making this an instance-based property (instead of function local), inner object
        # definitions can add themselves to the list in the midst of parsing an input.
        self.objects = []

    def read_object_defs(self):
        self.logger.debug("==============================================================")
        # Reset, in case the file is re-read
        self.objects = []
        for config in self.config_location:
            self.logger.debug("* Parsing %s" % config)

            # A flat list of objects, as found in the XML document.
            objects = etree.parse(config).getroot()

            # We need to handle both 1.0 and 1.1 XSD schemata *and* we may be
            # passed a list of config locations of different XSD versions so we
            # must find out here which one is used in the current config file
            # and pass the correct namespace down to other parts of XMLConfig.
            ns = objects.tag[:objects.tag.find("}") + 1]

            # A dictionary of abstract objects, keyed by their IDs, used in
            # traversing the hierarchies of parents; built upfront here for
            # convenience.
            abstract_objects = {}
            for obj in objects:
                if obj.get("abstract"):
                    abstract_objects[obj.get("id")] = obj

            for obj in objects:
                if obj.get("class") is None and not obj.get("parent"):
                    self._map_custom_class(obj, xml_mappings, ns)

                elif obj.get("parent"):
                    # Children are added to self.objects during the children->abstract parents traversal.
                    pos_constr = self._get_pos_constr(obj, ns)
                    named_constr = self._get_named_constr(obj, ns)
                    props = self._get_props(obj, ns)
                    self._traverse_parents(obj, obj, ns, pos_constr, named_constr, props, abstract_objects)
                    continue

                self.objects.append(self._convert_object(obj, ns=ns))

        self.logger.debug("==============================================================")
        for object in self.objects:
            self.logger.debug("Parsed %s" % object)
        return self.objects

    def _map_custom_class(self, obj, mappings, ns):
        """ Fill in the missing attributes of Python objects and make it look
        to the rest of XMLConfig as if they already were in the XML config file.
        """
        for class_name in mappings:
            tag_no_ns = obj.tag.replace(ns, "")
            if class_name == tag_no_ns:

                obj.set("class", mappings[class_name])
                constructor_arg = etree.Element("%s%s" % (ns, "constructor-arg"))
                value = etree.Element("%s%s" % (ns, "value"))
                value.text = obj.text
                obj.append(constructor_arg)
                constructor_arg.append(value)
                obj.text = ""

                break

        else:
            self.logger.warning("No matching type found for object %s" % obj)

    def _traverse_parents(self, leaf, child, ns, pos_constr,
                            named_constr, props, abstract_objects):

        parent = abstract_objects[child.get("parent")]

        # At this point we only build up the lists of parameters but we don't create
        # the object yet because the current parent object may still have its
        # own parent.

        # Positional constructors

        parent_pos_constrs = self._get_pos_constr(parent, ns)

        # Make sure there are as many child positional parameters as there
        # are in the parent's list.

        len_pos_constr = len(pos_constr)
        len_parent_pos_constrs = len(parent_pos_constrs)

        if len_pos_constr < len_parent_pos_constrs:
            pos_constr.extend([None] * (len_parent_pos_constrs - len_pos_constr))

        for idx, parent_pos_constr in enumerate(parent_pos_constrs):
            if not pos_constr[idx]:
                pos_constr[idx] = parent_pos_constr

        # Named constructors
        child_named_constrs = named_constr
        parent_named_constrs = self._get_named_constr(parent, ns)

        for parent_named_constr in parent_named_constrs:
            if parent_named_constr not in child_named_constrs:
                named_constr[parent_named_constr] = parent_named_constrs[parent_named_constr]

        # Properties
        child_props = [prop.name for prop in props]
        parent_props = self._get_props(parent, ns)

        for parent_prop in parent_props:
            if parent_prop.name not in child_props:
                props.append(parent_prop)

        if parent.get("parent"):
            self._traverse_parents(leaf, parent, ns, pos_constr, named_constr, props, abstract_objects)
        else:
            # Now we know we can create an object out of all the accumulated values.

            # The object's class is its topmost parent's class.
            class_ = parent.get("class")
            id, factory, lazy_init, abstract, parent, scope_ = self._get_basic_object_data(leaf, class_)

            c = self._create_object(id, factory, lazy_init, abstract, parent,
                           scope_, pos_constr, named_constr, props)

            self.objects.append(c)

        return parent

    def _get_pos_constr(self, object, ns):
        """ Returns a list of all positional constructor arguments of an object.
        """
        return [self._convert_prop_def(object, constr, object.get("id") + ".constr", ns) for constr in object.findall(ns+"constructor-arg")
                if not "name" in constr.attrib]

    def _get_named_constr(self, object, ns):
        """ Returns a dictionary of all named constructor arguments of an object.
        """
        return dict([(str(constr.get("name")), self._convert_prop_def(object, constr, object.get("id") + ".constr", ns))
                    for constr in object.findall(ns+"constructor-arg")  if "name" in constr.attrib])

    def _get_props(self, object, ns):
        """ Returns a list of all properties defined by an object.
        """
        return [self._convert_prop_def(object, p, p.get("name"), ns) for p in object.findall(ns+"property")]

    def _create_object(self, id, factory, lazy_init, abstract, parent,
                           scope, pos_constr, named_constr, props):
        """ A helper function which creates an object out of the supplied
        arguments.
        """

        c = ObjectDef(id=id, factory=factory, lazy_init=lazy_init,
            abstract=abstract, parent=parent)

        c.scope = scope
        c.pos_constr = pos_constr
        c.named_constr = named_constr
        c.props = props

        self.logger.debug("object: props = %s" % c.props)
        self.logger.debug("object: There are %s props" % len(c.props))

        return c

    def _get_basic_object_data(self, object, class_):
        """ A convenience method which creates basic object's data so that
        the code is not repeated.
        """

        if "scope" in object.attrib:
            scope_ = context.convert(object.get("scope"))
        else:
            scope_ = context.SINGLETON
        
        return(object.get("id"),  ReflectiveObjectFactory(class_, object.get("factory_method")),
            object.get("lazy-init", False), object.get("abstract", False),
               object.get("parent"), scope_)

    def _convert_object(self, object, prefix="", ns=None):
        """ This function collects all parameters required for an object creation
        and then calls a helper function which creates it.
        """
        if prefix != "":
            if "id" in object.attrib:
                object.set("id", prefix + "." + object.get("id"))
            else:
                object.set("id", prefix + ".<anonymous>")

        id, factory, lazy_init, abstract, parent, scope_ = self._get_basic_object_data(object, object.get("class"))

        pos_constr = self._get_pos_constr(object, ns)
        named_constr = self._get_named_constr(object, ns)
        props = self._get_props(object, ns)

        return self._create_object(id, factory, lazy_init, abstract, parent,
            scope_, pos_constr, named_constr, props)

    def _convert_ref(self, ref_node, name):
        if hasattr(ref_node, "attrib"):
            results = ReferenceDef(name, ref_node.get("object"))
            self.logger.debug("ref: Returning %s" % results)
            return results
        else:
            results = ReferenceDef(name, ref_node)
            self.logger.debug("ref: Returning %s" % results)
            return results

    def _convert_value(self, value, id, name, ns):
        if value.text is not None and value.text.strip() != "":
            self.logger.debug("value: Converting a direct value <%s>" % value.text)
            return value.text
        else:
            if value.tag == ns+"value":
                self.logger.debug("value: Converting a value's children %s" % value.getchildren()[0])
                results = self._convert_value(value.getchildren()[0], id, name, ns)
                self.logger.debug("value: results = %s" % str(results))
                return results
            elif value.tag == ns+"tuple":
                self.logger.debug("value: Converting a tuple")
                return self._convert_tuple(value, id, name, ns).value
            elif value.tag == ns+"list":
                self.logger.debug("value: Converting a list")
                return self._convert_list(value, id, name, ns).value
            elif value.tag == ns+"dict":
                self.logger.debug("value: Converting a dict")
                return self._convert_dict(value, id, name, ns).value
            elif value.tag == ns+"set":
                self.logger.debug("value: Converting a set")
                return self._convert_set(value, id, name, ns).value
            elif value.tag == ns+"frozenset":
                self.logger.debug("value: Converting a frozenset")
                return self._convert_frozen_set(value, id, name, ns).value
            else:
                self.logger.debug("value: %s.%s Don't know how to handle %s" % (id, name, value.tag))

    def _convert_dict(self, dict_node, id, name, ns):
        dict = {}
        for entry in dict_node.findall(ns+"entry"):
            self.logger.debug("dict: entry = %s" % entry)
            key = entry.find(ns+"key").find(ns+"value").text
            self.logger.debug("dict: key = %s" % key)
            if entry.find(ns+"value") is not None:
                dict[key] = self._convert_value(entry.find(ns+"value"), id, "%s.dict['%s']" % (name, key), ns)
            elif entry.find(ns+"ref") is not None:
                dict[key] = self._convert_ref(entry.find(ns+"ref"), "%s.dict['%s']" % (name, key))
            elif entry.find(ns+"object") is not None:
                self.logger.debug("dict: Parsing an inner object definition...")
                dict[key] = self._convert_inner_object(entry.find(ns+"object"), id, "%s.dict['%s']" % (name, key), ns)
            else:
                for token in ["dict", "tuple", "set", "frozenset", "list"]:
                    if entry.find(ns+token) is not None:
                        dict[key] = self._convert_value(entry.find(ns+token), id, "%s.dict['%s']" % (name, key), ns)
                        break
                if key not in dict:
                    self.logger.debug("dict: Don't know how to handle %s" % entry.tag)

        self.logger.debug("Dictionary is now %s" % dict)
        return DictDef(name, dict)

    def _convert_props(self, props_node, name, ns):
        dict = {}
        self.logger.debug("props: Looking at %s" % props_node)
        for prop in props_node:
            dict[prop.get("key")] = str(prop.text)
        self.logger.debug("props: Dictionary is now %s" % dict)
        return DictDef(name, dict)

    def _convert_list(self, list_node, id, name, ns):
        list = []
        self.logger.debug("list: Parsing %s" % list_node)
        for element in list_node:
            if element.tag == ns+"value":
                list.append(get_string(element.text))
            elif element.tag == ns+"ref":
                list.append(self._convert_ref(element, "%s.list[%s]" % (name, len(list))))
            elif element.tag == ns+"object":
                self.logger.debug("list: Parsing an inner object definition...")
                list.append(self._convert_inner_object(element, id, "%s.list[%s]" % (name, len(list)), ns))
            elif element.tag in [ns+token for token in ["dict", "tuple", "set", "frozenset", "list"]]:
                self.logger.debug("This list has child elements of type %s." % element.tag)
                list.append(self._convert_value(element, id, "%s.list[%s]" % (name, len(list)), ns))
                self.logger.debug("List is now %s" % list)
            else:
                self.logger.debug("list: Don't know how to handle %s" % element.tag)
        self.logger.debug("List is now %s" % list)
        return ListDef(name, list)

    def _convert_tuple(self, tuple_node, id, name, ns):
        list = []
        self.logger.debug("tuple: Parsing %s" % tuple_node)
        for element in tuple_node:
            self.logger.debug("tuple: Looking at %s" % element)
            if element.tag == ns+"value":
                self.logger.debug("tuple: Appending %s" % element.text)
                list.append(get_string(element.text))
            elif element.tag == ns+"ref":
                list.append(self._convert_ref(element, "%s.tuple(%s}" % (name, len(list))))
            elif element.tag == ns+"object":
                self.logger.debug("tuple: Parsing an inner object definition...")
                list.append(self._convert_inner_object(element, id, "%s.tuple(%s)" % (name, len(list)), ns))
            elif element.tag in [ns+token for token in ["dict", "tuple", "set", "frozenset", "list"]]:
                self.logger.debug("tuple: This tuple has child elements of type %s." % element.tag)
                list.append(self._convert_value(element, id, "%s.tuple(%s)" % (name, len(list)), ns))
                self.logger.debug("tuple: List is now %s" % list)
            else:
                self.logger.debug("tuple: Don't know how to handle %s" % element.tag)
        self.logger.debug("Tuple is now %s" % str(tuple(list)))
        return TupleDef(name, tuple(list))

    def _convert_set(self, set_node, id, name, ns):
        s = set()
        self.logger.debug("set: Parsing %s" % set_node)
        for element in set_node:
            self.logger.debug("Looking at element %s" % element)
            if element.tag == ns+"value":
                s.add(get_string(element.text))
            elif element.tag == ns+"ref":
                s.add(self._convert_ref(element, name + ".set"))
            elif element.tag == ns+"object":
                self.logger.debug("set: Parsing an inner object definition...")
                s.add(self._convert_inner_object(element, id, "%s.set(%s)" % (name, len(s)), ns))
            elif element.tag in [ns+token for token in ["dict", "tuple", "set", "frozenset", "list"]]:
                self.logger.debug("set: This set has child elements of type %s." % element.tag)
                s.add(self._convert_value(element, id, "%s.set(%s)" % (name,len(s)), ns))
            else:
                self.logger.debug("set: Don't know how to handle %s" % element.tag)
        self.logger.debug("Set is now %s" % s)
        return SetDef(name, s)

    def _convert_frozen_set(self, frozen_set_node, id, name, ns):
        item = self._convert_set(frozen_set_node, id, name, ns)
        self.logger.debug("frozenset: Frozen set is now %s" % frozenset(item.value))
        return FrozenSetDef(name, frozenset(item.value))

    def _convert_inner_object(self, object_node, id, name, ns):
        inner_object_def = self._convert_object(object_node, prefix="%s.%s" % (id, name), ns=ns)
        self.logger.debug("innerobj: Innerobject is now %s" % inner_object_def)
        self.objects.append(inner_object_def)
        return InnerObjectDef(name, inner_object_def)

    def _convert_prop_def(self, comp, p, name, ns):
        "This function translates object properties into useful collections of information for the container."
        #self.logger.debug("Is %s.%s a ref? %s" % (comp.get("id"), p.get("name"), p.find(ns+"ref") is not None or "ref" in p.attrib))
        #self.logger.debug("Is %s.%s a value? %s" % (comp.get("id"), p.get("name"), p.find(ns+"value") is not None or "value" in p.attrib))
        #self.logger.debug("Is %s.%s an inner object? %s" % (comp.get("id"), p.get("name"), p.find(ns+"object") is not None or "object" in p.attrib))
        #self.logger.debug("Is %s.%s a dict? %s" % (comp.get("id"), p.get("name"), p.find(ns+"dict") is not None or "dict" in p.attrib))
        #self.logger.debug("Is %s.%s a list? %s" % (comp.get("id"), p.get("name"), p.find(ns+"list") is not None or "list" in p.attrib))
        #self.logger.debug("Is %s.%s a tuple? %s" % (comp.get("id"), p.get("name"), p.find(ns+"tuple") is not None or "tuple" in p.attrib))
        #self.logger.debug("Is %s.%s a set? %s" % (comp.get("id"), p.get("name"), p.find(ns+"set") is not None or "set" in p.attrib))
        #self.logger.debug("Is %s.%s a frozenset? %s" % (comp.get("id"), p.get("name"), p.find(ns+"frozenset") is not None or "frozenset" in p.attrib))
        #self.logger.debug("")
        if "ref" in p.attrib or p.find(ns+"ref") is not None:
            if "ref" in p.attrib:
                return self._convert_ref(p.get("ref"), name)
            else:
                return self._convert_ref(p.find(ns+"ref"), name)
        elif "value" in p.attrib or p.find(ns+"value") is not None:
            if "value" in p.attrib:
                return ValueDef(name, get_string(p.get("value")))
            else:
                return ValueDef(name, get_string(p.find(ns+"value").text))
        elif "dict" in p.attrib or p.find(ns+"dict") is not None:
            if "dict" in p.attrib:
                return self._convert_dict(p.get("dict"), comp.get("id"), name, ns)
            else:
                return self._convert_dict(p.find(ns+"dict"), comp.get("id"), name, ns)
        elif "props" in p.attrib or p.find(ns+"props") is not None:
            if "props" in p.attrib:
                return self._convert_props(p.get("props"), name, ns)
            else:
                return self._convert_props(p.find(ns+"props"), name, ns)
        elif "list" in p.attrib or p.find(ns+"list") is not None:
            if "list" in p.attrib:
                return self._convert_list(p.get("list"), comp.get("id"), name, ns)
            else:
                return self._convert_list(p.find(ns+"list"), comp.get("id"), name, ns)
        elif "tuple" in p.attrib or p.find(ns+"tuple") is not None:
            if "tuple" in p.attrib:
                return self._convert_tuple(p.get("tuple"), comp.get("id"), name, ns)
            else:
                return self._convert_tuple(p.find(ns+"tuple"), comp.get("id"), name, ns)
        elif "set" in p.attrib or p.find(ns+"set") is not None:
            if "set" in p.attrib:
                return self._convert_set(p.get("set"), comp.get("id"), name, ns)
            else:
                return self._convert_set(p.find(ns+"set"), comp.get("id"), name, ns)
        elif "frozenset" in p.attrib or p.find(ns+"frozenset") is not None:
            if "frozenset" in p.attrib:
                return self._convert_frozen_set(p.get("frozenset"), comp.get("id"), name, ns)
            else:
                return self._convert_frozen_set(p.find(ns+"frozenset"), comp.get("id"), name, ns)
        elif "object" in p.attrib or p.find(ns+"object") is not None:
            if "object" in p.attrib:
                return self._convert_inner_object(p.get("object"), comp.get("id"), name, ns)
            else:
                return self._convert_inner_object(p.find(ns+"object"), comp.get("id"), name, ns)

