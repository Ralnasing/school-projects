#ifndef CNE_H
#define CNE_H

#include <memory>
#include "CExpr.h"

/**
 * @class CNe
 * @brief Binary comparison operator for "not equal" (!=)
 * 
 * Represents an expression node that compares two sub-expressions for inequality.
 */
class CNe : public CExpr
{
  public:
    /**
     * Constructor
     * @param[in] first   Left operand
     * @param[in] second  Right operand
     */
    CNe(std::shared_ptr<CExpr> first, std::shared_ptr<CExpr> second);

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
     * Left operand of the inequality comparison
     */
    std::shared_ptr<CExpr> m_FirstOp;

    /**
     * Right operand of the inequality comparison
     */
    std::shared_ptr<CExpr> m_SecondOp;
};

#endif // CNE_H
