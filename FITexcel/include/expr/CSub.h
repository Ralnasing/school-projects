#ifndef CSUB_H
#define CSUB_H

#include <memory>
#include "CExpr.h"

/**
 * @class CSub
 * @brief Binary operator for subtraction (-)
 * 
 * Represents an expression node that subtracts the right operand from the left operand.
 */
class CSub : public CExpr
{
  public:
    /**
     * Constructor
     * @param[in] first   Left operand
     * @param[in] second  Right operand
     */
    CSub(std::shared_ptr<CExpr> first, std::shared_ptr<CExpr> second);

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
     * Left operand of the subtraction
     */
    std::shared_ptr<CExpr> m_FirstOp;

    /**
     * Right operand of the subtraction
     */
    std::shared_ptr<CExpr> m_SecondOp;
};

#endif // CSUB_H
