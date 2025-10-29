from typing import Literal
import polars as pl
from bridge import Connections
from embeddings import Embeddings
from config import Configs
import datetime
import os
import duckdb

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
                    'goal': pl.Float32,
                    "pledged": pl.Float32,
                    "static_usd_rate": pl.Float32,
                    "usd_exchange_rate": pl.Float32,
                    "fx_rate": pl.Float32,
                    "percent_funded": pl.Float32,
                    "backers_count": pl.Int32,
                    "converted_pledged_amount": pl.Float32,                
                    }
    
    column_order = ['run_id',
                    'file',
                    'goal',
                    'is_liked',
                    'usd_exchange_rate',
                    'is_launched',
                    'id',
                    'is_in_post_campaign_pledging_phase',
                    'deadline',
                    'country',
                    'disable_communication',
                    'staff_pick',
                    'blurb',
                    'fx_rate',
                    'slug',
                    'spotlight',
                    'percent_funded',
                    'created_at',
                    'state_changed_at',
                    'current_currency',
                    'prelaunch_activated',
                    'static_usd_rate',
                    'usd_pledged',
                    'launched_at',
                    'name',
                    'state',
                    'is_starrable',
                    'backers_count',
                    'usd_type',
                    'is_disliked',
                    'currency',
                    'converted_pledged_amount',
                    'pledged',
                    'location_id',
                    'localized_name',
                    'location_country',
                    'location_state',
                    'category_id',
                    'category_name',
                    'category_parent_name',
                    'category_parent_id',
                    'profile_id',
                    'profile_name',
                    'profile_state',
                    'url_rewards',
                    'url_project',
                    'creator_id',
                    'creator_name',
                    'creator_is_registered',
                    'creator_is_email_verified',
                    'creator_has_admin_message_badge',
                    'creator_backing_action_count',
                    'video_status']
    
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
        self.lf = pl.scan_ndjson(self.file,batch_size=self.batch_size,low_memory=True,include_file_paths='file',schema=Configs.json_schema)
    
    def transform_file(self):
        """Performs the necessary transformations and cleaning to the JSON file.
        """
        self.lf = self.lf.with_columns(pl.col("data").struct.unnest()).drop('data').cast(self.schema_changes)

        if self.check_struct(self.lf,'creator','backing_action_count') is False:
            self.lf = self.lf.with_columns(pl.col("creator").struct.with_fields(backing_action_count=pl.lit(None)).alias("creator"))

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
            ).drop(self.cols_to_drop).sort('percent_funded').unique(subset=['id'],keep='last').select(self.column_order)
        print("File transformations entered.")


    def create_date_changes(self)-> list:
        """Generates a list of expressions to convert epoch dates to datetime columns. Used in transform step.

        Returns:
            list: List of expressions to be passed to with_columns method.
        """
        self.date_change_expressions = [pl.from_epoch(col) for col in self.date_changes]

    @staticmethod
    def check_struct(lf: pl.LazyFrame,struct_col: str,struct_field: str) -> bool:
        """Checks if a field exists in a struct.

        Args:
            lf (pl.LazyFrame): LazyFrame containing struct to evaluate.
            struct_col (str): Name of struct column to evaluate.
            struct_field (str): Name of field to validate is in struct.

        Returns:
            bool
        """
        struct_schmea = lf.select(struct_col).collect_schema().values().mapping.get(struct_col).fields

        if len([True for field in struct_schmea if field.name == struct_field]) > 0:
            return True
        else:
            return False
    
    def load(self,db_table:str,db_source: Literal['supabase','duckdb']):
        """Loads data into a designated database table.

        Args:
            db_table (str): Name of database table to be updated.
        """
        if db_source == 'supabase':
            cnx = Connections()
            print(f"Starting load step at {datetime.datetime.now()}")
            self.lf.collect(engine='streaming')\
                .write_database(db_table,
                                cnx.uri,
                                if_table_exists='append')
            print(f"Data successfully uploaded to database at {datetime.datetime.now()}")
            cnx.db_connection.close()

        else:
            db_file = 'crowdfunding_comps.db'
            if os.path.exists(db_file):
                print("Inserting rows into duckdb database.")
                self.insert_into_duckdb(self.lf,db_table,db_file)
                print("Insert complete.")
            else:
                print("Creating duckdb database.")
                self.create_duckdb_table(self.lf,db_table,db_file)
                print("Database created.")
                
    @staticmethod
    def insert_into_duckdb(base_df: pl.DataFrame | pl.LazyFrame, table_name: str, db: str):
        if isinstance(base_df,pl.LazyFrame):
            base_df = base_df.collect(engine='streaming')
            print("Successully collected LazyFrame")
        try:
            with duckdb.connect(db) as con:
                con.execute(f"INSERT INTO {table_name} SELECT * FROM base_df;")
        except Exception as e:
            print(e)
            
    @staticmethod
    def create_duckdb_table(base_df: pl.DataFrame | pl.LazyFrame, table_name: str, db: str):

        if isinstance(base_df,pl.LazyFrame):
            base_df = base_df.collect(engine='streaming')

        arrow_df = base_df.to_arrow()

        print("Created Arrow version of DF")

        with duckdb.connect(db) as con:

            con.sql(f"CREATE TABLE {table_name} AS SELECT * FROM arrow_df;")

    def create_embeddings(self):
        """Create an embedding of the combination of a embedding_columns.
        """
        print(f"Embedding columns: {Configs.embedding_columns}")
        embed = Embeddings(self.lf,Configs.embedding_columns)
        self.lf = embed.transform()

    def etl(self,output_db: Literal['supabase','duckdb']='duckdb'):
        """Runs the ETL process.

        Args:
            output_db (Literal['supabase','duckdb']): Output database to load data into. Defaults to DuckDB.
        """
        try:
            self.scan_file()
            self.create_date_changes()
            self.transform_file()
            self.create_embeddings()
            if self.output_db_table:
                self.load(self.output_db_table,output_db)
        except Exception as e:
            print(f'Unable to process file: {self.file}')
        