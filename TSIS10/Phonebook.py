import psycopg2
import csv
from psycopg2 import sql

class PhoneBook:
    def __init__(self, dbname, user, password, host='localhost', port='5432'):
        """Initialize database connection"""
        try:
            # Set client encoding to UTF8 explicitly
            self.conn = psycopg2.connect(
                dbname=dbname,
                user="postgres",
                password="MyNewPassword123!",
                host=host,
                port=port,
                client_encoding='UTF8',
                options='-c client_encoding=UTF8'
            )
            self.cursor = self.conn.cursor()
            print("Database connection established successfully")
        except Exception as e:
            print(f"Error connecting to database: {e}")
            raise

    def create_tables(self):
        """Create PhoneBook tables"""
        create_users_table = """
        CREATE TABLE IF NOT EXISTS users (
            user_id SERIAL PRIMARY KEY,
            first_name VARCHAR(50) NOT NULL,
            last_name VARCHAR(50) NOT NULL,
            email VARCHAR(100) UNIQUE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        
        create_phones_table = """
        CREATE TABLE IF NOT EXISTS phones (
            phone_id SERIAL PRIMARY KEY,
            user_id INTEGER REFERENCES users(user_id) ON DELETE CASCADE,
            phone_number VARCHAR(20) NOT NULL,
            phone_type VARCHAR(20) DEFAULT 'mobile',
            is_primary BOOLEAN DEFAULT FALSE
        );
        """
        
        try:
            self.cursor.execute(create_users_table)
            self.cursor.execute(create_phones_table)
            self.conn.commit()
            print("Tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")
            self.conn.rollback()

    def insert_user_console(self):
        """Insert user data from console input"""
        print("\n--- Add New Contact ---")
        first_name = input("Enter first name: ")
        last_name = input("Enter last name: ")
        email = input("Enter email (optional): ") or None
        phone_number = input("Enter phone number: ")
        phone_type = input("Enter phone type (mobile/home/work) [mobile]: ") or 'mobile'
        
        try:
            # Insert user
            insert_user_query = """
            INSERT INTO users (first_name, last_name, email)
            VALUES (%s, %s, %s) RETURNING user_id;
            """
            self.cursor.execute(insert_user_query, (first_name, last_name, email))
            user_id = self.cursor.fetchone()[0]
            
            # Insert phone
            insert_phone_query = """
            INSERT INTO phones (user_id, phone_number, phone_type, is_primary)
            VALUES (%s, %s, %s, TRUE);
            """
            self.cursor.execute(insert_phone_query, (user_id, phone_number, phone_type))
            
            self.conn.commit()
            print(f"Contact added successfully with ID: {user_id}")
        except Exception as e:
            print(f"Error inserting user: {e}")
            self.conn.rollback()

    def insert_from_csv(self, csv_file):
        """Insert data from CSV file"""
        try:
            with open(csv_file, 'r') as file:
                csv_reader = csv.DictReader(file)
                count = 0
                
                for row in csv_reader:
                    # Insert user
                    insert_user_query = """
                    INSERT INTO users (first_name, last_name, email)
                    VALUES (%s, %s, %s) RETURNING user_id;
                    """
                    self.cursor.execute(insert_user_query, 
                                      (row['first_name'], row['last_name'], 
                                       row.get('email', None)))
                    user_id = self.cursor.fetchone()[0]
                    
                    # Insert phone
                    insert_phone_query = """
                    INSERT INTO phones (user_id, phone_number, phone_type, is_primary)
                    VALUES (%s, %s, %s, %s);
                    """
                    self.cursor.execute(insert_phone_query, 
                                      (user_id, row['phone_number'], 
                                       row.get('phone_type', 'mobile'), True))
                    count += 1
                
                self.conn.commit()
                print(f"Successfully imported {count} contacts from CSV")
        except Exception as e:
            print(f"Error importing from CSV: {e}")
            self.conn.rollback()

    def update_user(self, user_id, first_name=None, phone_number=None):
        """Update user information"""
        try:
            if first_name:
                update_query = "UPDATE users SET first_name = %s WHERE user_id = %s;"
                self.cursor.execute(update_query, (first_name, user_id))
            
            if phone_number:
                update_query = """
                UPDATE phones SET phone_number = %s 
                WHERE user_id = %s AND is_primary = TRUE;
                """
                self.cursor.execute(update_query, (phone_number, user_id))
            
            self.conn.commit()
            print(f"User {user_id} updated successfully")
        except Exception as e:
            print(f"Error updating user: {e}")
            self.conn.rollback()

    def query_all_contacts(self):
        """Query all contacts"""
        query = """
        SELECT u.user_id, u.first_name, u.last_name, u.email, 
               p.phone_number, p.phone_type
        FROM users u
        LEFT JOIN phones p ON u.user_id = p.user_id
        ORDER BY u.last_name, u.first_name;
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def query_by_name(self, name):
        """Query contacts by name (first or last)"""
        query = """
        SELECT u.user_id, u.first_name, u.last_name, u.email, 
               p.phone_number, p.phone_type
        FROM users u
        LEFT JOIN phones p ON u.user_id = p.user_id
        WHERE u.first_name ILIKE %s OR u.last_name ILIKE %s;
        """
        self.cursor.execute(query, (f'%{name}%', f'%{name}%'))
        return self.cursor.fetchall()

    def query_by_phone(self, phone):
        """Query contacts by phone number"""
        query = """
        SELECT u.user_id, u.first_name, u.last_name, u.email, 
               p.phone_number, p.phone_type
        FROM users u
        JOIN phones p ON u.user_id = p.user_id
        WHERE p.phone_number LIKE %s;
        """
        self.cursor.execute(query, (f'%{phone}%',))
        return self.cursor.fetchall()

    def delete_by_user_id(self, user_id):
        """Delete contact by user ID"""
        try:
            delete_query = "DELETE FROM users WHERE user_id = %s;"
            self.cursor.execute(delete_query, (user_id,))
            self.conn.commit()
            print(f"User {user_id} deleted successfully")
        except Exception as e:
            print(f"Error deleting user: {e}")
            self.conn.rollback()

    def delete_by_phone(self, phone_number):
        """Delete contact by phone number"""
        try:
            # First find the user_id
            find_query = "SELECT user_id FROM phones WHERE phone_number = %s;"
            self.cursor.execute(find_query, (phone_number,))
            result = self.cursor.fetchone()
            
            if result:
                user_id = result[0]
                delete_query = "DELETE FROM users WHERE user_id = %s;"
                self.cursor.execute(delete_query, (user_id,))
                self.conn.commit()
                print(f"Contact with phone {phone_number} deleted successfully")
            else:
                print("Phone number not found")
        except Exception as e:
            print(f"Error deleting by phone: {e}")
            self.conn.rollback()

    def display_contacts(self, contacts):
        """Display contacts in formatted way"""
        if not contacts:
            print("No contacts found")
            return
        
        print("\n" + "="*80)
        print(f"{'ID':<5} {'Name':<25} {'Email':<25} {'Phone':<15} {'Type':<10}")
        print("="*80)
        for contact in contacts:
            user_id, first, last, email, phone, phone_type = contact
            name = f"{first} {last}"
            email = email or "N/A"
            phone = phone or "N/A"
            phone_type = phone_type or "N/A"
            print(f"{user_id:<5} {name:<25} {email:<25} {phone:<15} {phone_type:<10}")
        print("="*80 + "\n")

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()
        print("Database connection closed")


def main():
    # Initialize PhoneBook
    phonebook = PhoneBook(
        dbname='phonebook_db',
        user='postgres',
        password='your_password',
        host='localhost'
    )
    
    # Create tables
    phonebook.create_tables()
    
    while True:
        print("\n=== PhoneBook Menu ===")
        print("1. Add contact (console)")
        print("2. Import contacts from CSV")
        print("3. Update contact")
        print("4. View all contacts")
        print("5. Search by name")
        print("6. Search by phone")
        print("7. Delete contact by ID")
        print("8. Delete contact by phone")
        print("9. Exit")
        
        choice = input("\nEnter your choice: ")
        
        if choice == '1':
            phonebook.insert_user_console()
        
        elif choice == '2':
            csv_file = input("Enter CSV file path: ")
            phonebook.insert_from_csv(csv_file)
        
        elif choice == '3':
            user_id = int(input("Enter user ID to update: "))
            first_name = input("Enter new first name (or press Enter to skip): ")
            phone = input("Enter new phone number (or press Enter to skip): ")
            phonebook.update_user(
                user_id, 
                first_name if first_name else None,
                phone if phone else None
            )
        
        elif choice == '4':
            contacts = phonebook.query_all_contacts()
            phonebook.display_contacts(contacts)
        
        elif choice == '5':
            name = input("Enter name to search: ")
            contacts = phonebook.query_by_name(name)
            phonebook.display_contacts(contacts)
        
        elif choice == '6':
            phone = input("Enter phone to search: ")
            contacts = phonebook.query_by_phone(phone)
            phonebook.display_contacts(contacts)
        
        elif choice == '7':
            user_id = int(input("Enter user ID to delete: "))
            phonebook.delete_by_user_id(user_id)
        
        elif choice == '8':
            phone = input("Enter phone number to delete: ")
            phonebook.delete_by_phone(phone)
        
        elif choice == '9':
            phonebook.close()
            print("Goodbye!")
            break
        
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()