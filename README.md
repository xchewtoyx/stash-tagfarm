# Stash TagFarm

A CLI tool for creating linkfarms from StashApp data. Organize your media files by creating symbolic links grouped by tags and performers.

## Features

- **Tag-based organization**: Create directories and symlinks for scenes with specific tags
- **Performer-based organization**: Create directories and symlinks for scenes featuring specific performers  
- **Flexible configuration**: Use favourite tags/performers or manually specify them
- **Smart naming**: Use scene titles or original filenames for symlinks
- **Dry-run support**: Preview changes before applying them
- **Link maintenance**: Clean up dangling symlinks automatically
- **Rich CLI**: Beautiful command-line interface with progress tracking

## Installation

```bash
# Install from source
git clone https://github.com/xchewtoyx/stash-tagfarm.git
cd stash-tagfarm
pip install -e .
```

## Quick Start

1. **Initialize configuration**:
   ```bash
   tagfarm init
   ```

2. **Edit the configuration file** (`tagfarm.yaml`):
   ```yaml
   stash_url: http://localhost:9999/graphql
   farm_path: /path/to/your/linkfarm
   use_title: true
   
   tags:
     favourite: true
     names:
       - "Specific Tag Name"
   
   performers:
     favourite: true  
     names:
       - "Specific Performer Name"
   ```

3. **Build your linkfarm**:
   ```bash
   tagfarm build
   ```

4. **Clean up dangling links**:
   ```bash
   tagfarm clean
   ```

## Commands

### `tagfarm build`
Build the linkfarm from StashApp data based on your configuration.

**Options:**
- `--dry-run`: Preview what would be created without making changes
- `--config, -c`: Specify configuration file path (default: `tagfarm.yaml`)
- `--verbose, -v`: Enable verbose output

**Example:**
```bash
# Build with dry-run to preview
tagfarm build --dry-run

# Build with custom config
tagfarm build --config /path/to/config.yaml
```

### `tagfarm clean`
Clean up dangling symlinks in the linkfarm.

**Options:**
- `--dry-run`: Show what would be removed without making changes
- `--config, -c`: Specify configuration file path
- `--verbose, -v`: Enable verbose output

**Example:**
```bash
# Preview cleanup
tagfarm clean --dry-run

# Actually remove dangling links
tagfarm clean
```

### `tagfarm init`
Create a sample configuration file.

**Options:**
- `--output, -o`: Output path for configuration file (default: `tagfarm.yaml`)

**Example:**
```bash
# Create config in current directory
tagfarm init

# Create config at specific path
tagfarm init --output /path/to/config.yaml
```

## Configuration

The configuration file uses YAML format with the following structure:

```yaml
# StashApp connection
stash_url: http://localhost:9999/graphql
api_key: null  # Optional API key for authentication

# LinkFarm settings
farm_path: /path/to/linkfarm
use_title: true  # Use scene title instead of filename

# Tag processing
tags:
  favourite: true  # Include all favourite tags
  names:           # Manual tag names to include
    - "Specific Tag"
    - "Another Tag"

# Performer processing  
performers:
  favourite: true  # Include all favourite performers
  names:           # Manual performer names to include
    - "Performer Name"  
    - "Another Performer"
```

### Configuration Options

- **`stash_url`**: GraphQL endpoint URL for your StashApp instance
- **`api_key`**: Optional API key if your StashApp requires authentication
- **`farm_path`**: Directory where the linkfarm will be created
- **`use_title`**: Use scene titles for link names instead of original filenames
- **`tags.favourite`**: Include all tags marked as favourite in StashApp
- **`tags.names`**: List of specific tag names to include
- **`performers.favourite`**: Include all performers marked as favourite in StashApp  
- **`performers.names`**: List of specific performer names to include

## Directory Structure

The linkfarm is organized as follows:

```
/path/to/linkfarm/
├── tags/
│   ├── Tag Name 1/
│   │   ├── Scene Title 1.mp4 -> /original/path/file1.mp4
│   │   └── Scene Title 2.mp4 -> /original/path/file2.mp4
│   └── Tag Name 2/
│       └── Scene Title 3.mp4 -> /original/path/file3.mp4
└── performers/
    ├── Performer Name 1/
    │   ├── Scene Title 1.mp4 -> /original/path/file1.mp4
    │   └── Scene Title 2.mp4 -> /original/path/file2.mp4
    └── Performer Name 2/
        └── Scene Title 3.mp4 -> /original/path/file3.mp4
```

## Requirements

- Python 3.8+
- StashApp with GraphQL API enabled
- Access to the media files (for creating symlinks)

## License

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.