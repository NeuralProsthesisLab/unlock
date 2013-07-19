
import logging
import sys


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
        