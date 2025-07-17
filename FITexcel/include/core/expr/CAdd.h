#ifndef CADD_H
#define CADD_H

#include <memory>
#include "CExpr.h"

/**
 * @class CAdd
 * @brief Binary operator class for addition (+)
 *
 * Represents an expression node that computes the sum of two sub-expressions.
 */
class CAdd : public CExpr
{
  public:
    /**
     * Constructor
     * @param[in] first   Left operand
     * @param[in] second  Right operand
     */
    CAdd(std::shared_ptr<CExpr> first, std::shared_ptr<CExpr> second);

    /// \copydoc CExpr::getValue
    CValue getValue(const std::unordered_map<CPos, CBuilder, CPosHash>& map,
                    std::unordered_map<CPos, bool, CPosHash>& cyc, int colMove, int rowMove) const override;

    /// \copydoc CExpr::clone
    std::shared_ptr<CExpr> clone() const override;

  private:
    /**
     * Left operand of the addition
     */
    std::shared_ptr<CExpr> m_FirstOp;

    /**
     * Right operand of the addition
     */
    std::shared_ptr<CExpr> m_SecondOp;
};

#endif // CADD_H
