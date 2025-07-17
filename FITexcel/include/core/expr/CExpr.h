#ifndef CEXPR_H
#define CEXPR_H

#include <memory>
#include <unordered_map>
#include "CValue.h"
#include "CPos.h"
#include "CBuilder.h"

/**
 * @class CExpr
 * @brief Abstract base class for all expression operator classes.
 *
 * Provides an interface for evaluating expressions and cloning expression trees.
 */
class CExpr
{
  public:
    /**
     * Virtual destructor
     */
    virtual ~CExpr() = default;

    /**
     * Evaluates the expression.
     *
     * @param map  Cell map containing expression builders by position
     * @param cyc  Cycle detection map (used to prevent circular references)
     * @param colMove Optional column offset (e.g. relative formulas)
     * @param rowMove Optional row offset
     * @return Value of the expression (CValue: std::monostate, double, or std::string)
     */
    virtual CValue getValue(const std::unordered_map<CPos, CBuilder, CPosHash>& map,
                            std::unordered_map<CPos, bool, CPosHash>& cyc, int colMove, int rowMove) const = 0;

    /**
     * Creates a deep copy of the expression.
     *
     * This is used for polymorphic storage of expressions in containers.
     * @return Shared pointer to the newly cloned expression
     */
    virtual std::shared_ptr<CExpr> clone() const = 0;
};

#endif // CEXPR_H
