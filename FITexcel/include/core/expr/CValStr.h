#ifndef CVALSTR_H
#define CVALSTR_H

#include <memory>
#include <string>
#include "CExpr.h"

/**
 * @class CValStr
 * @brief String literal value expression
 * 
 * Represents a constant string value in the expression tree.
 */
class CValStr : public CExpr
{
  public:
    /**
     * Constructor
     * @param[in] val String value
     */
    explicit CValStr(const std::string& val);

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
     * Stored string value
     */
    std::string m_Val;
};

#endif // CVALSTR_H
