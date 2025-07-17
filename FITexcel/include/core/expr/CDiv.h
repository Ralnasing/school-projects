#ifndef CDIV_H
#define CDIV_H

#include <memory>
#include "CExpr.h"

/**
 * @class CDiv
 * @brief Binary operator class for division (/)
 * 
 * Represents an expression node that computes the quotient of two sub-expressions.
 */
class CDiv : public CExpr
{
  public:
    /**
     * Constructor
     * @param[in] first   Left operand
     * @param[in] second  Right operand
     */
    CDiv(std::shared_ptr<CExpr> first, std::shared_ptr<CExpr> second);

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
     * Left operand of the division
     */
    std::shared_ptr<CExpr> m_FirstOp;

    /**
     * Right operand of the division
     */
    std::shared_ptr<CExpr> m_SecondOp;
};

#endif // CDIV_H
