#include "core/expr/CDiv.h"
#include <variant>

// ======================== ======================== ======================== ========================
// Constructors
// ========================

CDiv::CDiv(std::shared_ptr<CExpr> first, std::shared_ptr<CExpr> second)
: m_FirstOp(std::move(first)), m_SecondOp(std::move(second))
{
}

// ======================== ======================== ======================== ========================
// Evaluation
// ========================

CValue CDiv::getValue(const std::unordered_map<CPos, CBuilder, CPosHash>& map,
                            std::unordered_map<CPos, bool, CPosHash>&     cyc,
                      int                                                 colMove,
                      int                                                 rowMove) const
{
    CValue first  = m_FirstOp->getValue(map, cyc, colMove, rowMove);
    CValue second = m_SecondOp->getValue(map, cyc, colMove, rowMove);

    if (!std::holds_alternative<double>(first) || !std::holds_alternative<double>(second))
        return CValue();

    double divisor = std::get<double>(second);
    if (divisor == 0.0)
        return CValue(); // division by zero → invalid

    return std::get<double>(first) / divisor;
}

// ======================== ======================== ======================== ========================
// Cloning
// ========================

std::shared_ptr<CExpr> CDiv::clone() const
{
    return std::make_shared<CDiv>(*this);
}
