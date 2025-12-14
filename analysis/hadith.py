import pandas as pd
import re
from pathlib import Path

class HadithAnalyzer:
    def __init__(self, csv_path):
        """
        Initialize the HadithAnalyzer with a CSV file path.
        
        Args:
            csv_path (str): Path to the CSV file
        """
        self.csv_path = csv_path
        self.df = None
        self.load_data()
        
    def load_data(self):
        """Load and preprocess the CSV data."""
        try:
            # Read the CSV file
            self.df = pd.read_csv(self.csv_path, encoding='utf-8')
            
            # Display column names for debugging
            print("Available columns:", list(self.df.columns))
            print("\n" + "="*50 + "\n")
            
            # Clean column names (remove extra spaces and special characters)
            self.df.columns = [col.strip() for col in self.df.columns]
            
            # Find the correct column names (they might have different naming)
            column_mapping = {}
            
            # Look for columns containing these keywords
            for col in self.df.columns:
                col_lower = col.lower()
                if 'sn' in col_lower or 'serial' in col_lower:
                    column_mapping['SN'] = col
                elif 'hadith' in col_lower and 'book' in col_lower:
                    column_mapping['Hadith_Book_No'] = col
                elif 'arabic' in col_lower and 'without' in col_lower:
                    column_mapping['Arabic_without_TASHKEEL'] = col
                elif 'arabic' in col_lower and 'tashkeel' in col_lower:
                    column_mapping['Arabic_TASHKEEL'] = col
                elif 'arabic' in col_lower and 'with' in col_lower:
                    column_mapping['Arabic_TASHKEEL'] = col
            
            # If we couldn't find columns by name, try to infer from structure
            if not column_mapping:
                print("Could not find columns by name. Trying to infer from structure...")
                # You may need to adjust this based on your actual CSV structure
                if len(self.df.columns) >= 7:
                    column_mapping = {
                        'SN': self.df.columns[0],
                        'Hadith_Book_No': self.df.columns[2],
                        'Arabic_without_TASHKEEL': self.df.columns[4],
                        'Arabic_TASHKEEL': self.df.columns[6]
                    }
            
            # Rename columns to standard names
            if column_mapping:
                self.df = self.df.rename(columns={
                    column_mapping['SN']: 'SN',
                    column_mapping['Hadith_Book_No']: 'Hadith_Book_No',
                    column_mapping['Arabic_without_TASHKEEL']: 'Arabic_without_TASHKEEL',
                    column_mapping['Arabic_TASHKEEL']: 'Arabic_TASHKEEL'
                })
            
            # Keep only the columns we need
            required_columns = ['SN', 'Hadith_Book_No', 'Arabic_without_TASHKEEL', 'Arabic_TASHKEEL']
            self.df = self.df[required_columns]
            
            # Clean the data
            self.clean_data()
            
            print(f"Successfully loaded {len(self.df)} records")
            print("\nFirst few records:")
            print(self.df.head())
            
        except Exception as e:
            print(f"Error loading CSV file: {e}")
            print("\nPlease check the CSV structure. If the column names are different,")
            print("you may need to manually specify them in the load_data() method.")
    
    def clean_data(self):
        """Clean and preprocess the data."""
        # Convert SN to numeric if possible
        self.df['SN'] = pd.to_numeric(self.df['SN'], errors='coerce')
        
        # Fill NaN values with empty string for text columns
        text_columns = ['Arabic_without_TASHKEEL', 'Arabic_TASHKEEL']
        for col in text_columns:
            self.df[col] = self.df[col].fillna('')
        
        # Remove any duplicate rows
        self.df = self.df.drop_duplicates()
    
    def search_arabic_text(self, query, search_column='both', case_sensitive=False):
        """
        Search for text in Arabic columns.
        
        Args:
            query (str): Search term
            search_column (str): 'both', 'without_tashkeel', or 'with_tashkeel'
            case_sensitive (bool): Whether search should be case sensitive
        
        Returns:
            pandas.DataFrame: Filtered results
        """
        if search_column == 'both':
            mask = (self.df['Arabic_without_TASHKEEL'].str.contains(query, case=case_sensitive, na=False) |
                    self.df['Arabic_TASHKEEL'].str.contains(query, case=case_sensitive, na=False))
        elif search_column == 'without_tashkeel':
            mask = self.df['Arabic_without_TASHKEEL'].str.contains(query, case=case_sensitive, na=False)
        elif search_column == 'with_tashkeel':
            mask = self.df['Arabic_TASHKEEL'].str.contains(query, case=case_sensitive, na=False)
        else:
            raise ValueError("search_column must be 'both', 'without_tashkeel', or 'with_tashkeel'")
        
        results = self.df[mask]
        print(f"Found {len(results)} results for query: '{query}'")
        return results
    
    def search_by_book_no(self, book_no):
        """Search hadith by book number."""
        results = self.df[self.df['Hadith_Book_No'] == book_no]
        print(f"Found {len(results)} hadith in book {book_no}")
        return results
    
    def search_by_sn_range(self, start_sn, end_sn):
        """Search hadith by SN range."""
        results = self.df[(self.df['SN'] >= start_sn) & (self.df['SN'] <= end_sn)]
        print(f"Found {len(results)} hadith in SN range {start_sn}-{end_sn}")
        return results
    
    def get_statistics(self):
        """Get basic statistics about the data."""
        stats = {
            'total_hadith': len(self.df),
            'unique_books': self.df['Hadith_Book_No'].nunique(),
            'sn_range': f"{self.df['SN'].min()} - {self.df['SN'].max()}",
            'avg_text_length_without_tashkeel': self.df['Arabic_without_TASHKEEL'].str.len().mean(),
            'avg_text_length_with_tashkeel': self.df['Arabic_TASHKEEL'].str.len().mean()
        }
        
        print("\n" + "="*50)
        print("DATA STATISTICS")
        print("="*50)
        for key, value in stats.items():
            print(f"{key.replace('_', ' ').title()}: {value}")
        
        # Show book distribution
        print("\nBook Distribution (Top 10):")
        book_counts = self.df['Hadith_Book_No'].value_counts().head(10)
        for book, count in book_counts.items():
            print(f"  Book {book}: {count} hadith")
        
        return stats
    
    def export_results(self, df, output_format='csv', filename='search_results'):
        """
        Export search results to a file.
        
        Args:
            df (pandas.DataFrame): Results to export
            output_format (str): 'csv' or 'excel'
            filename (str): Output filename (without extension)
        """
        if output_format == 'csv':
            df.to_csv(f'{filename}.csv', index=False, encoding='utf-8-sig')
            print(f"Results exported to {filename}.csv")
        elif output_format == 'excel':
            df.to_excel(f'{filename}.xlsx', index=False)
            print(f"Results exported to {filename}.xlsx")
        else:
            print("Unsupported format. Use 'csv' or 'excel'.")

# Example usage and interactive interface
def main():
    # Ask for CSV file path
    csv_path = input("Enter the path to your CSV file: ").strip()
    
    # Initialize the analyzer
    analyzer = HadithAnalyzer(csv_path)
    
    while True:
        print("\n" + "="*50)
        print("HADITH TEXT ANALYSIS MENU")
        print("="*50)
        print("1. Search in Arabic text")
        print("2. Search by Book Number")
        print("3. Search by SN Range")
        print("4. Show Statistics")
        print("5. Export current view")
        print("6. Display sample hadith")
        print("7. Exit")
        print("="*50)
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            query = input("Enter search term (Arabic): ").strip()
            if not query:
                print("Search term cannot be empty!")
                continue
                
            print("\nSearch in which column?")
            print("1. Both columns")
            print("2. Arabic without Tashkeel only")
            print("3. Arabic with Tashkeel only")
            col_choice = input("Enter choice (1-3): ").strip()
            
            if col_choice == '1':
                search_column = 'both'
            elif col_choice == '2':
                search_column = 'without_tashkeel'
            elif col_choice == '3':
                search_column = 'with_tashkeel'
            else:
                print("Invalid choice. Defaulting to 'both'.")
                search_column = 'both'
            
            results = analyzer.search_arabic_text(query, search_column)
            if not results.empty:
                print("\nSearch Results:")
                print(results[['SN', 'Hadith_Book_No']].head(20))
                
                # Show details for first result
                if input("\nShow details of first result? (y/n): ").lower() == 'y':
                    first = results.iloc[0]
                    print(f"\nSN: {first['SN']}")
                    print(f"Book No: {first['Hadith_Book_No']}")
                    print(f"Arabic without Tashkeel:\n{first['Arabic_without_TASHKEEL'][:500]}...")
                    print(f"\nArabic with Tashkeel:\n{first['Arabic_TASHKEEL'][:500]}...")
        
        elif choice == '2':
            try:
                book_no = input("Enter Book Number to search: ").strip()
                results = analyzer.search_by_book_no(book_no)
                if not results.empty:
                    print("\nResults:")
                    print(results[['SN', 'Hadith_Book_No']])
            except Exception as e:
                print(f"Error: {e}")
        
        elif choice == '3':
            try:
                start = int(input("Enter starting SN: "))
                end = int(input("Enter ending SN: "))
                results = analyzer.search_by_sn_range(start, end)
                if not results.empty:
                    print("\nResults:")
                    print(results[['SN', 'Hadith_Book_No']])
            except ValueError:
                print("Please enter valid numbers!")
        
        elif choice == '4':
            analyzer.get_statistics()
        
        elif choice == '5':
            if 'results' in locals() and not results.empty:
                format_choice = input("Export as (1) CSV or (2) Excel? Enter 1 or 2: ").strip()
                filename = input("Enter filename (without extension): ").strip()
                if format_choice == '1':
                    analyzer.export_results(results, 'csv', filename)
                elif format_choice == '2':
                    analyzer.export_results(results, 'excel', filename)
                else:
                    print("Invalid choice. Using CSV format.")
                    analyzer.export_results(results, 'csv', filename)
            else:
                print("No results to export. Perform a search first!")
        
        elif choice == '6':
            n = input("How many hadith to display? (default: 5): ").strip()
            n = int(n) if n.isdigit() else 5
            print(f"\nFirst {n} hadith:")
            print(analyzer.df.head(n))
        
        elif choice == '7':
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please enter a number between 1 and 7.")

# If running as a script
if __name__ == "__main__":
    main()