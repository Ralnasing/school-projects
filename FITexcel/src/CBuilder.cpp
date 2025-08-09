#include "CBuilder.h"
#include "expr/CAdd.h"
#include "expr/CSub.h"
#include "expr/CMul.h"
#include "expr/CDiv.h"
#include "expr/CPow.h"
#include "expr/CNeg.h"
#include "expr/CEq.h"
#include "expr/CNe.h"
#include "expr/CLt.h"
#include "expr/CLe.h"
#include "expr/CGt.h"
#include "expr/CGe.h"
#include "expr/CValNum.h"
#include "expr/CValStr.h"
#include "expr/CValRef.h"
#include <utility>

// ======================== ======================== ======================== ========================
// Constructors
// ========================

CBuilder::CBuilder(const std::string& content)
: m_Content(content), m_ColMove(0), m_RowMove(0)
{
}

CBuilder::CBuilder(const CBuilder& builder)
: m_Content(builder.m_Content), m_ColMove(builder.m_ColMove), m_RowMove(builder.m_RowMove), m_ValueStack(builder.m_ValueStack)
{
}

CBuilder& CBuilder::operator=(const CBuilder& builder)
{
    if (this == &builder)
        return *this;

    m_Content    = builder.m_Content;
    m_ValueStack = builder.m_ValueStack;
    m_ColMove    = builder.m_ColMove;
    m_RowMove    = builder.m_RowMove;

    return *this;
}

// ======================== ======================== ======================== ========================
// Operator Builders
// ========================

void CBuilder::opAdd()
{
    auto second = m_ValueStack.top(); m_ValueStack.pop();
    auto first  = m_ValueStack.top(); m_ValueStack.pop();
    m_ValueStack.push(CAdd(first, second).clone());
}

void CBuilder::opSub()
{
    auto second = m_ValueStack.top(); m_ValueStack.pop();
    auto first  = m_ValueStack.top(); m_ValueStack.pop();
    m_ValueStack.push(CSub(first, second).clone());
}

void CBuilder::opMul()
{
    auto second = m_ValueStack.top(); m_ValueStack.pop();
    auto first  = m_ValueStack.top(); m_ValueStack.pop();
    m_ValueStack.push(CMul(first, second).clone());
}

void CBuilder::opDiv()
{
    auto second = m_ValueStack.top(); m_ValueStack.pop();
    auto first  = m_ValueStack.top(); m_ValueStack.pop();
    m_ValueStack.push(CDiv(first, second).clone());
}

void CBuilder::opPow()
{
    auto second = m_ValueStack.top(); m_ValueStack.pop();
    auto first  = m_ValueStack.top(); m_ValueStack.pop();
    m_ValueStack.push(CPow(first, second).clone());
}

void CBuilder::opNeg()
{
    auto first = m_ValueStack.top(); m_ValueStack.pop();
    m_ValueStack.push(CNeg(first).clone());
}

void CBuilder::opEq()
{
    auto second = m_ValueStack.top(); m_ValueStack.pop();
    auto first  = m_ValueStack.top(); m_ValueStack.pop();
    m_ValueStack.push(CEq(first, second).clone());
}

void CBuilder::opNe()
{
    auto second = m_ValueStack.top(); m_ValueStack.pop();
    auto first  = m_ValueStack.top(); m_ValueStack.pop();
    m_ValueStack.push(CNe(first, second).clone());
}

void CBuilder::opLt()
{
    auto second = m_ValueStack.top(); m_ValueStack.pop();
    auto first  = m_ValueStack.top(); m_ValueStack.pop();
    m_ValueStack.push(CLt(first, second).clone());
}

void CBuilder::opLe()
{
    auto second = m_ValueStack.top(); m_ValueStack.pop();
    auto first  = m_ValueStack.top(); m_ValueStack.pop();
    m_ValueStack.push(CLe(first, second).clone());
}

void CBuilder::opGt()
{
    auto second = m_ValueStack.top(); m_ValueStack.pop();
    auto first  = m_ValueStack.top(); m_ValueStack.pop();
    m_ValueStack.push(CGt(first, second).clone());
}

void CBuilder::opGe()
{
    auto second = m_ValueStack.top(); m_ValueStack.pop();
    auto first  = m_ValueStack.top(); m_ValueStack.pop();
    m_ValueStack.push(CGe(first, second).clone());
}

// ======================== ======================== ======================== ========================
// Value Constructors
// ========================

void CBuilder::valNumber(double val)
{
    m_ValueStack.push(CValNum(val).clone());
}

void CBuilder::valString(std::string val)
{
    m_ValueStack.push(CValStr(std::move(val)).clone());
}

void CBuilder::valReference(std::string val)
{
    bool isAbsCol = false;
    bool isAbsRow = false;

    for (size_t i = 0; i < val.size(); ++i)
    {
        if (val[i] == '$')
        {
            ::isalpha(val[i + 1]) ? isAbsCol = true : isAbsRow = true;
            val.erase(i, 1);
            --i;
        }
    }

    m_ValueStack.push(CValRef(val, isAbsCol, isAbsRow).clone());
}

void CBuilder::valRange(std::string /*val*/)
{
    /* TODO */
}

void CBuilder::funcCall(std::string /*fnName*/, int /*paramCount*/)
{
    /* TODO */
}

// ======================== ======================== ======================== ========================
// Evaluation
// ========================

CValue CBuilder::evaluate(const std::unordered_map<CPos, CBuilder, CPosHash>& map,
                                std::unordered_map<CPos, bool, CPosHash>&     cyc) const
{
    auto value = m_ValueStack.top();
    return value->getValue(map, cyc, m_ColMove, m_RowMove);
}

// ======================== ======================== ======================== ========================
// State Modifiers
// ========================

void CBuilder::changeExpr(const CBuilder& builder)
{
    m_ValueStack = builder.m_ValueStack;
    m_Content    = builder.m_Content;
}

void CBuilder::setMove(int colMove, int rowMove)
{
    m_ColMove = colMove;
    m_RowMove = rowMove;
}
