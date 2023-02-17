from dataclass_csv import DataclassReader, DataclassWriter
from typing import Dict, List, Any
import itertools
from operator import attrgetter
from dataclasses import dataclass, field
from pydash import set_, get
import random

MAX_UNIQUE_ATTEMPTS = 500

class Table(type):
    __class_registry__:set = set()
    __loaded__:Dict[type,bool] = dict()
    def __init__(cls, name, bases, attrs, **kw):
        super().__init__(name, bases, attrs, **kw)
        cls.__class_registry__.add(cls)
        cls.instances = list()
        cls.__seed_defaults__ = dict()
        cls.__seen__ = dict()

    def __call__(cls, *args, **kw) -> Any:
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
        if 'generate_new' in kw and not kw['generate_new']:
            return None
 
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
    
    def unique(cls, field_name, func, *args, **kwargs) -> Any:
        ## raise exception if recursion depth exceeds a configurable amount
        attempt_count = kwargs.pop('attempt_count', None)
        if attempt_count is None:
            attempt_count = 0
        attempt_count += 1
        if attempt_count > MAX_UNIQUE_ATTEMPTS:
            raise Exception('''Difficult to generate unique value... '''
                            '''ensure your script is not '''
                            f'''guaranteeing uniqueness on {field_name} with a finite generator {func.__name__}''')
        
        #if we haven't seen this field before, create a set to track it
        if field_name not in cls.__seen__:
            cls.__seen__[field_name] = set()
            for instance in cls.instances:
                cls.__seen__[field_name].add(instance.__getattribute__(field_name))

        #hash_key is a key to use to check uniqueness of a dict (since the whole type itself is not hashable)
        hash_key = kwargs.pop('hash_key', None)
        if hash_key:
            retval = func(*args, **kwargs) 
            checkval = retval[hash_key]
        else:
            retval = func(*args, **kwargs)
            checkval = retval
            # if hash_key is not specified, and the return value is a dict, raise an exception
            if type(retval) == dict:
                raise Exception(f'for dictionary based generators such as {func.__name__} '
                                'you must specify a hash_key (key within the dict pointing to value to perform the uniqueness check upon) '
                                'e.g. unique("company_name", fake.company, hash_key="name") '
                                "for fake.company which returns {'name': 'Acme', 'suffix': 'LLC'}'}"
                                )
        #if the value is already in the set, recurse (while keeping track of attempts)
        if checkval in cls.__seen__[field_name]:
            return cls.unique(field_name, func, *args, hash_key=hash_key, attempt_count=attempt_count, **kwargs)
        else:
            #happy path, add the new value to the set and return it
            cls.__seen__[field_name].add(checkval)
            return retval 


    def pick_existing(cls, field_name, filter_func=None) -> Any:
        #pick at random from the subset that match the filter_func
        if filter_func:
            filtered_instances = list(filter(filter_func, cls.instances))
            index = random.randint(0,len(filtered_instances)-1)
            return filtered_instances[index].__getattribute__(field_name)
        
        #picked at random from existing instances
        else:
            index = random.randint(0,len(cls.instances)-1)
            return cls.instances[index].__getattribute__(field_name)

    @classmethod
    def writeall(cls) -> None:
        for sub in cls.__class_registry__:
            sub.write()
    
    def write(cls) -> None:
        with open(f'output/{cls.__name__.lower()}.csv', 'w') as f:
            x = DataclassWriter(f, cls.instances, cls, dialect='unix')
            x.write()