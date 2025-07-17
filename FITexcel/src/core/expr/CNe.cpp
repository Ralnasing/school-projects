#include "core/expr/CNe.h"
#include <variant>
#include <string>

// ======================== ======================== ======================== ========================
// Constructors
// ========================

CNe::CNe(std::shared_ptr<CExpr> first, std::shared_ptr<CExpr> second)
: m_FirstOp(std::move(first)), m_SecondOp(std::move(second))
{
}

// ======================== ======================== ======================== ========================
// Evaluation
// ========================

CValue CNe::getValue(const std::unordered_map<CPos, CBuilder, CPosHash>& map,
                           std::unordered_map<CPos, bool, CPosHash>&     cyc,
                     int                                                 colMove,
                     int                                                 rowMove) const
{
    CValue first  = m_FirstOp->getValue(map, cyc, colMove, rowMove);
    CValue second = m_SecondOp->getValue(map, cyc, colMove, rowMove);

    if (std::holds_alternative<std::monostate>(first) ||
        std::holds_alternative<std::monostate>(second) ||
        (std::holds_alternative<double>(first) && std::holds_alternative<std::string>(second)) ||
        (std::holds_alternative<std::string>(first) && std::holds_alternative<double>(second)))
    {
        return CValue();
    }

    if (std::holds_alternative<double>(first))
        return CValue(static_cast<double>(std::get<double>(first) != std::get<double>(second)));

    return CValue(static_cast<double>(std::get<std::string>(first) != std::get<std::string>(second)));
}

// ======================== ======================== ======================== ========================
// Cloning
// ========================

std::shared_ptr<CExpr> CNe::clone() const
{
    return std::make_shared<CNe>(*this);
}
