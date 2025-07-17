#ifndef CVALNUM_H
#define CVALNUM_H

#include <memory>
#include "CExpr.h"

/**
 * @class CValNum
 * @brief Numeric literal value expression
 * 
 * Represents a constant numeric value (e.g., a number like 42 or 3.14) in an expression tree.
 */
class CValNum : public CExpr
{
  public:
    /**
     * Constructor
     * @param[in] val Numeric value
     */
    explicit CValNum(double val);

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
     * Stored numeric value
     */
    double m_Val;
};

#endif // CVALNUM_H
