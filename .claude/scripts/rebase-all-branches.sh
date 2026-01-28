#!/bin/bash

# Script to rebase all challenge branches on the latest main branch
# This propagates README updates from main to all challenge branches

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Rebasing All Challenge Branches on Main ===${NC}\n"

# Save the current branch
ORIGINAL_BRANCH=$(git branch --show-current)
echo -e "${BLUE}Current branch: ${ORIGINAL_BRANCH}${NC}"

# Ensure we're in a clean working state
if ! git diff-index --quiet HEAD --; then
    echo -e "${RED}Error: You have uncommitted changes. Please commit or stash them first.${NC}"
    exit 1
fi

# Update main branch
echo -e "\n${BLUE}Updating main branch...${NC}"
git checkout main
git pull origin main 2>/dev/null || echo -e "${YELLOW}Note: Could not pull from remote. Using local main.${NC}"

# Get all branches except main and the current branch marker
echo -e "\n${BLUE}Finding all challenge branches...${NC}"
ALL_BRANCHES=$(git branch | grep -v "main" | grep -v "^\*" | sed 's/^[* ] //' | tr -d ' ')

if [ -z "$ALL_BRANCHES" ]; then
    echo -e "${YELLOW}No challenge branches found to rebase.${NC}"
    git checkout "$ORIGINAL_BRANCH"
    exit 0
fi

echo -e "${GREEN}Found branches:${NC}"
echo "$ALL_BRANCHES" | while read -r branch; do
    echo "  - $branch"
done

# Track success/failure
SUCCESSFUL_REBASES=()
FAILED_REBASES=()

# Rebase each branch
echo -e "\n${BLUE}Starting rebase process...${NC}\n"
for branch in $ALL_BRANCHES; do
    echo -e "${BLUE}Processing branch: ${branch}${NC}"

    # Checkout the branch
    if ! git checkout "$branch"; then
        echo -e "${RED}Failed to checkout ${branch}${NC}"
        FAILED_REBASES+=("$branch (checkout failed)")
        continue
    fi

    # Attempt rebase
    if git rebase main; then
        echo -e "${GREEN}✓ Successfully rebased ${branch}${NC}\n"
        SUCCESSFUL_REBASES+=("$branch")
    else
        echo -e "${RED}✗ Rebase conflict in ${branch}${NC}"
        echo -e "${YELLOW}Aborting rebase for ${branch}${NC}\n"
        git rebase --abort
        FAILED_REBASES+=("$branch (rebase conflict)")
    fi
done

# Return to original branch
echo -e "${BLUE}Returning to original branch: ${ORIGINAL_BRANCH}${NC}"
git checkout "$ORIGINAL_BRANCH"

# Summary
echo -e "\n${BLUE}=== Rebase Summary ===${NC}"
echo -e "${GREEN}Successful (${#SUCCESSFUL_REBASES[@]}):${NC}"
for branch in "${SUCCESSFUL_REBASES[@]}"; do
    echo "  ✓ $branch"
done

if [ ${#FAILED_REBASES[@]} -gt 0 ]; then
    echo -e "\n${RED}Failed (${#FAILED_REBASES[@]}):${NC}"
    for branch in "${FAILED_REBASES[@]}"; do
        echo "  ✗ $branch"
    done
    echo -e "\n${YELLOW}You'll need to manually resolve conflicts in failed branches:${NC}"
    echo "  1. git checkout <branch-name>"
    echo "  2. git rebase main"
    echo "  3. Resolve conflicts"
    echo "  4. git rebase --continue"
fi

# Option to push
if [ ${#SUCCESSFUL_REBASES[@]} -gt 0 ]; then
    echo -e "\n${YELLOW}To push the rebased branches to remote, run:${NC}"
    for branch in "${SUCCESSFUL_REBASES[@]}"; do
        echo "  git push origin $branch --force-with-lease"
    done
    echo -e "\n${YELLOW}Or push all at once with:${NC}"
    echo "  git push origin --force-with-lease --all"
fi

echo -e "\n${GREEN}Done!${NC}"
