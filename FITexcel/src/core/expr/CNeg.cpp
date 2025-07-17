#include "core/expr/CNeg.h"
#include <variant>

// ======================== ======================== ======================== ========================
// Constructors
// ========================

CNeg::CNeg(std::shared_ptr<CExpr> operand)
: m_Op(std::move(operand))
{
}

// ======================== ======================== ======================== ========================
// Evaluation
// ========================

CValue CNeg::getValue(const std::unordered_map<CPos, CBuilder, CPosHash>& map,
                            std::unordered_map<CPos, bool, CPosHash>&     cyc,
                      int                                                 colMove,
                      int                                                 rowMove) const
{
    CValue op = m_Op->getValue(map, cyc, colMove, rowMove);

    if (!std::holds_alternative<double>(op))
        return CValue();

    return CValue(-std::get<double>(op));
}

// ======================== ======================== ======================== ========================
// Cloning
// ========================

std::shared_ptr<CExpr> CNeg::clone() const
{
    return std::make_shared<CNeg>(*this);
}
