from dataclass_csv import DataclassReader, DataclassWriter, dateformat
from typing import Dict, List, Any
import itertools
from operator import attrgetter
from dataclasses import dataclass, field
from pydash import set_, get
import random
import sqlalchemy as SA
from dotenv import load_dotenv
load_dotenv()
from dataclasses import dataclass, field, fields
from datetime import datetime, date
from google.cloud import storage
from google.cloud import bigquery
import os

MAX_UNIQUE_ATTEMPTS = 500

#TODO: currently the user must call the generation in the 
# correct DAG order, if the post_init uses a field from another table (pick_existing, etc)
# perhaps we can use the __loaded__ variable of len(cls.instances) > 0 to determine if we should
# throw an exception inidicating they should be called in a different order

class Table(type):
    __class_registry__:set = set()
    __loaded__:Dict[type,bool] = dict()
    __snowflake__ = None #slot to store the snowflake connection
    __bigquery__ = None #slot to store the bigquery connection
    
    def __init__(cls, name, bases, attrs, **kw):
        super().__init__(name, bases, attrs, **kw)
        cls.__class_registry__.add(cls)
        cls.instances = list() #stores the instances of this class which have been generated
        cls.__seed_defaults__ = dict() #stores the default_factory for fields using itertools.count (smoth sequences)
        cls.__seen__ = dict() #slot to store the seen values for unique fields

    def __call__(cls, *args, **kw) -> Any:
        if 'load_existing' in kw and kw['load_existing'] and cls not in cls.__loaded__:
            try:
                with open(cls.__file_path__, 'r') as f:
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
                        if 'generate_new' in kw and not kw['generate_new']:
                            return None
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
            #only write if the class has been loaded, which avoids 
            # an annoying overwrite with blank issue
            # if sub in cls.__loaded__ and cls.__loaded__[sub]: 
            sub.write()
    
    def write(cls) -> None:
        with open(cls.__file_path__, 'w') as f:
            writerInstance = DataclassWriter(f, cls.instances, cls, dialect='unix')
            writerInstance.write()

    def generate(cls, count:int = 1, **kwargs) -> None:
        '''
        Generate a number of instances of a class
        Args:
            count: number of instances to generate
            kwargs: keyword arguments to pass to the constructor
                load_existing: if True, will load existing data from the csv file
                generate_new: if False, will not generate new data
        '''
        for _ in range(count):
            cls(**kwargs)

    @property
    def sqlalchemy_fields(cls) -> List[SA.Column]:
        cols = list()
        for f in fields(cls):
            # print(f.name, f.type)
            if f.type == str:
                cols.append(SA.Column(f.name, SA.String))
            elif f.type == int:
                cols.append(SA.Column(f.name, SA.Integer))
            elif f.type == float:
                cols.append(SA.Column(f.name, SA.Float))
            elif f.type == bool:
                cols.append(SA.Column(f.name, SA.Boolean))
            elif f.type == list:
                cols.append(SA.Column(f.name, SA.ARRAY(SA.String)))
            elif f.type == dict:
                cols.append(SA.Column(f.name, SA.JSON))
            elif f.type == date:
                cols.append(SA.Column(f.name, SA.Date))                
            elif f.type == datetime:
                cols.append(SA.Column(f.name, SA.DateTime))
            else:
                raise Exception(f'Unknown type {f.type}')
        return cols
    
    @property
    def bq_fields(cls):
        cols = list()
        for f in fields(cls):
            if f.type == str:
                cols.append(bigquery.SchemaField(f.name, "STRING"))
            elif f.type == int:
                cols.append(bigquery.SchemaField(f.name, "INT64"))
            elif f.type == float:
                cols.append(bigquery.SchemaField(f.name, "FLOAT64"))
            elif f.type == bool:
                cols.append(bigquery.SchemaField(f.name, "BOOL"))
            elif f.type == list:
                cols.append(bigquery.SchemaField(f.name, "ARRAY"))
            elif f.type == dict:
                #TODO: no idea how to handle this
                # cols.append(bigquery.SchemaField(f.name, "STRUCT"))
                cols.append(bigquery.SchemaField(f.name, "STRING"))
            elif f.type == date:
                cols.append(bigquery.SchemaField(f.name, "DATETIME"))
            elif f.type == datetime:
                cols.append(bigquery.SchemaField(f.name, "DATETIME"))
            else:
                raise Exception(f'Unknown type {f.type}')
        return cols

    @property
    def __table_name__(cls):
        return cls.__name__.lower()
    
    @property
    def __file_name__(cls):
        return f'{cls.__table_name__}.csv'
    
    @property
    def __file_path__(cls):
        return f"{os.environ['OUTPUT_FOLDER']}/{cls.__file_name__}"

    def upload(cls):
        """
        Uploads a file to the bucket.
        # bucket_name = "your-bucket-name"
        # source_file_name = "local/path/to/file"
        # destination_blob_name = "storage-object-name"
        :return:
        """
        gcp_client = storage.Client()
        bucket = gcp_client.bucket(os.environ['GCS_BUCKET'])
        blob = bucket.blob(cls.__file_name__)
        blob.upload_from_filename(cls.__file_path__)
        print("File {} uploaded to {}.".format(cls.__file_path__, cls.__file_name__))

    @classmethod
    def __init__bq(cls):
        if not cls.__bigquery__:
            cls.__bigquery__ = bigquery.Client()

    def push_to_bq(cls) -> None:
        # client = bigquery.Client()
        cls.__init__bq()
        client = cls.__bigquery__
        job_config = bigquery.LoadJobConfig(
            # autodetect=True, 
            schema=cls.bq_fields,
            source_format=bigquery.SourceFormat.CSV,
            skip_leading_rows=1,
        )
        BQ_PROJECT = os.environ['BQ_PROJECT']
        BQ_DATASET = os.environ['BQ_DATASET']
        uri = f"gs://{os.environ['GCS_BUCKET']}/{cls.__file_name__}"
        table_id = f"{BQ_PROJECT}.{BQ_DATASET}.{cls.__table_name__}"
        #drop table if exists
        client.delete_table(table_id, not_found_ok=True)
        #create table
        load_job = client.load_table_from_uri(
            uri, table_id, job_config=job_config
        )  # Make an API request.
        load_job.result()  # Waits for the job to complete.
        destination_table = client.get_table(table_id)
        print(f"Loaded {destination_table.num_rows} rows to BigQuery {table_id}")

    @classmethod
    def __init__snowflake(cls):
        if not cls.__snowflake__:
            from snowflake.sqlalchemy import URL
            from sqlalchemy.engine import create_engine
            cls.__snowflake_engine__ = create_engine(URL(
                user=os.environ['SF_USER'],
                password=os.environ['SF_PASSWORD'],
                account=os.environ['SF_ACCOUNT'],
                warehouse=os.environ['SF_WAREHOUSE'],
                database=os.environ['SF_DATABASE'],
                schema=os.environ['SF_SCHEMA'],
                role=os.environ['SF_ROLE']
            ), 
            pool_reset_on_return=None
            )

    def push_to_sf(cls) -> None:
        cls.__init__snowflake()
        engine = cls.__snowflake_engine__
        the_table = SA.Table(cls.__table_name__, SA.MetaData(
            schema=os.environ['SF_SCHEMA']
        ), *cls.sqlalchemy_fields)
        the_table.drop(engine, checkfirst=True)
        the_table.create(engine, checkfirst=True)
        result = engine.execute(
            f'''
            /* Standard data load */
            COPY INTO {cls.__table_name__}
                FROM @{ os.environ['SF_STAGE_NAME'] }
              FILES = ( '{cls.__file_name__}' ) 
              FILE_FORMAT = ( 
                                TYPE = CSV 
                                SKIP_HEADER = 1 
                                FIELD_DELIMITER = ','
                                FIELD_OPTIONALLY_ENCLOSED_BY = '"'
                                EMPTY_FIELD_AS_NULL = TRUE
                                NULL_IF = ""
                                )
              FORCE = TRUE
            '''
        ).fetchall()
        engine.execute('COMMIT').fetchall()

        
        print(f"Loaded {result[0][3]} rows to Snowflake {os.environ['SF_DATABASE']}"
              f".{os.environ['SF_SCHEMA']}.{cls.__table_name__}")

    def push_to_dbs(cls) -> None:
        ''' Performs upload to GCS, push to BQ and push to Snowflake '''
        cls.upload()
        cls.push_to_bq()
        cls.push_to_sf()

    @classmethod
    def pushall(cls) -> None:
        ''' Pushes all registered classes to GCS, BQ and Snowflake'''
        for sub in cls.__class_registry__:
            sub.push_to_dbs()
