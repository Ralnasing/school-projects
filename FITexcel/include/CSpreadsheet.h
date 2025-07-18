#ifndef CSPREADSHEET_H
#define CSPREADSHEET_H

#include <unordered_map>
#include <string>
#include <iostream>
#include "CPos.h"
#include "CBuilder.h"

/**
 * @class CSpreadsheet
 * @brief Main class representing a spreadsheet
 * 
 * Manages storage, evaluation, and manipulation of cell content.
 */
class CSpreadsheet
{
  public:
    /**
     * Returns bit flags indicating supported features for testing
     * @return Flags for testing capabilities
     */
    static unsigned capabilities();

    /**
     * Default constructor – creates an empty spreadsheet
     */
    CSpreadsheet();

    /**
     * Copy constructor
     * @param[in] src Spreadsheet to copy
     */
    CSpreadsheet(const CSpreadsheet& src);

    /**
     * Assignment operator
     * @param[in] src Spreadsheet to copy
     * @return Reference to this object
     */
    CSpreadsheet& operator=(const CSpreadsheet& src);

    /**
     * Loads the spreadsheet from an input stream
     * @param[in] is Input stream
     * @return true if loaded successfully, false otherwise
     */
    bool load(std::istream& is);

    /**
     * Saves the spreadsheet to an output stream
     * @param[in] os Output stream
     * @return true if saved successfully, false otherwise
     */
    bool save(std::ostream& os) const;

    /**
     * Sets the content of a cell
     * @param[in] pos      Position of the cell
     * @param[in] contents Content string to assign
     * @return true on success, false on parse/eval error
     */
    bool setCell(CPos pos, std::string contents);

    /**
     * Evaluates the value of a cell
     * @param[in] pos Position of the cell
     * @return Evaluated value, or empty CValue() if evaluation fails
     */
    CValue getValue(CPos pos);

    /**
     * Copies a rectangular area of cells to a new location
     * @param[in] dst Destination (top-left corner)
     * @param[in] src Source (top-left corner)
     * @param[in] w   Width in cells (columns), default 1
     * @param[in] h   Height in cells (rows), default 1
     */
    void copyRect(CPos dst, CPos src, int w = 1, int h = 1);

  private:
    /**
     * Internal storage of cell builders mapped by position
     */
    std::unordered_map<CPos, CBuilder, CPosHash> m_Sheet;
};

#endif // CSPREADSHEET_H
