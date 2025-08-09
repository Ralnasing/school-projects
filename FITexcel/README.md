# C++ Spreadsheet

A simple spreadsheet implementation in C++ as a school project.

## Features

- **Cell Management**: Store and manipulate cell content with automatic type detection
- **Formula Evaluation**: Support for arithmetic operations (+, -, *, /, ^) and comparison operators (=, <>, <, <=, >, >=)
- **Cell References**: Both absolute (`$A$1`) and relative (`A1`) cell references
- **Range Support**: Handle cell ranges for advanced operations
- **Function Calls**: Extensible function system for built-in spreadsheet functions
- **CSV Save/Load**: Load and save spreadsheets in CSV format
- **Copy Operations**: Copy rectangular areas of cells with automatic reference adjustment
- **Cycle Detection**: Prevents infinite loops in circular references

## Project Structure

```
├── include/           # Header files
│   ├── CSpreadsheet.h
│   ├── CBuilder.h
│   ├── CExprBuilder.h
│   ├── CPos.h
│   ├── CValue.h
│   └── expr/          # Expression-related headers
├── src/               # Source files
│   ├── CSpreadsheet.cpp
│   ├── CBuilder.cpp
│   ├── CPos.cpp
│   ├── expr/          # Expression implementations
│   └── main.cpp
├── tests/             # Unit tests
│   ├── test_*.cpp
│   └── doctest.h
├── parser/            # Expression parser library
│   └── libexpression_parser.a
├── build/             # Compiled object files (Created with "make")
├── bin/               # Executable files (Created with "make")
└── Makefile
```

## Building the Project

### Prerequisites

- C++17 compatible compiler (GCC, Clang, or MSVC)
- Make build system

### Compilation

```bash
# Build the entire project
make

# Build and run tests
make test

# Clean build artifacts
make clean
```

The project uses a static library (`libexpression_parser.a`) for expression parsing functionality.

## Usage Example

```cpp
#include "CSpreadsheet.h"
#include <iostream>
#include <sstream>

int main() {
    CSpreadsheet sheet;
    
    // Set cell values
    sheet.setCell(CPos("A1"), "10");
    sheet.setCell(CPos("A2"), "20");
    sheet.setCell(CPos("A3"), "=A1+A2");
    
    // Get evaluated values
    CValue result = sheet.getValue(CPos("A3"));
    // result contains 30.0
    
    // Copy operations
    sheet.copyRect(CPos("B1"), CPos("A1"), 1, 3);
    
    // Save to CSV
    std::ostringstream oss;
    sheet.save(oss);
    
    return 0;
}
```

## Testing

The project includes comprehensive unit tests using the doctest framework:

```bash
# Individual test modules
- test_cpos.cpp      # Position handling tests
- test_cbuilder.cpp  # Expression builder tests  
- test_cspreadsheet.cpp # Spreadsheet functionality tests
- test_expr.cpp      # Expression evaluation tests
```
