#ifndef CPOS_H
#define CPOS_H

#include <string>
#include <string_view>
#include <utility>
#include <cstdint>

/**
 * Number of letters in the English alphabet 
 * for stringToIndex method implementation
 */
constexpr int ENG_ALPH_SIZE = 26;

/**
 * @class CPos
 * Represents a cell identifier in a table (e.g., spreadsheet-style).
 * Provides methods for parsing, comparing, and transforming cell positions.
 */
class CPos
{
  public:
    /**
     * Default constructor
     */
    CPos();

    /**
     * Constructs a cell position from a string like "A1"
     * @param str input string representing the cell position
     */
    CPos(std::string_view str);

    /**
     * Returns the numeric column index
     * @return column index (0-based)
     */
    size_t colIndex() const;

    /**
     * Returns the numeric row index
     * @return row index (0-based)
     */
    size_t rowIndex() const;

    /**
     * Returns the cell name as a string (e.g., "B3")
     * @return cell name
     */
    std::string cellName() const;

    /**
     * Equality operator
     * @param pos object to compare with
     * @return true if the positions are equal, false otherwise
     */
    bool operator==(const CPos& pos) const;

    /**
     * Less-than operator (for sorting or ordering)
     * @param pos object to compare with
     * @return true if this position is before the other
     */
    bool operator<(const CPos& pos) const;

    /**
     * Adds a vector offset to the current cell position
     * @param pos base position
     * @param vec vector offset (columns, rows)
     * @return new position with applied offset
     */
    friend CPos operator+(const CPos& pos, const std::pair<int, int>& vec);

  private:
    /**
     * Cell identifier string (e.g., "A1", "D42")
     */
    mutable std::string m_Cell;

    /**
     * Column as a string and numeric index
     * e.g., {"A", 0}, {"AA", 26}
     */
    std::pair<std::string, int> m_Col;

    /**
     * Row number (0-based)
     */
    int m_Row;

    /**
     * Splits the cell string into column and row parts
     * @param str input string (e.g., "C10")
     * @return pair of column string and row number
     */
    std::pair<std::string, int> divide(const std::string& str) const;

    /**
     * Converts a column label (e.g., "AB") to its numeric index
     * @param str column label
     * @return 0-based column index
     */
    int stringToIndex(const std::string& str) const;

    /**
     * Converts a column index to its letter representation
     * @param index 0-based column index
     * @return column string (e.g., "AB")
     */
    std::string indexToString(int index) const;
};

/**
 * Hash functor for storing CPos objects in unordered containers.
 * Inspired by XLNT library implementation:
 * https://github.com/tfussell/xlnt/blob/master/include/xlnt/cell/cell_reference.hpp
 */
struct CPosHash
{
    size_t operator()(const CPos& pos) const
    {
        return std::hash<uint64_t>{}(pos.rowIndex() | (static_cast<uint64_t>(pos.colIndex()) << 32));
    }
};

#endif // CPOS_H
