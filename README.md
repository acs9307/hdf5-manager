# HDF5 File Manager

A Python-based ncurses interface for browsing and manipulating HDF5 files.

## Features

- **Interactive browsing**: Navigate through HDF5 file structure using arrow keys
- **Group export**: Export entire groups to separate HDF5 files
- **CSV conversion**: Convert datasets and groups to CSV format
- **Single datasets**: Export to single CSV file
- **Groups with single dataset**: Export to single CSV file
- **Groups with multiple datasets/subgroups**: Export to directory structure with CSV files
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
python3 hdf5-manager.py
```

### Open specific file
```bash
python3 hdf5-manager.py data.h5
python3 hdf5-manager.py /path/to/file.hdf5
python3 hdf5-manager.py --file experiment.h5
```

### Check dependencies
```bash
python3 hdf5-manager.py --check-deps
```

### Get help
```bash
python3 hdf5-manager.py --help
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
| `c` | Export selected group/dataset to CSV |
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

### Export to CSV
The CSV export functionality (`c` key) works intelligently based on what you select:

#### Single Dataset Export
1. Navigate to desired dataset
2. Press `c`
3. Enter output filename
4. Dataset will be converted to CSV format

#### Group Export to CSV
1. Navigate to desired group (or navigate inside the group)
2. Press `c`
3. Enter output path (file/directory name)

**Export behavior:**
- **Single dataset**: Creates one CSV file
- **Group with datasets**: Creates one CSV file combining all datasets in that group
- **Group with subgroups**: Creates directory named after the group, with CSV files for each subgroup's datasets
- **Mixed groups**: Creates CSV file for current group's datasets AND directory for subgroups

#### CSV Export Examples
```
HDF5 Structure:          CSV Output:
/experiment/             experiment.csv (contains data1, data2 combined)
├── data1               experiment/
├── data2               ├── analysis.csv (contains stats, plots combined)
├── analysis/           └── results/
│   ├── stats           │   ├── trial1.csv
│   └── plots           │   └── trial2.csv
└── results/            └── summary.csv (contains metadata)
  ├── trial1
  ├── trial2
  └── summary/
      └── metadata
```

### View Dataset Information
1. Navigate to desired dataset
2. Press `i`
3. View shape, type, size, and attributes

## Examples

```bash
# Start with no file
python3 hdf5-manager.py

# Open file on startup
python3 hdf5-manager.py data.h5

# Open file with full path
python3 hdf5-manager.py /home/user/experiments/results.hdf5

# Alternative syntax
python3 hdf5-manager.py --file data.h5

# Check if dependencies are installed
python3 hdf5-manager.py --check-deps

# Create test file and open it
python3 scripts/create_test_hdf5.py
python3 hdf5-manager.py test_data.h5
```

## CSV Export Features

### Data Type Handling
- **Scalar datasets**: Converted to single-row CSV
- **1D arrays**: Converted to single-column CSV
- **2D arrays**: Converted directly to CSV with proper columns
- **Higher dimensions**: Flattened to 2D format
- **Complex data types**: Handled gracefully with error information

### Directory Structure
When exporting groups with multiple items:
- Each dataset becomes a `.csv` file
- Each subgroup becomes a subdirectory
- Directory structure mirrors HDF5 group hierarchy
- File names match HDF5 dataset/group names

### Error Handling
- Invalid datasets create error information CSV
- Failed exports are reported but don't stop the process
- Partial exports are allowed (some files may succeed while others fail)

## Error Handling

The application includes comprehensive error handling for:
- File access issues
- Invalid HDF5 files
- Missing files
- Corrupted HDF5 files
- Export failures
- Navigation errors
- Missing dependencies
- CSV conversion errors
- Directory creation failures

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
- Very large datasets may consume significant memory during CSV conversion

## Troubleshooting

### Missing Dependencies
```bash
python3 hdf5-manager.py --check-deps
pip install h5py pandas numpy
```

### File Not Found
- Check file path is correct
- Use absolute paths if needed
- Ensure file has proper permissions

### CSV Export Issues
- Ensure sufficient disk space for output
- Check write permissions for output directory
- Large datasets may take time to convert

### Invalid HDF5 File
- Verify file is not corrupted
- Check file was created properly
- Try opening with h5py directly to test
```

Let me test the updated script to make sure it works:

```bash
python3 hdf5-manager.py --help
