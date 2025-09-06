import argparse
import json
import sys
import polars as pl

class JSONQueryEngine:
    def __init__(self):
        self.ctx = pl.SQLContext()
        
    def read_json_file(self, path: str) -> pl.DataFrame:
        """Read JSON file into a Polars DataFrame"""
        try:
            if path.endswith('.ndjson'):
                df = pl.read_ndjson(path)
            else:
                df = pl.read_json(path)
            return df
        except Exception as e:
            print(f"Error reading JSON file: {str(e)}", file=sys.stderr)
            sys.exit(1)
    
    def read_csv_file(self, path: str, separator: str) -> pl.DataFrame:
        """Read JSON file into a Polars DataFrame"""
        try:
            df = pl.read_csv(path,separator=separator)
            return df
        except Exception as e:
            print(f"Error reading CSV file: {str(e)}", file=sys.stderr)
            sys.exit(1)
    
            
    def execute_query(self, query: str, df: pl.DataFrame) -> pl.DataFrame:
        """Execute SQL query on DataFrame"""
        try:
            self.ctx.register('df',df)
            result = self.ctx.execute(query)
            return result.collect()
        except Exception as e:
            print(f"Error executing query: {str(e)}", file=sys.stderr)
            sys.exit(1)
            
    def format_output(self, df: pl.DataFrame, format: str = 'table') -> str:
        """Format output according to specified format"""
        if format == 'json':
            return df.write_json('./queryResults.json')
        elif format == 'csv':
            return df.write_csv('./queryResults.csv')
        else:  # default to table
            return df

def main():
    parser = argparse.ArgumentParser(description="JSON Query Engine using Polars")
    parser.add_argument('file', type=str, help="Path to JSON/CSV file")
    parser.add_argument('query', type=str, help="SQL query to execute. REMEBER: refer to the datframe as 'df'")
    parser.add_argument('--format', choices=['table', 'json', 'csv'], 
                       default='table', help="Output format. Default: stdout. Other supported format: csv, json.")
    parser.add_argument('--separator', 
                       default=',', help="Optional separator for CSV. Default: comma.\nMUST BE A SINGLE BYTE CHARACTER")
    
    args = parser.parse_args()
    
    engine = JSONQueryEngine()
    
    # Read JSON file
    print(args.file)
    if args.file.endswith(('.json','.ndjson')):
    	df = engine.read_json_file(args.file)
    elif args.file.endswith(('.csv','.txt')): #sometimes txt files are used to store csv
    	df = engine.read_csv_file(args.file, args.separator)
    else:
    	print("File format not supported!(SUPPORTED: JSON/CSV)")
    
    # Execute query
    result = engine.execute_query(args.query, df)
    
    # Output result
    print(engine.format_output(result, args.format))

if __name__ == "__main__":
    main()
