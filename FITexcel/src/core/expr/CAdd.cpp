#include "core/expr/CAdd.h"
#include <variant>
#include <string>

// ======================== ======================== ======================== ========================
// Internal Helpers
// ========================

/**
 * Handles addition of numeric and string types — overload for (double + string)
 */
static CValue plus(double first, const std::string& second)
{
    return CValue(std::to_string(first) + second);
}

/**
 * Handles addition of numeric and string types — overload for (string + double)
 */
static CValue plus(const std::string& first, double second)
{
    return CValue(first + std::to_string(second));
}

// ======================== ======================== ======================== ========================
// Constructors
// ========================

CAdd::CAdd(std::shared_ptr<CExpr> first, std::shared_ptr<CExpr> second)
: m_FirstOp(std::move(first)), m_SecondOp(std::move(second))
{
}

// ======================== ======================== ======================== ========================
// Evaluation
// ========================

CValue CAdd::getValue(const std::unordered_map<CPos, CBuilder, CPosHash>& map,
                            std::unordered_map<CPos, bool, CPosHash>&     cyc,
                      int                                                 colMove,
                      int                                                 rowMove) const
{
    CValue first  = m_FirstOp->getValue(map, cyc, colMove, rowMove);
    CValue second = m_SecondOp->getValue(map, cyc, colMove, rowMove);

    if (std::holds_alternative<std::monostate>(first) || std::holds_alternative<std::monostate>(second))
        return CValue();

    size_t choice = 0;
    if (!std::holds_alternative<double>(first))  choice += 1;
    if (!std::holds_alternative<double>(second)) choice += 2;

    switch (choice)
    {
        case 0:
            return std::get<double>(first) + std::get<double>(second);
        case 1:
            return plus(std::get<std::string>(first), std::get<double>(second));
        case 2:
            return plus(std::get<double>(first), std::get<std::string>(second));
        default:
            return std::get<std::string>(first) + std::get<std::string>(second);
    }
}

// ======================== ======================== ======================== ========================
// Cloning
// ========================

std::shared_ptr<CExpr> CAdd::clone() const
{
    return std::make_shared<CAdd>(*this);
}
