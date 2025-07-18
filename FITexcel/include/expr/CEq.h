#ifndef CEQ_H
#define CEQ_H

#include <memory>
#include "CExpr.h"

/**
 * @class CEq
 * @brief Binary comparison operator for equality (=)
 * 
 * Represents an expression node that compares two sub-expressions for equality.
 */
class CEq : public CExpr
{
  public:
    /**
     * Constructor
     * @param[in] first   Left operand
     * @param[in] second  Right operand
     */
    CEq(std::shared_ptr<CExpr> first, std::shared_ptr<CExpr> second);

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
     * Left operand of the equality comparison
     */
    std::shared_ptr<CExpr> m_FirstOp;

    /**
     * Right operand of the equality comparison
     */
    std::shared_ptr<CExpr> m_SecondOp;
};

#endif // CEQ_H
