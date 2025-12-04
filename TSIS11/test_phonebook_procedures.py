import os
os.environ['PGCLIENTENCODING'] = 'UTF8'

import psycopg2
from psycopg2 import sql

class PhoneBookProcedures:
    def __init__(self, dbname, user, password, host='localhost', port='5432'):
        """Initialize database connection"""
        try:
            os.environ['PGHOST'] = host
            os.environ['PGPORT'] = str(port)
            os.environ['PGDATABASE'] = dbname
            os.environ['PGUSER'] = user
            os.environ['PGPASSWORD'] = password
            os.environ['PGCLIENTENCODING'] = 'UTF8'
            
            self.conn = psycopg2.connect('')
            self.conn.set_client_encoding('UTF8')
            self.cursor = self.conn.cursor()
            print("✓ Database connection established")
        except Exception as e:
            print(f"✗ Error connecting to database: {e}")
            raise

    def search_by_pattern(self, pattern):
        """Test search_contacts_by_pattern function"""
        print(f"\n{'='*80}")
        print(f"🔍 SEARCHING FOR PATTERN: '{pattern}'")
        print('='*80)
        
        try:
            self.cursor.execute("SELECT * FROM search_contacts_by_pattern(%s);", (pattern,))
            results = self.cursor.fetchall()
            
            if results:
                print(f"{'ID':<5} {'First Name':<15} {'Last Name':<15} {'Email':<25} {'Phone':<18} {'Type':<10}")
                print('-'*80)
                for row in results:
                    user_id, first, last, email, phone, ptype = row
                    email = email or "N/A"
                    phone = phone or "N/A"
                    ptype = ptype or "N/A"
                    print(f"{user_id:<5} {first:<15} {last:<15} {email:<25} {phone:<18} {ptype:<10}")
                print(f"\nFound {len(results)} result(s)")
            else:
                print("No results found")
        except Exception as e:
            print(f"✗ Error: {e}")

    def upsert_user(self, first_name, last_name, email, phone, phone_type='mobile'):
        """Test upsert_user_phone procedure"""
        print(f"\n{'='*80}")
        print(f"📝 UPSERTING USER: {first_name} {last_name}")
        print('='*80)
        
        try:
            self.cursor.execute(
                "CALL upsert_user_phone(%s, %s, %s, %s, %s);",
                (first_name, last_name, email, phone, phone_type)
            )
            self.conn.commit()
            
            # Get notices
            for notice in self.conn.notices:
                print(f"📢 {notice.strip()}")
            
            print("✓ Operation completed")
        except Exception as e:
            print(f"✗ Error: {e}")
            self.conn.rollback()

    def insert_multiple(self, users_data):
        """Test insert_multiple_users procedure"""
        print(f"\n{'='*80}")
        print(f"📦 INSERTING MULTIPLE USERS")
        print('='*80)
        
        try:
            self.cursor.execute("CALL insert_multiple_users(%s);", (users_data,))
            self.conn.commit()
            
            # Get notices
            for notice in self.conn.notices:
                print(f"📢 {notice.strip()}")
            
            # Show invalid records
            print(f"\n{'='*80}")
            print("❌ INVALID RECORDS LOG:")
            print('='*80)
            
            self.cursor.execute("""
                SELECT first_name, last_name, phone_number, error_message, logged_at
                FROM invalid_phones_log
                ORDER BY logged_at DESC
                LIMIT 10;
            """)
            
            invalid_records = self.cursor.fetchall()
            if invalid_records:
                print(f"{'First':<15} {'Last':<15} {'Phone':<18} {'Error':<30} {'Time':<20}")
                print('-'*80)
                for row in invalid_records:
                    first, last, phone, error, logged = row
                    print(f"{first:<15} {last:<15} {phone:<18} {error:<30} {str(logged)[:19]}")
            else:
                print("No invalid records")
                
        except Exception as e:
            print(f"✗ Error: {e}")
            self.conn.rollback()

    def get_paginated(self, limit=10, offset=0, order_by='last_name'):
        """Test get_contacts_paginated function"""
        print(f"\n{'='*80}")
        print(f"📄 PAGINATED RESULTS (Limit: {limit}, Offset: {offset}, Order: {order_by})")
        print('='*80)
        
        try:
            self.cursor.execute(
                "SELECT * FROM get_contacts_paginated(%s, %s, %s);",
                (limit, offset, order_by)
            )
            results = self.cursor.fetchall()
            
            if results:
                total_count = results[0][7] if results else 0
                print(f"Total records: {total_count}")
                print(f"Showing: {offset + 1} to {min(offset + limit, total_count)}")
                print()
                
                print(f"{'ID':<5} {'First':<12} {'Last':<12} {'Email':<22} {'Phone':<16} {'Type':<8}")
                print('-'*80)
                
                for row in results:
                    user_id, first, last, email, phone, ptype, created, total = row
                    email = (email or "N/A")[:20]
                    phone = phone or "N/A"
                    ptype = ptype or "N/A"
                    print(f"{user_id:<5} {first:<12} {last:<12} {email:<22} {phone:<16} {ptype:<8}")
            else:
                print("No results found")
                
        except Exception as e:
            print(f"✗ Error: {e}")

    def delete_contact(self, first_name=None, last_name=None, phone_number=None):
        """Test delete_contact procedure"""
        print(f"\n{'='*80}")
        print(f"🗑️  DELETING CONTACT")
        print('='*80)
        
        try:
            if phone_number:
                print(f"Deleting by phone: {phone_number}")
                self.cursor.execute(
                    "CALL delete_contact(p_phone_number => %s);",
                    (phone_number,)
                )
            elif first_name and last_name:
                print(f"Deleting by name: {first_name} {last_name}")
                self.cursor.execute(
                    "CALL delete_contact(p_first_name => %s, p_last_name => %s);",
                    (first_name, last_name)
                )
            else:
                print("✗ Must provide either phone_number OR both first_name and last_name")
                return
            
            self.conn.commit()
            
            # Get notices
            for notice in self.conn.notices:
                print(f"📢 {notice.strip()}")
                
        except Exception as e:
            print(f"✗ Error: {e}")
            self.conn.rollback()

    def show_all_contacts(self):
        """Show all contacts"""
        print(f"\n{'='*80}")
        print(f"📋 ALL CONTACTS")
        print('='*80)
        
        try:
            self.cursor.execute("""
                SELECT u.user_id, u.first_name, u.last_name, u.email,
                       p.phone_number, p.phone_type
                FROM users u
                LEFT JOIN phones p ON u.user_id = p.user_id
                ORDER BY u.last_name, u.first_name;
            """)
            results = self.cursor.fetchall()
            
            if results:
                print(f"{'ID':<5} {'First Name':<15} {'Last Name':<15} {'Email':<25} {'Phone':<18} {'Type':<10}")
                print('-'*80)
                for row in results:
                    user_id, first, last, email, phone, ptype = row
                    email = email or "N/A"
                    phone = phone or "N/A"
                    ptype = ptype or "N/A"
                    print(f"{user_id:<5} {first:<15} {last:<15} {email:<25} {phone:<18} {ptype:<10}")
                print(f"\nTotal: {len(results)} record(s)")
            else:
                print("No contacts found")
        except Exception as e:
            print(f"✗ Error: {e}")

    def close(self):
        """Close connection"""
        self.cursor.close()
        self.conn.close()
        print("\n✓ Connection closed")


def main():
    """Main test menu"""
    pb = PhoneBookProcedures(
        dbname='phonebook_db',
        user='postgres',
        password='MyNewPassword123!',
        host='localhost'
    )
    
    while True:
        print("\n" + "="*80)
        print("📞 PHONEBOOK - STORED PROCEDURES TEST MENU")
        print("="*80)
        print("1. Search by pattern")
        print("2. Insert/Update user (Upsert)")
        print("3. Insert multiple users")
        print("4. Get contacts with pagination")
        print("5. Delete contact")
        print("6. Show all contacts")
        print("7. Run demo tests")
        print("8. Exit")
        print("="*80)
        
        choice = input("\nEnter your choice: ")
        
        if choice == '1':
            pattern = input("Enter search pattern: ")
            pb.search_by_pattern(pattern)
        
        elif choice == '2':
            first = input("First name: ")
            last = input("Last name: ")
            email = input("Email (optional): ") or None
            phone = input("Phone number: ")
            ptype = input("Phone type [mobile]: ") or 'mobile'
            pb.upsert_user(first, last, email, phone, ptype)
        
        elif choice == '3':
            print("\nEnter users in format: FirstName,LastName,Email,Phone")
            print("Separate multiple users with semicolon (;)")
            print("Example: John,Doe,john@mail.com,+77771234567;Jane,Smith,jane@mail.com,+77772345678")
            users_data = input("\nUsers data: ")
            pb.insert_multiple(users_data)
        
        elif choice == '4':
            limit = int(input("Limit (default 10): ") or 10)
            offset = int(input("Offset (default 0): ") or 0)
            order = input("Order by (last_name/first_name/created_at) [last_name]: ") or 'last_name'
            pb.get_paginated(limit, offset, order)
        
        elif choice == '5':
            print("\nDelete by:")
            print("1. Phone number")
            print("2. Name")
            del_choice = input("Choice: ")
            
            if del_choice == '1':
                phone = input("Phone number: ")
                pb.delete_contact(phone_number=phone)
            elif del_choice == '2':
                first = input("First name: ")
                last = input("Last name: ")
                pb.delete_contact(first_name=first, last_name=last)
        
        elif choice == '6':
            pb.show_all_contacts()
        
        elif choice == '7':
            run_demo_tests(pb)
        
        elif choice == '8':
            pb.close()
            print("\n👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")


def run_demo_tests(pb):
    """Run demonstration tests"""
    print("\n" + "="*80)
    print("🎬 RUNNING DEMO TESTS")
    print("="*80)
    
    # Test 1: Insert users
    print("\n📝 Test 1: Inserting test users...")
    pb.upsert_user('Alice', 'Johnson', 'alice@test.com', '+77771111111', 'mobile')
    pb.upsert_user('Bob', 'Williams', 'bob@test.com', '+77772222222', 'work')
    pb.upsert_user('Charlie', 'Brown', 'charlie@test.com', '+77773333333', 'mobile')
    
    # Test 2: Search
    print("\n🔍 Test 2: Searching for 'Alice'...")
    pb.search_by_pattern('Alice')
    
    # Test 3: Update existing user
    print("\n📝 Test 3: Updating Alice's phone...")
    pb.upsert_user('Alice', 'Johnson', 'alice@test.com', '+77779999999', 'home')
    
    # Test 4: Insert multiple with some invalid
    print("\n📦 Test 4: Bulk insert with validation...")
    users_data = (
        "David,Miller,david@test.com,+77774444444;"
        "Eve,Davis,eve@test.com,+77775555555;"
        "Invalid,User,test@test.com,123;"  # Invalid phone
        "Frank,Wilson,frank@test.com,+7777"  # Too short
    )
    pb.insert_multiple(users_data)
    
    # Test 5: Pagination
    print("\n📄 Test 5: Paginated results...")
    pb.get_paginated(3, 0)
    
    # Test 6: Delete
    print("\n🗑️  Test 6: Deleting test user...")
    pb.delete_contact(first_name='Charlie', last_name='Brown')
    
    # Test 7: Show all
    print("\n📋 Test 7: Final state of all contacts...")
    pb.show_all_contacts()
    
    print("\n" + "="*80)
    print("✅ DEMO TESTS COMPLETED")
    print("="*80)


if __name__ == "__main__":
    main()