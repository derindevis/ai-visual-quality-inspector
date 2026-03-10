from database import create_user

# Create admin user
create_user(
    username = "admin",
    name     = "Derin Devis",
    email    = "derindevis79@gmail.com",
    password = "admin123",
    role     = "admin"
)

# Create viewer user
create_user(
    username = "viewer",
    name     = "saurabh T.J",
    email    = "saurabhjijil@gmail.com",
    password = "viewer123",
    role     = "viewer"
)

print("\n✅ All users created successfully!")
print("You can now view them in SQLite Viewer in VS Code!")