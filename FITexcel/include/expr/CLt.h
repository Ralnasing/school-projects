#ifndef CLT_H
#define CLT_H

#include <memory>
#include "CExpr.h"

/**
 * @class CLt
 * @brief Binary comparison operator for "less than" (<)
 * 
 * Represents an expression node that checks whether the first operand is less than the second.
 */
class CLt : public CExpr
{
  public:
    /**
     * Constructor
     * @param[in] first   Left operand
     * @param[in] second  Right operand
     */
    CLt(std::shared_ptr<CExpr> first, std::shared_ptr<CExpr> second);

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

#endif // CLT_H
