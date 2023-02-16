from dataclass_csv import DataclassReader, DataclassWriter
from typing import Dict
import itertools
from operator import attrgetter
from dataclasses import dataclass, field
from pydash import set_, get
import random

class Table(type):
    __class_registry__:set = set()
    __loaded__:Dict[type,bool] = dict()
    def __init__(cls, name, bases, attrs, **kw):
        super().__init__(name, bases, attrs, **kw)
        cls.__class_registry__.add(cls)
        cls.instances = list()
        cls.__seed_defaults__ = dict()
        cls.__seen__ = dict()

    def __call__(cls, *args, **kw):
        if 'load_existing' in kw and kw['load_existing'] and cls not in cls.__loaded__:
            try:
                with open(f'output/{cls.__name__.lower()}.csv', 'r') as f:
                    existing_instances = DataclassReader(f, cls)
                    cls.instances = list(existing_instances)
                    cls.__loaded__[cls] = True
                    #For fields using itertools.count, set the default_factory to the next value
                    for k,v in cls.__dataclass_fields__.items():
                        if hasattr(v, 'default_factory'):
                            if hasattr(v.default_factory, '__qualname__'):
                                if v.default_factory.__qualname__ == 'count.__next__':
                                    new_seed = max(cls.instances, key=attrgetter(k)).__getattribute__(k) + 1
                                    set_(cls.__seed_defaults__,[cls, k], itertools.count(new_seed).__next__)
                    #run after_first_run hook (extends existing data)
                    for instance in cls.instances:
                        if hasattr(instance, 'after_first_run'):
                            instance.after_first_run()
                    
            except FileNotFoundError:
                pass
 
        #remove the load_existing kwarg / should not be passed into an instance
        kw.pop('load_existing', None)
        #overriding natural sequences, with one having the correct value
        seed_defaults = get(cls.__seed_defaults__,[cls])
        if seed_defaults:
            for k,v in seed_defaults.items():
                if k not in kw:
                    kw[k] = v()
        instance = super(Table, cls).__call__(*args, **kw)
        cls.instances.append(instance)
        return instance
    
    def unique(cls, field_name, func, *args, **kwargs):
        hash_key = kwargs.pop('hash_key', None)
        if field_name not in cls.__seen__:
            cls.__seen__[field_name] = set()
            for instance in cls.instances:
                cls.__seen__[field_name].add(instance.__getattribute__(field_name))
            if hash_key:
                retval = func(*args, **kwargs) 
                checkval = retval[hash_key]
            else:
                retval = func(*args, **kwargs)
                checkval = retval
            if checkval in cls.__seen__[field_name]:
                return cls.unique(field_name, func, *args, **kwargs)
            else:
                cls.__seen__[field_name].add(checkval)
                return retval 
        else:
            if hash_key:
                retval = func(*args, **kwargs) 
                checkval = retval[hash_key]
            else:
                retval = func(*args, **kwargs)
                checkval = retval
            if checkval in cls.__seen__[field_name]:
                return cls.unique(field_name, func, *args, **kwargs)
            else:
                cls.__seen__[field_name].add(checkval)
                return retval

    def pick_existing(cls, field_name):
        index = random.randint(0,len(cls.instances)-1)
        return cls.instances[index].__getattribute__(field_name)

    @classmethod
    def writeall(cls):
        for sub in cls.__class_registry__:
            sub.write()
    
    def write(cls):
        with open(f'output/{cls.__name__.lower()}.csv', 'w') as f:
            x = DataclassWriter(f, cls.instances, cls, dialect='unix')
            x.write()