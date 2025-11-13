import duckdb
from typing import Optional, List, Dict, Any
from pathlib import Path

class DuckDBManager:
    """manages duckdb connection and query execution"""
    def __init__(self, db_path: Optional[str] = None):
        """
        init duckdb manager
        args:
            db_path: path to persist db file or use in-memory db
        """
        self.db_path = db_path
        self.conn = duckdb.connect(db_path or ":memory")
        self.loaded_tables: Dict[str, str] = {} # table_name -> file_path

    def load_file(self, file_path: str, table_name: Optional[str] = None) -> str:
        """
        load a data file (csv, parquet, arrow) into duckdb
        args:
            file_path: path to file
            table_name: optional table name, use filename without extension if none
        returns:
            the table name useduv
        """
        path = Path(file_path)
        if not table_name:
            table_name = path.stem.replace(" ", "_").replace("-","_")

        # create a view for easier naming and schema
        suffix = path.suffix.lower()

        if suffix == ".csv" or suffix == ".gz":
            query = f"CREATE OR REPLACE VIEW {table_name} AS SELECT * FROM read_csv_auto('{file_path}')"
        elif suffix == ".parquet":
            query = f"CREATE OR REPLACE VIEW {table_name} AS SELECT * FROM read_parquet('{file_path}')"
        elif suffix == ".arrow":
            query = f"CREATE OR REPLACE VIEW {table_name} AS SELECT * FROM read_arrow('{file_path}')"
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

        self.conn.execute(query)
        self.loaded_tables[table_name] = file_path
        return table_name
        
    def execute_query(self, query: str) -> duckdb.DuckDBPyConnection:
        """
        execute sql query

        args:
            query: sql query string
        returns:
            query result object
        """
        return self.conn.execute(query)
    
    def get_table_schema(self, table_name: str) -> List[tuple]:
        """
        get schema information for a table

        args:
            table_name: name of the table
        returns:
            list of (column_name, column_type) tuples
        """
        result = self.conn.execute(f"DESCRIBE {table_name}").fetchall()
        return [(row[0], row[1]) for row in result]
    
    def get_table_stats(self, table_name: str) -> Dict[str, Any]:
        """
        get basic stats for a table

        args:
            table_name: name of the table
        returns:
            dictionary with row count and column count
        """
        row_count = self.conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        schema = self.get_table_schema(table_name)

        return {
            "row_count": row_count,
            "column_count": len(schema),
            "columns": schema
        }

    def list_tables(self) -> List[str]:
        """
        list all available tables/views
        returns:
            list of table names
        """
        return list(self.loaded_tables.keys())
    
    def export_result(self, query:str, output_path: str, format: str = "csv"):
        """
        execute query and export results to a file

        args:
            query: sql query to execute
            output_path: path to output file
            format: output format('csv', 'parquet', 'arrow')
        """
        if format == "csv":
            self.conn.execute(f"COPY ({query}) TO '{output_path}' (HEADER, DELIMITER ',')")
        elif format == "parquet":
            self.conn.execute(f"COPY ({query}) TO '{output_path}' (FORMAT PARQUET)")
        elif format == "arrow":
            self.conn.execute(f"COPY ({query}) TO '{output_path}' (FORMAT ARROW)")
        else:
            raise ValueError(f"Unsupported export format: {format}")
        
    def close(self):
        """close the database connection"""
        self.conn.close()