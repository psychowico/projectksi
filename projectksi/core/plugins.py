import inspect
from importlib import import_module
import collections

class ServiceLocator(object):
    """ Simple implementation of ServiceLocator pattern. It provide minimalistic
    functionality to fetching and storing services + *create_alias* method for create
    services aliases.
    """
    services = None
    aliases = None
    stored_results = None

    def __init__(self):
        self.services = {}
        self.aliases = {}
        self.stored_results = {}

    def _resolve_to_key(self, key_or_alias):
        while key_or_alias in self.aliases:
            key_or_alias = self.aliases[key_or_alias]
        return key_or_alias

    def has(self, key_or_alias):
        key = self._resolve_to_key(key_or_alias)
        return key in self.services

    def get(self, key_or_alias):
        key = self._resolve_to_key(key_or_alias)
        if not key in self.services:
            raise KeyError("Service %s not found!" % key_or_alias)
        if key not in self.stored_results:
            self.stored_results[key] = self.services[key]()
        return self.stored_results[key]

    def set(self, key, service, can_override = False):
        if len(key) == 0:
            raise NameError("Value key can not be empty!")
        if not isinstance(service, collections.Callable):
            raise ValueError("Argument service must be callable value (key '%s'." % key)
        if not can_override and key in self.services:
            raise KeyError("Service %s exists, you can not override it!" % key)
        if key in self.aliases:
            raise KeyError("Alias with key '%s' exists, "
                           "you can not create service with this name!" % key)
        self.services[key] = service

    def create_alias(self, alias, key_or_alias):
        if len(alias) == 0:
            raise NameError("Value alias can not be empty!")
        if alias in self.services or alias in self.aliases:
            raise KeyError("Alias or service with name '%s' already exists!" % alias)
        if key_or_alias not in self.services and key_or_alias not in self.aliases:
            raise KeyError("Service '%s' not found!" % alias)
        self.aliases[alias] = key_or_alias

class PluginAbstract(object):
    """ Base class that should be implemented in all plugins added to game. It is
    provided few methods and information that give our more control for plugins management.
    """

    service_locator = None

    def unique_name(self):
        """ Plugin base name
        """
        raise NotImplementedError()

    def readable_name(self):
        """ Human readable plugin name, for printing pursposes
        """
        return self.unique_name()

    def name(self):
        """ Only shortcut to "readable_name" method
        """
        return self.readable_name()

    def depending(self):
        """ tuple of unique_name without which this particular plugin can not working
        """
        return ()

    def services_depending(self):
        """ tuple of service keys without which this particular plugin can not working.
        this will be visible for debug purposes.
        """
        return ()

    def description(self):
        """ Plugin description, should have human readable info about what exacly this plugin divmod
        """
        raise NotImplementedError()

    def includeme(self, config, service_locator):
        """ This method will be called by PluginsManager as end of loading plugin. It provid "config"
        object for plugin, so it can register his own views and make any configuration (you should check
        pyramid documentation for more info). Do not forgot about calling *config.scan()* at end of this
        method if you want you plugin to have *declarative* based views support. Additionally it provide
        access to service_locator object, responsible for plugins communications.
        """
        raise NotImplementedError()

class PluginsManager(object):
    plugins = None
    service_locator = None

    def __init__(self, config):
        self.config = config
        self.plugins = {}
        self.service_locator = ServiceLocator()
        self._register_plugins(config)
        #config.action('register_plugins', self._register_plugins, args=(config,), introspectables=(intr,) )

    def _register_plugins(self, config):
        """ This method looking for 'projectksi.plugins' configuration entry.
        If it exist, it should contains plugins list that will be treated as
        projectksi plugins plugins. Method will be looking for class derived
        from "PluginAbstract" class, if it will not found it, exception will be
        raised. For all founded plugins it will register introspectable in
        "projectksi plugins" group and run "includeme" plugin method.
        """
        plugins = {}
        introspectables = []
        p_str = config.registry.settings.get('projectksi.plugins', '' )
        p_list = p_str.split()
        for plugin_path in p_list:
            mod = import_module(plugin_path)

            classes = inspect.getmembers(mod, inspect.isclass)
            plugin_classes = [c[1] for c in classes if issubclass(c[1], PluginAbstract)]
            if(len(plugin_classes) > 1):
                raise Exception('More that one class derivered'
                                ' by PluginAbstract founded in "%s" plugin.' % plugin_path)
            elif(len(plugin_classes) == 0):
                raise Exception('Plugins "%s" need have one class derivered '
                                'by PluginAbstract in his __init__.py file.' % plugin_path)
            plugin_class = plugin_classes[0]

            plugin = plugin_class()
            plugin_name = plugin.name()
            plugins[plugin_name] = plugin

            intr = config.introspectable(category_name='projectksi plugins',
                                 discriminator=( 'plugin', plugin_name ),
                                 title=('<%s>' % plugin.unique_name()),
                                 type_name='projectksi plugin')
            intr['name'] = plugin_name
            intr['description'] = plugin.description()
            intr['dependent on plugins'] = plugin.depending()
            intr['dependent on services'] = plugin.services_depending()

            introspectables.append(intr)

            plugin.service_locator = self.service_locator
            plugin.includeme(config, self.service_locator)

        config.action('apply_plugins', self._apply_plugins, args=(config, plugins),
                      introspectables=introspectables)

    def _apply_plugins(self, config, plugins):
        self.plugins = plugins