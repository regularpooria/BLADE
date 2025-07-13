#!/bin/bash

# Directory to search (default to current dir if not specified)
SEARCH_DIR="${1:-.}"

echo "Searching for unique_chunks.json under: $SEARCH_DIR"

# Find all unique_chunks.json files, print their paths and sizes
find "$SEARCH_DIR" -type f -name 'unique_chunks.json' -print0 | \
    tee /tmp/unique_chunks_files.txt | \
    xargs -0 du -b | \
    tee /tmp/unique_chunks_sizes.txt

# Calculate total size
total_bytes=$(awk '{sum += $1} END {print sum}' /tmp/unique_chunks_sizes.txt)

# Print result
echo
echo "Total unique_chunks.json files found: $(wc -l < /tmp/unique_chunks_files.txt)"
echo "Total size in bytes:      $total_bytes"
echo "Total size in kilobytes:  $((total_bytes / 1024)) KB"
echo "Total size in megabytes:  $((total_bytes / 1048576)) MB"
