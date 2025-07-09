# HDF5 File Manager

A Python-based ncurses interface for browsing and manipulating HDF5 files.

## Features

- **Interactive browsing**: Navigate through HDF5 file structure using arrow keys
- **Group export**: Export entire groups to separate HDF5 files
- **CSV conversion**: Convert datasets to CSV format
- **Dataset information**: View detailed information about datasets including shape, type, and attributes
- **Intuitive interface**: Easy-to-use ncurses-based terminal interface
- **Command-line arguments**: Open files directly from command line

## Installation

1. Run the setup script:
```bash
./scripts/setup.sh
```

Or install manually:
```bash
pip install h5py pandas numpy
```

## Usage

### Basic Usage
```bash
python3 scripts/hdf5_manager.py
```

### Open specific file
```bash
python3 scripts/hdf5_manager.py data.h5
python3 scripts/hdf5_manager.py /path/to/file.hdf5
python3 scripts/hdf5_manager.py --file experiment.h5
```

### Check dependencies
```bash
python3 scripts/hdf5_manager.py --check-deps
```

### Get help
```bash
python3 scripts/hdf5_manager.py --help
```

### Create test data
```bash
python3 scripts/create_test_hdf5.py
```

## Command Line Arguments

| Argument | Description |
|----------|-------------|
| `file` | HDF5 file to open on startup (positional) |
| `-f, --file` | HDF5 file to open on startup (named argument) |
| `--check-deps` | Check if all required dependencies are installed |
| `-v, --version` | Show version information |
| `-h, --help` | Show help message with examples |

## Controls

| Key | Action |
|-----|--------|
| `o` | Open HDF5 file |
| `↑/↓` | Navigate up/down |
| `Enter` | Enter group or navigate to parent |
| `e` | Export selected group to HDF5 file |
| `c` | Export selected dataset to CSV |
| `i` | Show detailed dataset information |
| `q` | Quit application |

## Interface Elements

- 📁 **Groups**: Directories that can contain other groups or datasets
- 📄 **Datasets**: Data arrays with shape and type information
- **Selected item**: Highlighted in reverse colors
- **Status bar**: Shows current file and path
- **Help bar**: Shows available commands

## File Operations

### Export Group to HDF5
1. Navigate to desired group
2. Press `e`
3. Enter output filename
4. Group and all contents will be exported

### Export Dataset to CSV
1. Navigate to desired dataset
2. Press `c`
3. Enter output filename
4. Dataset will be converted to CSV format

### View Dataset Information
1. Navigate to desired dataset
2. Press `i`
3. View shape, type, size, and attributes

## Examples

```bash
# Start with no file
python3 scripts/hdf5_manager.py

# Open file on startup
python3 scripts/hdf5_manager.py data.h5

# Open file with full path
python3 scripts/hdf5_manager.py /home/user/experiments/results.hdf5

# Alternative syntax
python3 scripts/hdf5_manager.py --file data.h5

# Check if dependencies are installed
python3 scripts/hdf5_manager.py --check-deps

# Create test file and open it
python3 scripts/create_test_hdf5.py
python3 scripts/hdf5_manager.py test_data.h5
```

## Error Handling

The application includes comprehensive error handling for:
- File access issues
- Invalid HDF5 files
- Missing files
- Corrupted HDF5 files
- Export failures
- Navigation errors
- Missing dependencies

## Requirements

- Python 3.6+
- h5py >= 3.0.0
- pandas >= 1.3.0
- numpy >= 1.20.0
- curses (included with Python on Unix systems)

## Limitations

- Read-only access to HDF5 files
- CSV export works best with 1D and 2D datasets
- Terminal size affects display capacity
- Requires Unix-like system for ncurses support

## Troubleshooting

### Missing Dependencies
```bash
python3 scripts/hdf5_manager.py --check-deps
pip install h5py pandas numpy
```

### File Not Found
- Check file path is correct
- Use absolute paths if needed
- Ensure file has proper permissions

### Invalid HDF5 File
- Verify file is not corrupted
- Check file was created properly
- Try opening with h5py directly to test
```

Let me test the updated script to make sure it works:

```bash
python3 scripts/hdf5_manager.py --help

