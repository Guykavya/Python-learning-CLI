name = input()
print(f"Image: {name.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))}")
print(f"Hidden: {name.startswith('.')}")
print(f"Backup: {name.endswith(('~', '.bak'))}")
