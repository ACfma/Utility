#!/bin/bash

REPO_PATH=$1
SOURCE_BRANCH=$2
TARGET_DIR=$3

# Check required arguments
if [ $# -ne 3 ]; then
    echo "Input parameters must 3:"
    echo "  repository_path : Path to your Git repository"
    echo "  source_branch  : Name of the Git branch to compare against current branch"
    echo "  target_directory : Directory where modified files will be copied"
    exit 1
fi

#Initial warning to avoid misunderstandings
echo "DISCLAIMER: This program relies on the branch whos files should be copied elseware to be already checked out at the time of running this script."
echo "Did you properly checked out your repository at the desired branch/commit?[y/n]"
will=""
while [ "$will" != "y" ]
do
	read will
	case "$will" in
		"y")
			echo "Perfect! Let's proceed...";;
		"n")
			echo "No problem, come back when you're ready <3"
			exit 0;;	
		*)
			echo "Input should be 'y' or 'n' (lowercase).";;	
	esac
done

# Verify repository exists by looking for the .git file
if [ ! -d "$REPO_PATH/.git" ]; then
    echo "Error: '$REPO_PATH' is not a valid Git repository"
    exit 1
fi

# Create target directory if it doesn't already exist
mkdir -p "$TARGET_DIR"

# Get current branch name (needed for finding common ancestor)
CURRENT_BRANCH=$(cd "$REPO_PATH" && git symbolic-ref --short HEAD)

# Verify source branch exists
if ! cd "$REPO_PATH" && git show-ref --verify --quiet refs/heads/$SOURCE_BRANCH; then
    echo "Error: Branch '$SOURCE_BRANCH' does not exist"
    exit 1
fi

# Get common ancestor hash
COMMON_ANCESTOR=$(cd "$REPO_PATH" && git merge-base $CURRENT_BRANCH $SOURCE_BRANCH)

# Find modified files since common ancestor
MODIFIED_FILES=$(cd "$REPO_PATH" && git diff --name-only $COMMON_ANCESTOR..HEAD)

# Process each modified file
echo "Copying modified files..."
for file in $MODIFIED_FILES; do
    # Skip deleted files
    if [ -f "$REPO_PATH/$file" ]; then
        # Create parent directories in target if they don't exist
        target_path="$TARGET_DIR/${file%/*}"
        mkdir -p "$target_path"
        
        # Copy the file
        cp -p "$REPO_PATH/$file" "$target_path/"
        echo "Copied: $file"
    fi
done

echo "Copy operation completed."


