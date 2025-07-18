#include "core/expr/CPow.h"
#include <cmath>
#include <variant>

// ======================== ======================== ======================== ========================
// Constructors
// ========================

CPow::CPow(std::shared_ptr<CExpr> first, std::shared_ptr<CExpr> second)
: m_FirstOp(std::move(first)), m_SecondOp(std::move(second))
{
}

// ======================== ======================== ======================== ========================
// Evaluation
// ========================

CValue CPow::getValue(const std::unordered_map<CPos, CBuilder, CPosHash>& map,
                            std::unordered_map<CPos, bool, CPosHash>&     cyc,
                      int                                                 colMove,
                      int                                                 rowMove) const
{
    CValue first  = m_FirstOp->getValue(map, cyc, colMove, rowMove);
    CValue second = m_SecondOp->getValue(map, cyc, colMove, rowMove);

    if (!std::holds_alternative<double>(first) || !std::holds_alternative<double>(second))
        return CValue();

    return CValue(std::pow(std::get<double>(first), std::get<double>(second)));
}

// ======================== ======================== ======================== ========================
// Cloning
// ========================

std::shared_ptr<CExpr> CPow::clone() const
{
    return std::make_shared<CPow>(*this);
}
