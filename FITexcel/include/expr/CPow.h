#ifndef CPOW_H
#define CPOW_H

#include <memory>
#include "CExpr.h"

/**
 * @class CPow
 * @brief Binary operator for exponentiation (^)
 * 
 * Represents an expression node that raises the left operand to the power of the right operand.
 */
class CPow : public CExpr
{
  public:
    /**
     * Constructor
     * @param[in] first   Left operand (base)
     * @param[in] second  Right operand (exponent)
     */
    CPow(std::shared_ptr<CExpr> first, std::shared_ptr<CExpr> second);

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
     * Left operand (base)
     */
    std::shared_ptr<CExpr> m_FirstOp;

    /**
     * Right operand (exponent)
     */
    std::shared_ptr<CExpr> m_SecondOp;
};

#endif // CPOW_H
