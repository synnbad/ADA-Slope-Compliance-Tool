import os

# List of relative paths where we want .gitkeep files
folders = [
    "data/raw",
    "data/processed",
    "notebooks",
    "scripts",
    "outputs/maps",
    "outputs/reports",
    "docs"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)  # Ensure folder exists
    keep_path = os.path.join(folder, ".gitkeep")
    with open(keep_path, "w") as f:
        pass  # Create empty file
    print(f"✔️  .gitkeep added in {folder}")
