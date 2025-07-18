#include "core/expr/CValRef.h"
#include "core/CPos.h"
#include "core/CBuilder.h"

// ======================== ======================== ======================== ========================
// Constructors
// ========================

CValRef::CValRef(const std::string& cell, bool absCol, bool absRow)
: m_Cell(cell), m_AbsCol(absCol), m_AbsRow(absRow)
{
}

// ======================== ======================== ======================== ========================
// Getters
// ========================

CValue CValRef::getValue(const std::unordered_map<CPos, CBuilder, CPosHash>& map,
                               std::unordered_map<CPos, bool, CPosHash>&     cyc,
                         int                                                 colMove,
                         int                                                 rowMove) const
{
    CPos pos = CPos(m_Cell) + std::make_pair(m_AbsCol ? 0 : colMove,
                                             m_AbsRow ? 0 : rowMove);

    if (pos.colIndex() < 0 || pos.rowIndex() < 0)
        return CValue();

    auto cell = map.find(pos);
    if (cell != map.end())
    {
        auto cellCyc = cyc.find(pos);
        if (cellCyc != cyc.end())
            return CValue();

        cyc.insert({pos, 0});
        CValue ret = cell->second.evaluate(map, cyc);
        cyc.erase(pos);
        return ret;
    }

    return CValue();
}

// ======================== ======================== ======================== ========================
// Cloning
// ========================

std::shared_ptr<CExpr> CValRef::clone() const
{
    return std::make_shared<CValRef>(*this);
}
