#ifndef CVALREF_H
#define CVALREF_H

#include <memory>
#include <string>
#include "CExpr.h"

/**
 * @class CValRef
 * @brief Expression node representing a reference to a single cell
 * 
 * Stores the identifier of the referenced cell and information about absolute/relative addressing.
 */
class CValRef : public CExpr
{
  public:
    /**
     * Constructor
     * @param[in] cell    Cell identifier (e.g., "A1", "$B$2")
     * @param[in] absCol  Whether the column is absolute
     * @param[in] absRow  Whether the row is absolute
     */
    CValRef(const std::string& cell, bool absCol, bool absRow);

    /// \copydoc CExpr::getValue
    CValue getValue(
        const std::unordered_map<CPos, CBuilder, CPosHash>& map,
              std::unordered_map<CPos, bool, CPosHash>&     cyc,
        int                                                 colMove,
        int                                                 rowMove) const override;

    /// \copydoc CExpr::clone
    std::shared_ptr<CExpr> clone() const override;

  private:
    /**
     * Raw cell identifier (as parsed, e.g., "B7", "$C$4")
     */
    std::string m_Cell;

    /**
     * Whether the column part is absolute (prefixed with '$')
     */
    bool m_AbsCol;

    /**
     * Whether the row part is absolute (prefixed with '$')
     */
    bool m_AbsRow;
};

#endif // CVALREF_H
