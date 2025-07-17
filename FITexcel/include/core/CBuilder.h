#ifndef CBUILDER_H
#define CBUILDER_H

#include <stack>
#include <string>
#include <memory>
#include <unordered_map>

#include "CExprBuilder.h"
#include "CExpr.h"
#include "CPos.h"
#include "CValue.h"

/**
 * @class CBuilder
 * @brief Concrete builder class that constructs expression trees from parsed tokens.
 * 
 * Inherits from CExprBuilder and builds expression objects (CExpr) based on parsed input,
 * such as literals, operators, references, functions, etc.
 */
class CBuilder : public CExprBuilder
{
  public:

    /**
     * Constructor with cell content
     * @param content Raw cell string content
     */
    explicit CBuilder(const std::string& content);

    /**
     * Copy constructor
     */
    CBuilder(const CBuilder& builder);

    /**
     * Copy assignment operator
     */
    CBuilder& operator=(const CBuilder& builder);

    void opAdd() override; ///< Addition (+)
    void opSub() override; ///< Subtraction (-)
    void opMul() override; ///< Multiplication (*)
    void opDiv() override; ///< Division (/)
    void opPow() override; ///< Exponentiation (^)
    void opNeg() override; ///< Unary minus (-)
    void opEq()  override; ///< Equality (=)
    void opNe()  override; ///< Inequality (<>)
    void opLt()  override; ///< Less than (<)
    void opLe()  override; ///< Less than or equal (<=)
    void opGt()  override; ///< Greater than (>)
    void opGe()  override; ///< Greater than or equal (>=)

    /**
     * Pushes a numeric literal
     * @param val Literal number
     */
    void valNumber(double val) override;

    /**
     * Pushes a string literal
     * @param val Literal string
     */
    void valString(std::string val) override;

    /**
     * Adds a reference to another cell
     * @param val Cell name (e.g. "A7", "$X$12")
     */
    void valReference(std::string val) override;

    /**
     * Adds a reference to a range of cells
     * @param val Range string (e.g. "A7:$C9", "$X$12:Z29")
     */
    void valRange(std::string val) override;

    /**
     * Adds a function call
     * @param fnName Name of the function
     * @param paramCount Number of arguments
     */
    void funcCall(std::string fnName, int paramCount) override;

    /**
     * Evaluates the resulting expression tree
     * @param map Map of positions to builders
     * @param cyc Cycle detection map
     * @return Evaluated value
     */
    CValue evaluate(const std::unordered_map<CPos, CBuilder, CPosHash>& map,
                          std::unordered_map<CPos, bool, CPosHash>&     cyc) const;

    /**
     * Replaces internal expression tree
     */
    void changeExpr(const CBuilder& builder);

    /**
     * Sets column and row movement (for relative reference handling)
     */
    void setMove(int colMove, int rowMove);

    std::string m_Content;  ///< Original cell content (raw)
    int         m_ColMove;  ///< Relative column offset
    int         m_RowMove;  ///< Relative row offset

  private:
    /**
     * Stack used for storing expression nodes during construction
     */
    std::stack<std::shared_ptr<CExpr>> m_ValueStack;
};

#endif // CBUILDER_H
