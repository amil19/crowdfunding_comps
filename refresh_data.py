import os
from dotenv import load_dotenv
import etl as ETL
import app_reference as ref
from ks_datasets import KS_Datasets
from embeddings import Embeddings
from rich.console import Console
import polars as pl

class Refresh():

    def __init__(self,n: int=10):
        """Initializes the refresh class and establishes DB connection.

        Args:
            n (int): Number of scrapes to iterate through for refreshing. Defaults to 10.
        """
        load_dotenv()
        self.db_conn = ETL.KS_Records.initialize_connection('md')
        self.console = Console(record=True) 
        self.n = n
        if self.n:
            self.limit_qualifier = f"limit {self.n}"
        else:
            self.limit_qualifier = None

    def _pull_existing_ks_ids(self):
        """Loads existing camapign IDs from database.
        """
        existing_ids = self.db_conn.execute(f"Select distinct id from {ref.ks_table} order by id").fetchall()
        self.existing_ids = set([id[0] for id in existing_ids])
        self.console.log("Retrieved existing campaign IDs from database")

    def _pull_existing_run_ids(self):
        """Loads existing run_ids from database.
        """
        query = f"""select distinct(run_id) from {ref.ks_table} order by run_id desc {self.limit_qualifier};"""
        existing_run_ids = self.db_conn.execute(query).fetchall()
        self.existing_run_ids = [id[0] for id in existing_run_ids]
        self.console.log("Retrieved existing run IDs from database")

    def _check_scrapes(self):
        """Retrieves links for web scrapes.
        """
        datasets = KS_Datasets()
        self.scrape_links = datasets.archive_links
        if self.n:
            self.scrape_links=self.scrape_links[0:self.n]

    def _define_new_scrapes(self):
        """Defines new scrapes based on run_id.
        """
        self.new_scrapes = []
        for link in self.scrape_links:
            start_idx = link.find("Kickstarter_")
            end_idx = link.find(".",start_idx)
            run_id = link[start_idx:end_idx]
            if run_id not in self.existing_run_ids:
                self.new_scrapes.append(link)
        self.console.log(f"Found {len(self.new_scrapes)} new scrapes to process")
        self.new_scrapes.reverse()

    def _process_scrape(self,link: str):
        """Processes a web scrape file.

        Args:
            link (str): Link to web scape.
        """
        data = ETL.KS_Records(link)
        data.scan_file()
        data.create_date_changes()
        data.transform_file()
        self.lf = data.lf.collect(engine='streaming').lazy()
        self.console.log("Processed file")
    
    def _define_new_ids(self):
        """Determines the IDs of new campaigns.
        """
        ids_in_scrape = set(self.lf.select("id").unique().collect().to_series().to_list())
        self.ids_to_add = ids_in_scrape.difference(self.existing_ids)
        self.console.log(f"Found {len(self.ids_to_add)} new campaign IDs to add")

    def _create_new_data(self):
        """Subsets the new record data.
        """
        self.new_data = self.lf.filter(pl.col("id").is_in(self.ids_to_add))
        self.console.log("Subset new data")
    
    def _create_embeddings(self):
        """Creates embeddings for new records.
        """
        embeddings = Embeddings(self.new_data,'id',['name','blurb'])
        embeddings.create_documents()
        embeddings.transform()
        self.embeddings_df = embeddings.df.drop(['cols_to_embed', 'is_in_post_campaign_pledging_phase'])
        self.console.log("Created embeddings for new data")
    
    def _update_exiting_records(self):
        """Updates existing records whose info has changed.
        """
        existing_records = self._load_existing_records()
        df1 = self._subset_existing_data(existing_records)
        df2 = self._subset_existing_data(self.lf)
        mismached_records = self._find_mismatches(df1,df2)
        ids_to_update = mismached_records.select(pl.col("id").cast(str)).collect().to_series().to_list()
        updated_records = self.lf.join(mismached_records.select("id","embeddings"),
                                       on='id',how='inner')\
                                        .drop('is_in_post_campaign_pledging_phase')
        self._delete_outdated_records(ids_to_update)
        ETL.KS_Records.insert_into_duckdb(
            base_df=updated_records,
            table_name=ref.ks_table,
            db=os.environ.get('DUCKDB')
            )

    def _load_existing_records(self) -> pl.LazyFrame:
        """Loads existing database records. Used to check for changes.

        Returns:
            pl.LazyFrame: LazyFrame containing the columns to check for changes within.
        """
        query = f"Select id,goal,percent_funded,usd_pledged,embeddings from {ref.ks_table}"
        return self.db_conn.execute(query).pl().lazy()

    def _subset_existing_data(self, df:pl.LazyFrame) -> pl.LazyFrame:
        """Filters out new campaign ids from the data.

        Args:
            df (pl.LazyFrame): Either old or new scrape records.

        Returns:
            pl.LazyFrame: Scrape records without new campaign IDs.
        """
        new_records = pl.col("id").is_in(self.ids_to_add)
        df = df.filter(~new_records).sort('id').fill_null(0)
        return df
    
    def _find_mismatches(self,old_data: pl.LazyFrame,new_data: pl.LazyFrame) -> pl.LazyFrame:
        """Finds the records whose information has changed in current scrape
        compared to existing data.

        Args:
            old_data (pl.LazyFrame): Existing campaign records
            new_data (pl.LazyFrame): New campaign records from current scrape

        Returns:
            pl.LazyFrame: Records in new data that don't match old data
        """
        old_data = old_data.select(['id','goal','percent_funded','usd_pledged','embeddings'])
        new_data = new_data.select(['id','goal','percent_funded','usd_pledged'])

        return new_data.join(old_data, on=['id','goal','percent_funded','usd_pledged'],
                                     how='anti')

    def _delete_outdated_records(self,ids: list[int]):
        """Purges outdated records from database.

        Args:
            ids (list[int]): Campaign IDs to delete
        """
        self.db_conn.execute(f"delete from {ref.ks_table} where id in ({','.join(ids)})")
        self.console.log("Purged outdated records from database.")

    def run(self):
        self._pull_existing_ks_ids()
        self._pull_existing_run_ids()
        self._check_scrapes()
        self._define_new_scrapes()
        for idx,link in enumerate(self.new_scrapes,1):
            self.console.log(f"Processing link {idx} of {len(self.new_scrapes)}")
            self._process_scrape(link)
            self._define_new_ids()
            self._create_new_data()
            self._create_embeddings()
            ETL.KS_Records.insert_into_duckdb(
                base_df=self.embeddings_df,
                table_name=ref.ks_table,
                db=os.environ.get('DUCKDB')
                )
            del self.embeddings_df, self.new_data
            self._update_exiting_records()
            del self.lf
            self.console.log("[green] Succesfully processed new scrape")
        self.console.log("[green] Full Refresh completed")