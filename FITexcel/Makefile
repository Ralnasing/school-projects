# Compiler and flags
CXX = g++
CXXFLAGS = -std=c++17 -pedantic -Wall -Wextra -Iinclude

# Directories
SRC_DIR = src
BUILD_DIR = build
BIN_DIR = bin
TEST_DIR = tests
PARSER_LIB = parser/libexpression_parser.a

# Create necessary folders
$(shell mkdir -p $(BUILD_DIR)/expr $(BIN_DIR))

# Source files
SRC_FILES = $(wildcard $(SRC_DIR)/*.cpp) $(wildcard $(SRC_DIR)/expr/*.cpp)
OBJ_FILES = $(patsubst $(SRC_DIR)/%.cpp,$(BUILD_DIR)/%.o,$(SRC_FILES))
OBJ_FILES := $(patsubst $(SRC_DIR)/expr/%.cpp,$(BUILD_DIR)/expr/%.o,$(OBJ_FILES))

# Test files
TEST_SRC = $(TEST_DIR)/test_main.cpp
TEST_OBJ = $(BUILD_DIR)/test_main.o
TEST_BIN = $(BIN_DIR)/test_exec

# Final executables
APP_BIN = $(BIN_DIR)/spreadsheet

# Default target
all: $(APP_BIN)

# Main app target
$(APP_BIN): $(OBJ_FILES)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(PARSER_LIB)

# Compile source files
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

$(BUILD_DIR)/expr/%.o: $(SRC_DIR)/expr/%.cpp
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Test target
test: $(TEST_BIN)
	./$(TEST_BIN)

$(TEST_BIN): $(filter-out $(BUILD_DIR)/main.o,$(OBJ_FILES)) $(TEST_OBJ)
	$(CXX) $(CXXFLAGS) -o $@ $^ $(PARSER_LIB)

$(TEST_OBJ): $(TEST_SRC)
	$(CXX) $(CXXFLAGS) -c $< -o $@

# Clean build
clean:
	rm -rf $(BUILD_DIR) $(BIN_DIR)
