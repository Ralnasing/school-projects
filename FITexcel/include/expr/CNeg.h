#ifndef CNEG_H
#define CNEG_H

#include <memory>
#include "CExpr.h"

/**
 * @class CNeg
 * @brief Unary operator for negation (-)
 * 
 * Represents an expression node that negates the result of its operand.
 */
class CNeg : public CExpr
{
  public:
    /**
     * Constructor
     * @param[in] operand Operand to negate
     */
    explicit CNeg(std::shared_ptr<CExpr> operand);

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
     * Operand of the negation
     */
    std::shared_ptr<CExpr> m_Op;
};

#endif // CNEG_H
