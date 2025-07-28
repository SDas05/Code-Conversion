#!/usr/bin/env python3
# Official build script from py-tree-sitter repo
import argparse
import os
import subprocess
import sys

parser = argparse.ArgumentParser(description="Build a Tree-sitter language shared library.")
parser.add_argument("output", help="Path to output .so file")
parser.add_argument("repos", nargs='+', help="Paths to grammar repositories")
args = parser.parse_args()

output_path = os.path.abspath(args.output)
repo_paths = [os.path.abspath(repo) for repo in args.repos]

print(f"Building shared library: {output_path}")
print(f"Using grammars: {repo_paths}")

cmd = [
    "gcc",
    "-shared",
    "-I", os.path.join("vendor", "tree-sitter-core", "lib", "include"),
    "-I", os.path.join("vendor", "tree-sitter-core", "lib", "src"),
]

# Add only lib.c from tree-sitter core (contains all core functionality)
cmd.append(os.path.join("vendor", "tree-sitter-core", "lib", "src", "lib.c"))

# Add grammar-specific include paths
for repo in repo_paths:
    cmd.extend(["-I", repo])
    common_dir = os.path.join(repo, "common")
    if os.path.isdir(common_dir):
        cmd.extend(["-I", common_dir])

cmd.extend(["-o", output_path])

# Add grammar source files
for repo in repo_paths:
    cmd.append(os.path.join(repo, "src", "parser.c"))
    scanner_path = os.path.join(repo, "src", "scanner.c")
    if os.path.exists(scanner_path):
        cmd.append(scanner_path)

print("Running:", ' '.join(cmd))
subprocess.run(cmd, check=True)
print(f"Built shared library at {output_path}")
