#ifndef CGE_H
#define CGE_H

#include <memory>
#include "CExpr.h"

/**
 * @class CGe
 * @brief Binary comparison operator for "greater than or equal to" (>=)
 * 
 * Represents an expression node that compares whether the first operand is greater than or equal to the second.
 */
class CGe : public CExpr
{
  public:
    /**
     * Constructor
     * @param[in] first   Left operand
     * @param[in] second  Right operand
     */
    CGe(std::shared_ptr<CExpr> first, std::shared_ptr<CExpr> second);

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
     * Left operand of the comparison
     */
    std::shared_ptr<CExpr> m_FirstOp;

    /**
     * Right operand of the comparison
     */
    std::shared_ptr<CExpr> m_SecondOp;
};

#endif // CGE_H
