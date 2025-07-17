#include "core/expr/CValStr.h"

// ======================== ======================== ======================== ========================
// Constructors
// ========================

CValStr::CValStr(const std::string& val)
: m_Val(val)
{
}

// ======================== ======================== ======================== ========================
// Getters
// ========================

CValue CValStr::getValue(const std::unordered_map<CPos, CBuilder, CPosHash>& map,
                               std::unordered_map<CPos, bool, CPosHash>&     cyc,
                         int                                                 colMove,
                         int                                                 rowMove) const
{
    return CValue(m_Val);
}

// ======================== ======================== ======================== ========================
// Cloning
// ========================

std::shared_ptr<CExpr> CValStr::clone() const
{
    return std::make_shared<CValStr>(*this);
}
