#!/bin/bash

# --- CONFIGURATION ---
CONTAINER_NAME="n8n"                 # Your Docker container name
IMPORT_DIR="./imports"               # Where you upload your JSONs
DOCKER_PATH="/tmp/n8n_import"        # Internal container mapping

echo "🚀 Starting n8n Seamless Import..."

# 1. Check if the import directory has files
if [ -z "$(ls -A $IMPORT_DIR/*.json 2>/dev/null)" ]; then
    echo "ℹ️  Check: No .json files found in $IMPORT_DIR. Skipping."
    exit 0
fi

# 2. Run the n8n CLI command via Docker
echo "📦 Importing workflows into n8n..."
docker exec -u node $CONTAINER_NAME n8n import:workflow --separate --input=$DOCKER_PATH

# 3. Check if the command succeeded
if [ $? -eq 0 ]; then
    echo "✅ Success! Workflows imported."
    # 4. Cleanup (Security: Remove JSONs after import)
    rm $IMPORT_DIR/*.json
    echo "🧹 Cleanup: JSON files removed for security."
else
    echo "❌ Error: Import failed. Keeping files for debugging."
    exit 1
fi