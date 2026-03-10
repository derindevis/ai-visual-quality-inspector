import bcrypt

passwords = ["admin123", "viewer123"]
names = ["Admin", "Viewer"]

print("=" * 50)
print("Copy these hashed passwords!")
print("=" * 50)

for i, password in enumerate(passwords):
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    print(f"{names[i]} hashed password:")
    print(hashed.decode('utf-8'))
    print("=" * 50)