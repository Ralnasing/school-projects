#include "core/expr/CValNum.h"

// ======================== ======================== ======================== ========================
// Constructors
// ========================

CValNum::CValNum(double val)
: m_Val(val)
{
}

// ======================== ======================== ======================== ========================
// Evaluation
// ========================

CValue CValNum::getValue(const std::unordered_map<CPos, CBuilder, CPosHash>& map,
                               std::unordered_map<CPos, bool, CPosHash>&     cyc,
                         int                                                 colMove,
                         int                                                 rowMove) const
{
    return CValue(m_Val);
}

// ======================== ======================== ======================== ========================
// Cloning
// ========================

std::shared_ptr<CExpr> CValNum::clone() const
{
    return std::make_shared<CValNum>(*this);
}
