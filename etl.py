from typing import Literal
import polars as pl
from bridge import Connections
import datetime

class KS_Records():
    """Class to perform ETL process on Kickstarter archive files."""

    # Columns to drop
    cols_to_drop = ['location','photo','category','profile',
                    'urls','creator','video','table_id',
                    'robot_id','country_displayable_name',"currency_trailing_code",
                    "currency_symbol","source_url"
                    ]
    # Date cols to reformat
    date_changes = ["created_at","state_changed_at","deadline","launched_at"]

    # Schema changes to perform before loading data
    schema_changes = {'usd_pledged': pl.Float32,                  
                    'goal': pl.Int32,
                    "pledged": pl.Float32,
                    "static_usd_rate": pl.Float32,
                    "usd_exchange_rate": pl.Float32,
                    "fx_rate": pl.Float32,
                    "percent_funded": pl.Float32,
                    "backers_count": pl.Int32,
                    "converted_pledged_amount": pl.Int32,                
                    }
    
    def __init__(self,file: str, batch_size: int=10_000,output_db_table: str=None):
        """Initializes class to perform ETL process on a Kickstarter archive file.

        Args:
            file (str): Link to archive file.
            batch_size (int, optional): Batch size to use when processing JSON file. Defaults to 10_000.
            output_db_table (str, optional): Name of table in database to load data into. Defaults to None.
            If no table name is entered, the data will be available inside of a LazyFrame in this instance.
        """
        self.file = file
        self.batch_size = batch_size
        self.output_db_table = output_db_table

    def scan_file(self):
        """Scans the Kickstarter archive JSON file.
        """
        self.lf = pl.scan_ndjson(self.file,batch_size=self.batch_size,low_memory=True,include_file_paths='file')
    
    def transform_file(self):
        """Performs the necessary transformations and cleaning to the JSON file.
        """
        self.lf = self.lf.with_columns(pl.col("data").struct.unnest()).drop('data').cast(self.schema_changes)
        self.lf = self.lf.with_columns(
            pl.col("location").struct.field("id").alias("location_id"),
            pl.col("location").struct.field("localized_name"),
            pl.col("location").struct.field("country").alias("location_country"),
            pl.col("location").struct.field("state").alias("location_state"),
            pl.col("category").struct.field('id').alias("category_id"),
            pl.col("category").struct.field("name").alias("category_name"),
            pl.col("category").struct.field("parent_name").alias("category_parent_name"),
            pl.col("category").struct.field("parent_id").alias("category_parent_id"),
            pl.col("profile").struct.field("id").alias("profile_id"),
            pl.col("profile").struct.field("name").alias("profile_name"),
            pl.col("profile").struct.field("state").alias("profile_state"),
            pl.col("urls").struct.field('web').struct.field('rewards').alias("url_rewards"),
            pl.col("urls").struct.field('web').struct.field('project').alias("url_project"),
            pl.col("creator").struct.field("id").alias("creator_id"),
            pl.col("creator").struct.field("name").alias('creator_name'),
            pl.col("creator").struct.field("is_registered").alias("creator_is_registered"),
            pl.col("creator").struct.field("is_email_verified").alias("creator_is_email_verified"),
            pl.col("creator").struct.field("has_admin_message_badge").alias("creator_has_admin_message_badge"),
            pl.col("creator").struct.field("backing_action_count").alias("creator_backing_action_count").cast(pl.Int32),
            pl.col("video").struct.field("status").alias("video_status"),
            *self.date_change_expressions
            ).drop(self.cols_to_drop).sort('percent_funded').unique(subset=['id'],keep='last')


    def create_date_changes(self)-> list:
        """Generates a list of expressions to convert epoch dates to datetime columns. Used in transform step.

        Returns:
            list: List of expressions to be passed to with_columns method.
        """
        self.date_change_expressions = [pl.from_epoch(col) for col in self.date_changes]
    
    def load(self,db_table:str):
        """Loads data into a designated database table.

        Args:
            db_table (str): Name of database table to be updated.
        """

        cnx = Connections()
        print(f"Starting load step at {datetime.datetime.now()}")
        self.lf.collect(engine='streaming')\
            .write_database(db_table,
                            cnx.uri,
                            if_table_exists='append')
        print(f"Data successfully uploaded to database at {datetime.datetime.now()}")
        cnx.db_connection.close()


    def etl(self):
        """Runs the ETL process.
        """
        self.scan_file()
        self.create_date_changes()
        self.transform_file()
        if self.output_db_table:
            self.load(self.output_db_table)
        