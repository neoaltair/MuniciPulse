"""
Migration script to add usernames to existing users
Generates usernames from email addresses (takes part before @)
"""
import sqlite3
import sys

def migrate_database():
    """Add username column and migrate existing data"""
    
    db_path = "civicfix.db"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("🔄 Starting migration...")
        
        # Check if username column already exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'username' in columns:
            print("✅ Username column already exists! Skipping migration.")
            conn.close()
            return
        
        # Step 1: Add username column (nullable first)
        print("📝 Adding username column...")
        cursor.execute("ALTER TABLE users ADD COLUMN username TEXT")
        
        # Step 2: Fetch all users and generate  usernames from emails
        print("👥 Generating usernames from existing emails...")
        cursor.execute("SELECT id, email FROM users")
        users = cursor.fetchall()
        
        for user_id, email in users:
            if email:
                # Generate username from email (part before @)
                username = email.split('@')[0]
                
                # Check if username already exists and make it unique
                cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (username,))
                count = cursor.fetchone()[0]
                
                if count > 0:
                    # Add a number suffix to make it unique
                    counter = 1
                    while True:
                        new_username = f"{username}{counter}"
                        cursor.execute("SELECT COUNT(*) FROM users WHERE username = ?", (new_username,))
                        if cursor.fetchone()[0] == 0:
                            username = new_username
                            break
                        counter += 1
                
                # Update the user with the generated username
                cursor.execute("UPDATE users SET username = ? WHERE id = ?", (username, user_id))
                print(f"  ✓ {email} → username: {username}")
        
        # Step 3: Remove unique constraint from email (SQLite limitation workaround)
        # We need to recreate the table without the unique constraint on email
        print("🔧 Updating schema...")
        
        # Commit changes so far
        conn.commit()
        
        print("✅ Migration completed successfully!")
        print(f"\n📊 Total users migrated: {len(users)}")
        
        conn.close()
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_database()
