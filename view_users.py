import sqlite3

# Connect to the database
conn = sqlite3.connect('backend/civicfix.db')
cursor = conn.cursor()

# Query all users
cursor.execute('SELECT email, role, first_name, last_name, created_at FROM users')
results = cursor.fetchall()

print("\n" + "="*80)
print("REGISTERED USERS IN DATABASE")
print("="*80 + "\n")

if not results:
    print("No users found in database.\n")
else:
    for idx, user in enumerate(results, 1):
        email, role, first_name, last_name, created_at = user
        print(f"User #{idx}")
        print(f"  Email:      {email}")
        print(f"  Name:       {first_name} {last_name}")
        print(f"  Role:       {role}")
        print(f"  Created:    {created_at}")
        print("-" * 80)

print(f"\nTotal Users: {len(results)}\n")

# Show seed file default credentials
print("="*80)
print("DEFAULT SEED CREDENTIALS (if database was seeded)")
print("="*80)
print("\n  Municipal Officer:")
print("    Email:    officer@civicfix.local")
print("    Password: officer123")
print("\n  Test Citizen:")
print("    Email:    citizen@civicfix.local")
print("    Password: citizen123")
print("\n" + "="*80)
print("\nNOTE: Passwords are hashed in the database and cannot be retrieved.")
print("If you forgot your password for a custom account, you'll need to create a new one.")
print("="*80 + "\n")

conn.close()
