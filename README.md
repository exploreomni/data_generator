# subset_demo_data

This package is to facilitate high quality synthetic data ETLs. 


To create a new table:

#smooth incrementing ids even for adding
id:int = field(default_factory=itertools.count().__next__)