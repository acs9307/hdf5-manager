#!/usr/bin/env python3
"""
HDF5 File Manager with ncurses interface
Allows browsing, exporting subgroups, and converting to CSV
"""

import curses
import h5py
import pandas as pd
import numpy as np
import os
import sys
import argparse
from pathlib import Path
import traceback


class HDF5Manager:
    def __init__(self, stdscr):
        self.stdscr = stdscr
        self.current_file = None
        self.current_path = "/"
        self.items = []
        self.selected_index = 0
        self.scroll_offset = 0
        
        # Initialize colors
        curses.start_color()
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Selected
        curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)   # Directory
        curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # Dataset
        curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # Error
        curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK) # Info
        
        # Hide cursor
        curses.curs_set(0)
        
    def show_message(self, message, color_pair=0):
        """Display a message at the bottom of the screen"""
        height, width = self.stdscr.getmaxyx()
        self.stdscr.addstr(height - 1, 0, " " * (width - 1))
        self.stdscr.addstr(height - 1, 0, message[:width-1], curses.color_pair(color_pair))
        self.stdscr.refresh()
        
    def get_input(self, prompt):
        """Get user input"""
        height, width = self.stdscr.getmaxyx()
        curses.echo()
        curses.curs_set(1)
        self.stdscr.addstr(height - 1, 0, " " * (width - 1))
        self.stdscr.addstr(height - 1, 0, prompt)
        self.stdscr.refresh()
        
        try:
            user_input = self.stdscr.getstr(height - 1, len(prompt)).decode('utf-8')
        except:
            user_input = ""
            
        curses.noecho()
        curses.curs_set(0)
        return user_input
        
    def open_file(self, filename=None):
        """Open an HDF5 file"""
        if filename is None:
            filename = self.get_input("Enter HDF5 file path: ")
        
        if not filename:
            return False
            
        try:
            # Expand user path and resolve relative paths
            filename = os.path.expanduser(filename)
            filename = os.path.abspath(filename)
            
            if not os.path.exists(filename):
                self.show_message(f"File not found: {filename}", 4)
                return False
                
            if self.current_file:
                self.current_file.close()
                
            self.current_file = h5py.File(filename, 'r')
            self.current_path = "/"
            self.load_current_directory()
            self.show_message(f"Opened: {filename}", 5)
            return True
        except Exception as e:
            self.show_message(f"Error opening file: {str(e)}", 4)
            return False
            
    def load_current_directory(self):
        """Load items from current directory in HDF5 file"""
        if not self.current_file:
            self.items = []
            return
            
        try:
            if self.current_path == "/":
                current_group = self.current_file
            else:
                current_group = self.current_file[self.current_path]
                
            self.items = []
            
            # Add parent directory option if not at root
            if self.current_path != "/":
                self.items.append(("../", "parent", None))
                
            # Add groups and datasets
            for key in current_group.keys():
                item = current_group[key]
                if isinstance(item, h5py.Group):
                    self.items.append((key + "/", "group", item))
                elif isinstance(item, h5py.Dataset):
                    shape_str = f"Shape: {item.shape}, Type: {item.dtype}"
                    self.items.append((key, "dataset", item, shape_str))
                    
            self.selected_index = 0
            self.scroll_offset = 0
            
        except Exception as e:
            self.show_message(f"Error loading directory: {str(e)}", 4)
            
    def navigate_to_item(self):
        """Navigate to selected item"""
        if not self.items:
            return
            
        item = self.items[self.selected_index]
        name, item_type = item[0], item[1]
        
        if item_type == "parent":
            # Go to parent directory
            if self.current_path != "/":
                self.current_path = "/".join(self.current_path.rstrip("/").split("/")[:-1])
                if not self.current_path:
                    self.current_path = "/"
                self.load_current_directory()
        elif item_type == "group":
            # Enter group
            if self.current_path == "/":
                self.current_path = "/" + name.rstrip("/")
            else:
                self.current_path = self.current_path.rstrip("/") + "/" + name.rstrip("/")
            self.load_current_directory()
            
    def export_group_to_hdf5(self):
        """Export selected group to separate HDF5 file"""
        if not self.items or self.selected_index >= len(self.items):
            # If no items or invalid selection, check if we're in a group
            if self.current_path != "/":
                # We're inside a group, use current group
                group_name = self.current_path.split("/")[-1]
                output_file = self.get_input(f"Export current group '{group_name}' to file: ")
                if not output_file:
                    return
                    
                try:
                    # Expand user path and resolve relative paths
                    output_file = os.path.expanduser(output_file)
                    output_file = os.path.abspath(output_file)
                    
                    # Ensure .h5 extension
                    if not output_file.endswith('.h5') and not output_file.endswith('.hdf5'):
                        output_file += '.h5'
                        
                    source_group = self.current_file[self.current_path]
                    
                    with h5py.File(output_file, 'w') as out_file:
                        self.copy_group(source_group, out_file)
                        
                    self.show_message(f"Successfully exported to: {output_file}", 5)
                    
                except Exception as e:
                    self.show_message(f"Export failed: {str(e)}", 4)
            else:
                self.show_message("No group selected and not inside a group", 4)
            return
            
        item = self.items[self.selected_index]
        name, item_type = item[0], item[1]
        
        if item_type != "group":
            # If not a group but we're inside a group, use current group
            if self.current_path != "/":
                group_name = self.current_path.split("/")[-1]
                output_file = self.get_input(f"Export current group '{group_name}' to file: ")
                if not output_file:
                    return
                    
                try:
                    # Expand user path and resolve relative paths
                    output_file = os.path.expanduser(output_file)
                    output_file = os.path.abspath(output_file)
                    
                    # Ensure .h5 extension
                    if not output_file.endswith('.h5') and not output_file.endswith('.hdf5'):
                        output_file += '.h5'
                        
                    source_group = self.current_file[self.current_path]
                    
                    with h5py.File(output_file, 'w') as out_file:
                        self.copy_group(source_group, out_file)
                        
                    self.show_message(f"Successfully exported to: {output_file}", 5)
                    
                except Exception as e:
                    self.show_message(f"Export failed: {str(e)}", 4)
            else:
                self.show_message("Please select a group to export or navigate inside a group", 4)
            return
            
        output_file = self.get_input(f"Export '{name}' to file: ")
        if not output_file:
            return
            
        try:
            # Expand user path and resolve relative paths
            output_file = os.path.expanduser(output_file)
            output_file = os.path.abspath(output_file)
            
            # Ensure .h5 extension
            if not output_file.endswith('.h5') and not output_file.endswith('.hdf5'):
                output_file += '.h5'
                
            group_path = self.current_path.rstrip("/") + "/" + name.rstrip("/")
            if self.current_path == "/":
                group_path = "/" + name.rstrip("/")
                
            source_group = self.current_file[group_path]
            
            with h5py.File(output_file, 'w') as out_file:
                self.copy_group(source_group, out_file)
                
            self.show_message(f"Successfully exported to: {output_file}", 5)
            
        except Exception as e:
            self.show_message(f"Export failed: {str(e)}", 4)
            
    def copy_group(self, source, dest):
        """Recursively copy group contents"""
        for key in source.keys():
            source.copy(key, dest)
            
    def export_dataset_to_csv(self):
        """Export selected dataset to CSV file"""
        if not self.items or self.selected_index >= len(self.items):
            return
            
        item = self.items[self.selected_index]
        name, item_type = item[0], item[1]
        
        if item_type != "dataset":
            self.show_message("Please select a dataset to export", 4)
            return
            
        output_file = self.get_input(f"Export '{name}' to CSV file: ")
        if not output_file:
            return
            
        try:
            # Expand user path and resolve relative paths
            output_file = os.path.expanduser(output_file)
            output_file = os.path.abspath(output_file)
            
            # Ensure .csv extension
            if not output_file.endswith('.csv'):
                output_file += '.csv'
                
            dataset_path = self.current_path.rstrip("/") + "/" + name
            if self.current_path == "/":
                dataset_path = "/" + name
                
            dataset = self.current_file[dataset_path]
            data = dataset[:]
            
            # Convert to pandas DataFrame
            if len(data.shape) == 1:
                df = pd.DataFrame(data, columns=[name])
            elif len(data.shape) == 2:
                df = pd.DataFrame(data)
            else:
                # For higher dimensions, flatten or handle appropriately
                df = pd.DataFrame(data.reshape(-1, data.shape[-1]))
                
            df.to_csv(output_file, index=False)
            self.show_message(f"Successfully exported to: {output_file}", 5)
            
        except Exception as e:
            self.show_message(f"CSV export failed: {str(e)}", 4)
            
    def show_dataset_info(self):
        """Show detailed information about selected dataset"""
        if not self.items or self.selected_index >= len(self.items):
            return
            
        item = self.items[self.selected_index]
        name, item_type = item[0], item[1]
        
        if item_type != "dataset":
            self.show_message("Please select a dataset to view info", 4)
            return
            
        try:
            dataset_path = self.current_path.rstrip("/") + "/" + name
            if self.current_path == "/":
                dataset_path = "/" + name
                
            dataset = self.current_file[dataset_path]
            
            # Create info window
            height, width = self.stdscr.getmaxyx()
            info_height = min(15, height - 4)
            info_width = min(60, width - 4)
            info_y = (height - info_height) // 2
            info_x = (width - info_width) // 2
            
            info_win = curses.newwin(info_height, info_width, info_y, info_x)
            info_win.box()
            info_win.addstr(1, 2, f"Dataset: {name}")
            info_win.addstr(2, 2, f"Shape: {dataset.shape}")
            info_win.addstr(3, 2, f"Type: {dataset.dtype}")
            info_win.addstr(4, 2, f"Size: {dataset.size}")
            
            # Show attributes if any
            if dataset.attrs:
                info_win.addstr(6, 2, "Attributes:")
                row = 7
                for attr_name, attr_value in dataset.attrs.items():
                    if row < info_height - 2:
                        info_win.addstr(row, 4, f"{attr_name}: {attr_value}")
                        row += 1
                        
            info_win.addstr(info_height - 2, 2, "Press any key to close")
            info_win.refresh()
            info_win.getch()
            
        except Exception as e:
            self.show_message(f"Info error: {str(e)}", 4)
            
    def draw_screen(self):
        """Draw the main screen"""
        self.stdscr.clear()
        height, width = self.stdscr.getmaxyx()
        
        # Title
        title = "HDF5 File Manager"
        self.stdscr.addstr(0, (width - len(title)) // 2, title, curses.A_BOLD)
        
        # Current file and path
        if self.current_file:
            file_info = f"File: {self.current_file.filename} | Path: {self.current_path}"
            self.stdscr.addstr(1, 0, file_info[:width-1])
        else:
            self.stdscr.addstr(1, 0, "No file opened - Press 'o' to open a file")
            
        # Separator
        self.stdscr.addstr(2, 0, "-" * (width - 1))
        
        # Items list
        display_height = height - 6
        start_row = 3
        
        for i, item in enumerate(self.items[self.scroll_offset:self.scroll_offset + display_height]):
            row = start_row + i
            name, item_type = item[0], item[1]
            
            # Determine color and prefix
            if item_type == "parent":
                color = curses.color_pair(2)
                prefix = "📁 "
            elif item_type == "group":
                color = curses.color_pair(2)
                prefix = "📁 "
            elif item_type == "dataset":
                color = curses.color_pair(3)
                prefix = "📄 "
                if len(item) > 3:  # Has shape info
                    name = f"{name} ({item[3]})"
            else:
                color = 0
                prefix = "   "
                
            # Highlight selected item (override other colors)
            actual_index = i + self.scroll_offset
            if actual_index == self.selected_index:
                color = curses.color_pair(1)  # Selected color overrides item type color
                
            display_text = f"{prefix}{name}"
            self.stdscr.addstr(row, 0, display_text[:width-1], color)
            
        # Help text
        help_text = "o:Open | ↑↓/jk:Navigate | ←→/hl:Parent/Enter | g:Top | G:Bottom | e:Export HDF5 | c:Export CSV | i:Info | q:Quit"
        self.stdscr.addstr(height - 2, 0, help_text[:width-1], curses.color_pair(5))
        
        self.stdscr.refresh()
        
    def handle_scroll(self):
        """Handle scrolling logic"""
        height, width = self.stdscr.getmaxyx()
        display_height = height - 6
        
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + display_height:
            self.scroll_offset = self.selected_index - display_height + 1
            
    def run(self):
        """Main application loop"""
        while True:
            self.draw_screen()
            
            try:
                key = self.stdscr.getch()
                
                if key == ord('q') or key == ord('Q'):
                    break
                elif key == ord('o') or key == ord('O'):
                    self.open_file()
                elif (key == curses.KEY_UP or key == ord('k') or key == ord('K')) and self.selected_index > 0:
                    self.selected_index -= 1
                    self.handle_scroll()
                elif (key == curses.KEY_DOWN or key == ord('j') or key == ord('J')) and self.selected_index < len(self.items) - 1:
                    self.selected_index += 1
                    self.handle_scroll()
                elif key == ord('h') or key == ord('H'):
                    # Go to parent directory (vim-style left)
                    if self.current_path != "/":
                        self.current_path = "/".join(self.current_path.rstrip("/").split("/")[:-1])
                        if not self.current_path:
                            self.current_path = "/"
                        self.load_current_directory()
                elif key == ord('l') or key == ord('L') or key == ord('\n') or key == curses.KEY_ENTER or key == 10:
                    # Enter directory/group (vim-style right) or regular enter
                    self.navigate_to_item()
                elif key == ord('g'):
                    # Go to top (vim-style gg, but single g for simplicity)
                    self.selected_index = 0
                    self.handle_scroll()
                elif key == ord('G'):
                    # Go to bottom (vim-style G)
                    if self.items:
                        self.selected_index = len(self.items) - 1
                        self.handle_scroll()
                elif key == ord('e') or key == ord('E'):
                    self.export_group_to_hdf5()
                elif key == ord('c') or key == ord('C'):
                    self.export_dataset_to_csv()
                elif key == ord('i') or key == ord('I'):
                    self.show_dataset_info()
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.show_message(f"Error: {str(e)}", 4)
                
        # Cleanup
        if self.current_file:
            self.current_file.close()


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='HDF5 File Manager - Interactive ncurses interface for browsing and manipulating HDF5 files',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                          # Start with no file loaded
  %(prog)s data.h5                  # Open data.h5 on startup
  %(prog)s /path/to/file.hdf5       # Open file with full path
  %(prog)s --file experiment.h5     # Alternative syntax

Controls:
  o           Open HDF5 file
  ↑/↓         Navigate up/down
  Enter       Enter group or navigate to parent
  e           Export selected group to HDF5 file
  c           Export selected dataset to CSV
  i           Show detailed dataset information
  q           Quit application

File Operations:
  - Export groups: Select a group and press 'e' to export to separate HDF5 file
  - Export datasets: Select a dataset and press 'c' to convert to CSV
  - View info: Select a dataset and press 'i' to see detailed information
        """
    )
    
    parser.add_argument(
        'file',
        nargs='?',
        help='HDF5 file to open on startup'
    )
    
    parser.add_argument(
        '-f', '--file',
        dest='file_alt',
        help='HDF5 file to open on startup (alternative syntax)'
    )
    
    parser.add_argument(
        '-v', '--version',
        action='version',
        version='HDF5 File Manager 1.0'
    )
    
    parser.add_argument(
        '--check-deps',
        action='store_true',
        help='Check if all required dependencies are installed'
    )
    
    return parser.parse_args()


def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import h5py
        print(f"✓ h5py {h5py.__version__}")
    except ImportError:
        missing_deps.append('h5py')
        print("✗ h5py - not installed")
    
    try:
        import pandas as pd
        print(f"✓ pandas {pd.__version__}")
    except ImportError:
        missing_deps.append('pandas')
        print("✗ pandas - not installed")
    
    try:
        import numpy as np
        print(f"✓ numpy {np.__version__}")
    except ImportError:
        missing_deps.append('numpy')
        print("✗ numpy - not installed")
    
    try:
        import curses
        print("✓ curses - available")
    except ImportError:
        missing_deps.append('curses')
        print("✗ curses - not available (Windows?)")
    
    if missing_deps:
        print(f"\nMissing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install " + " ".join(missing_deps))
        return False
    else:
        print("\n✓ All dependencies are available!")
        return True


def validate_hdf5_file(filename):
    """Validate that the file exists and is a valid HDF5 file"""
    if not filename:
        return True, None  # No file specified is OK
    
    # Expand user path and resolve relative paths
    filename = os.path.expanduser(filename)
    filename = os.path.abspath(filename)
    
    if not os.path.exists(filename):
        return False, f"File not found: {filename}"
    
    if not os.path.isfile(filename):
        return False, f"Path is not a file: {filename}"
    
    try:
        with h5py.File(filename, 'r') as f:
            # Try to read the file to ensure it's valid HDF5
            list(f.keys())
        return True, filename
    except Exception as e:
        return False, f"Invalid HDF5 file: {str(e)}"


def main(stdscr, filename=None):
    """Main function to run the HDF5 manager"""
    try:
        manager = HDF5Manager(stdscr)
        
        # If filename provided, try to open it
        if filename:
            success = manager.open_file(filename)
            if not success:
                # Show error message and wait for user input
                manager.show_message("Press any key to continue without file...", 4)
                stdscr.getch()
        
        manager.run()
    except Exception as e:
        # In case of any unhandled exception, show error and exit gracefully
        stdscr.clear()
        stdscr.addstr(0, 0, f"Fatal error: {str(e)}")
        stdscr.addstr(1, 0, "Press any key to exit...")
        stdscr.refresh()
        stdscr.getch()


if __name__ == "__main__":
    # Parse command line arguments
    args = parse_arguments()
    
    # Handle dependency check
    if args.check_deps:
        check_dependencies()
        sys.exit(0)
    
    # Check if required modules are available
    try:
        import h5py
        import pandas as pd
        import numpy as np
        import curses
    except ImportError as e:
        print(f"Missing required module: {e}")
        print("Please install required packages:")
        print("pip install h5py pandas numpy")
        print("\nOr run with --check-deps to see detailed dependency status")
        sys.exit(1)
    
    # Determine which file to open
    filename = args.file or args.file_alt
    
    # Validate the file if provided
    if filename:
        is_valid, result = validate_hdf5_file(filename)
        if not is_valid:
            print(f"Error: {result}")
            sys.exit(1)
        filename = result
    
    # Create wrapper function with filename
    def main_wrapper(stdscr):
        main(stdscr, filename)
    
    # Run the application
    try:
        curses.wrapper(main_wrapper)
    except KeyboardInterrupt:
        print("\nApplication interrupted by user")
    except Exception as e:
        print(f"Application error: {str(e)}")
        sys.exit(1)