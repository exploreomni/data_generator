# Subset Demo Generator

This package is to facilitate high quality synthetic data ETLs. 
It works by declaratively structuring dataclasses, which then can be serialized to a csv, pushed to GCS and pushed into multiple databases.
It offers methods to generate unique values, run over run, as well as generation based on poisson and other methods. 

### To create a new table:
```python

@dataclass
class Person(metaclass=Table):
    # will result in a file named person.csv and table named person
    # dataclass fields will become csv columns and table columns with the correct types
    # this column will increment smoothly run over run
    id:int = field(default_factory=itertools.count(1).__next__) 
    #if more logic is needed than a simple default factory func, handle it in the __post_init__ function
    gender: str = field(init=False)
    # if you have a parent object, you can pass it in, for conditionality
    parent_object: InitVar[type] = None

    def __post_init__(self, parent_object:type):
        self.gender = random.choice(['M','F'])
        if self.gender == 'M':
            ...
        else:
            ...
        
        if parent_object.foo > 10:
            #conditional logic based off parent
            self.gender == 'N/A'
        
    
```


#smooth incrementing ids even for adding
```python
    id:int = field(default_factory=itertools.count(1).__next__)
```

## Snowflake Staging Setup
First go into snowflake, in the correct destination schema and create the stage from GCS
```sql
create stage my_gcs_stage
  url = 'gcs://name_of_gcs_bucket'
  storage_integration = gcp_int;
```
Snowflake generates a GCP service account which will need read privledges on the bucket. You can see the service
account by running the following command:
```sql
DESC STORAGE INTEGRATION GCP_INT;
```
the service account to enable with GCP storage reader privledges will be in the STORAGE_GCP_SERVICE_ACCOUNT property.

The name of this stage will need to be placed in your environment variables  .env file too
```
SF_STAGE_NAME=my_gcs_stage
```





### Licensing Considerations
considered the licensable data from here:
https://www.themoviedb.org/

am using rapid api instead, gives clips from imdb videos

Also use only the population column from https://simplemaps.com/data/us-zips
to accurately generate us adresses based on population