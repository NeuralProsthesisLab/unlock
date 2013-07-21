
import atexit
import logging
from traceback import format_exc

import logging
import scope
import sys

PROTOTYPE = "scope.PROTOTYPE"
SINGLETON = "scope.SINGLETON"

def convert(scope_str):
    "This function converts the string-version of scope into the internal, enumerated version."
    if scope_str == "prototype":
        return PROTOTYPE
    elif scope_str == "singleton":
        return SINGLETON
    else:
        raise Exception("Can not handle scope %s" % s)
        
    

class ReflectiveObjectFactory(object):
    def __init__(self, module_and_class, factory_method):
        super(ReflectiveObjectFactory, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.module_and_class = module_and_class
        self.factory_method = factory_method

    def create_object(self, constr, named_constr):
        self.logger.debug("Creating an instance of %s" % self.module_and_class)
        parts = self.module_and_class.split(".")
        module_name = ".".join(parts[:-1])
        class_name = parts[-1]
        assert module_name != ""

        __import__(module_name)
        clazz = getattr(sys.modules[module_name], class_name)
        if self.factory_method:
            factory_method = getattr(clazz, self.factory_method)
            return factory_method(*constr, **named_constr)
        else:
            return clazz(*constr, **named_constr)

    def __str__(self):
        return "ReflectiveObjectFactory(%s)" % self.module_and_class
        
        
class ObjectContainer(object):
    """
    ObjectContainer is a container which uses multiple Config objects to read sources of
    object definitions. When a object is requested from this container, it may optionally
    pull the object from a scoped cache. If there is no stored copy of the object, it
    uses the scanned definition and its associated ObjectFactory to create an instance. It
    can then optionally store it in a scoped cache for future usage (e.g. singleton).
    
    Object definitions are stored in the container in a neutral format, decoupling the
    container entirely from the original source location. This means that XML, python code,
    and other formats may all contain definitions. By the time they
    reach this container, it doesn't matter what their original format was when a object
    instance is needed. NOTE: This explicitly means that one object in one source
    can refer to another object in another source OF ANY FORMAT as a property.
    """
    def __init__(self, config = None):
        self.logger = logging.getLogger(__name__)

        if config is None:
            self.configs = []
        elif isinstance(config, list):
            self.configs = config
        else:
            self.configs = [config]

        self.object_defs = {}
    
        for configuration in self.configs:
            self.logger.debug("=== Scanning configuration %s for object definitions ===" % configuration)
            for object_def in configuration.read_object_defs():
                if object_def.id not in self.object_defs:
                    self.logger.debug("%s object definition does not exist. Adding to list of definitions." % object_def.id)
                else:
                    self.logger.debug("Overriding previous definition of %s" % object_def.id)
                self.object_defs[object_def.id] = object_def

        self.logger.debug("=== Done reading object definitions. ===")

        self.objects = {}

    def get_object(self, name, ignore_abstract=False):
        """
        This function attempts to find the object in the singleton cache. If not found, 
        delegates to _create_object in order to hunt for the definition, and request a
        object factory to generate one.
        """
        try:
            object_def = self.object_defs[name]
            if object_def.abstract and not ignore_abstract:
                raise AbstractObjectException("Object [%s] is an abstract one." % name)
                
            return self.objects[name]
            
        except KeyError, e:
            self.logger.debug("Did NOT find object '%s' in the singleton storage." % name)
            try:
                object_def = self.object_defs[name]
                if object_def.abstract and not ignore_abstract:
                    raise AbstractObjectException("Object [%s] is an abstract one." % name)
                
                comp = self._create_object(object_def)
                
                # Evaluate any scopes, and store appropriately.
                if self.object_defs[name].scope == scope.SINGLETON:
                    self.objects[name] = comp
                    self.logger.debug("Stored object '%s' in container's singleton storage" % name)
                elif self.object_defs[name].scope == scope.PROTOTYPE:
                    pass
                else:
                    raise InvalidObjectScope("Don't know how to handle scope %s" % self.object_defs[name].scope)
                
                return comp
            except KeyError, e:
                self.logger.error("Object '%s' has no definition!" % name)
                raise e
            
    def _get_constructors_pos(self, object_def):
        """
        This function iterates over the positional constructors, and assembles their values into a list.
        In this situation, the order as read from the XML should be the order expected by the class
        definition.
        """
        return tuple([constr.get_value(self) for constr in object_def.pos_constr
                      if hasattr(constr, "get_value")])

    def _get_constructors_kw(self, kwargs):
        """
        This function iterates over the named constructors, and assembles their values into a list.
        In this situation, each argument is associated with a name, and due to unicode format provided
        by the XML parser, requires conversion into a new dictionary.
        """
        return dict([(key, kwargs[key].get_value(self)) for key in kwargs
                     if hasattr(kwargs[key], "get_value")])


    def _create_object(self, object_def):
        """
        If the object isn't stored in any scoped cache, and must instead be created, this method
        takes all the steps to read the object's definition, res it up, and store it in the appropriate
        scoped cache.
        """
        self.logger.debug("Creating an instance of %s" % object_def)
        
        [constr.prefetch(self) for constr in object_def.pos_constr if hasattr(constr, "prefetch")]
        [constr.prefetch(self) for constr in object_def.named_constr.values() if hasattr(constr, "prefetch")]
        [prop.prefetch(self) for prop in object_def.props if hasattr(prop, "prefetch")]
        
        # Res up an instance of the object, with ONLY constructor-based properties set.
        obj = object_def.factory.create_object(self._get_constructors_pos(object_def),
                                               self._get_constructors_kw(object_def.named_constr))

        # Fill in the other property values.
        [prop.set_value(obj, self) for prop in object_def.props if hasattr(prop, "set_value")]
        
        return obj
        
        
class AbstractObjectException(Exception):
    """ Raised when the user's code tries to get an abstract object from
    the container.
    """
    
class InvalidObjectScope(Exception):
    pass

class ApplicationContext(ObjectContainer):
    """
    ApplicationContext IS a ObjectContainer. It also has the ability to define the lifecycle of
    objects.
    """
    def __init__(self, config = None):
        super(ApplicationContext, self).__init__(config)
            
        atexit.register(self.shutdown_hook)
            
        self.logger = logging.getLogger(__name__)
        self.classnames_to_avoid = set(["PyroProxyFactory", "ProxyFactoryObject", "Pyro4ProxyFactory", "Pyro4FactoryObject"])
         
        for object_def in self.object_defs.values():
            self._apply(object_def)
            
        for configuration in self.configs:
            self._apply(configuration)
            
        for object_def in self.object_defs.values():
            if not object_def.lazy_init and object_def.id not in self.objects:
                self.logger.debug("Eagerly fetching %s" % object_def.id)
                self.get_object(object_def.id, ignore_abstract=True)
                
        post_processors = [object for object in self.objects.values() if isinstance(object, ObjectPostProcessor)]
        
        for obj_name, obj in self.objects.iteritems():
            if not isinstance(obj, ObjectPostProcessor):
                for post_processor in post_processors:
                    self.objects[obj_name] = post_processor.post_process_before_initialization(obj, obj_name)
                    
                    
        for object in self.objects.values():
            self._apply(object)
            
        for obj_name, obj in self.objects.iteritems():
            if not isinstance(obj, ObjectPostProcessor):
                for post_processor in post_processors:
                    self.objects[obj_name] = post_processor.post_process_after_initialization(obj, obj_name)
                    
    def _apply(self, obj):
        if not (obj.__class__.__name__ in self.classnames_to_avoid): 
            if hasattr(obj, "after_properties_set"):
                obj.after_properties_set()
            #if hasattr(obj, "post_process_after_initialization"):
            #    obj.post_process_after_initialization(self)
            if hasattr(obj, "set_app_context"):
                obj.set_app_context(self)
                
    def get_objects_by_type(self, type_, include_type=True):
        """ Returns all objects which are instances of a given type.
        If include_type is False then only instances of the type's subclasses
        will be returned.
        """
        result = {}
        for obj_name, obj in self.objects.iteritems():
            if isinstance(obj, type_):
                if include_type == False and type(obj) is type_:
                    continue
                result[obj_name] = obj
                
        return result
                
    def shutdown_hook(self):
        self.logger.debug("Invoking the destroy_method on registered objects")
        
        for obj_name, obj in self.objects.iteritems():
            if isinstance(obj, DisposableObject):
                try:
                    if hasattr(obj, "destroy_method"):
                        destroy_method_name = getattr(obj, "destroy_method")
                    else:
                        destroy_method_name = "destroy"
                        
                    destroy_method = getattr(obj, destroy_method_name)
                    
                except Exception, e:
                    self.logger.error("Could not destroy object '%s', exception '%s'" % (obj_name, format_exc()))
                    
                else:
                    if callable(destroy_method):
                        try:
                            self.logger.debug("About to destroy object '%s'" % obj_name)
                            destroy_method()
                            self.logger.debug("Successfully destroyed object '%s'" % obj_name)
                        except Exception, e:
                            self.logger.error("Could not destroy object '%s', exception '%s'" % (obj_name, format_exc()))
                    else:
                        self.logger.error("Could not destroy object '%s', " \
                            "the 'destroy_method' attribute it defines is not callable, " \
                            "its type is '%r', value is '%r'" % (obj_name, type(destroy_method), destroy_method))
                        
        self.logger.debug("Successfully invoked the destroy_method on registered objects")
            
            
class InitializingObject(object):
    """This allows definition of a method which is invoked by the container after an object has had all properties set."""
    def after_properties_set(self):
        pass

class ObjectPostProcessor(object):
    def post_process_before_initialization(self, obj, obj_name):
        return obj
    def post_process_after_initialization(self, obj, obj_name):
        return obj

class ApplicationContextAware(object):
    def __init__(self):
        self.app_context = None
        
    def set_app_context(self, app_context):
        self.app_context = app_context

class ObjectNameAutoProxyCreator(ApplicationContextAware, ObjectPostProcessor):
    """
    This object will iterate over a list of objects, and automatically apply
    a list of advisors to every callable method. This is useful when default advice
    needs to be applied widely with minimal configuration.
    """
    def __init__(self, objectNames = [], interceptorNames = []):
        super(ObjectNameAutoProxyCreator, self).__init__()
        self.objectNames = objectNames
        self.interceptorNames = interceptorNames

class DisposableObject(object):
    """ This allows definition of a method which is invoked when the 
    container's shutting down to release the resources held by an object.
    """
    def destroy(self):
        raise NotImplementedError("Should be overridden by subclasses")
