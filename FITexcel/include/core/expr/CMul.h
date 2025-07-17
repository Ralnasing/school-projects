#ifndef CMUL_H
#define CMUL_H

#include <memory>
#include "CExpr.h"

/**
 * @class CMul
 * @brief Binary operator for multiplication (*)
 * 
 * Represents an expression node that multiplies the results of two sub-expressions.
 */
class CMul : public CExpr
{
  public:
    /**
     * Constructor
     * @param[in] first   Left operand
     * @param[in] second  Right operand
     */
    CMul(std::shared_ptr<CExpr> first, std::shared_ptr<CExpr> second);

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
     * Left operand of the multiplication
     */
    std::shared_ptr<CExpr> m_FirstOp;

    /**
     * Right operand of the multiplication
     */
    std::shared_ptr<CExpr> m_SecondOp;
};

#endif // CMUL_H
