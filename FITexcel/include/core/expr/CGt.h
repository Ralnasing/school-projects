#ifndef CGT_H
#define CGT_H

#include <memory>
#include "CExpr.h"

/**
 * @class CGt
 * @brief Binary comparison operator for "greater than" (>)
 * 
 * Represents an expression node that checks whether the first operand is greater than the second.
 */
class CGt : public CExpr
{
  public:
    /**
     * Constructor
     * @param[in] first   Left operand
     * @param[in] second  Right operand
     */
    CGt(std::shared_ptr<CExpr> first, std::shared_ptr<CExpr> second);

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

#endif // CGT_H
