#include "core/CSpreadsheet.h"
#include "core/CBuilder.h"
#include "core/CPos.h"
#include <string>
#include <vector>
#include <unordered_map>
#include <utility>
#include <sstream>
#include <functional>

// ======================== ======================== ======================== ========================
// Constructors
// ========================

CSpreadsheet::CSpreadsheet() = default;

CSpreadsheet::CSpreadsheet(const CSpreadsheet& src)
: m_Sheet(src.m_Sheet)
{
}

CSpreadsheet& CSpreadsheet::operator=(const CSpreadsheet& src)
{
    if (this != &src)
        m_Sheet = src.m_Sheet;
    return *this;
}

// ======================== ======================== ======================== ========================
// File Operations
// ========================

bool CSpreadsheet::load(std::istream& is)
{
    CSpreadsheet tmpSheet;
    std::string input, check;
    std::vector<std::string> tokens;

    while (std::getline(is, input, '%'))
    {
        tokens.push_back(input);

        if (tokens.size() == 4)
        {
            const std::string& posStr   = tokens[0];
            const std::string& contents = tokens[1];
            int colMove, rowMove;

            try
            {
                colMove = std::stoi(tokens[2]);
                rowMove = std::stoi(tokens[3]);
            }
            catch (...) { return false; }

            check += posStr + contents + tokens[2] + tokens[3];

            try
            {
                CPos pos(posStr);
                if (!tmpSheet.setCell(pos, contents)) return false;

                auto cell = tmpSheet.m_Sheet.find(pos);
                if (cell == tmpSheet.m_Sheet.end()) return false;

                cell->second.setMove(colMove, rowMove);
            }
            catch (...) { return false; }

            tokens.clear();
        }
    }

    if (tokens.size() != 1) return false;
    if (tokens[0] != std::to_string(std::hash<std::string>{}(check))) return false;

    *this = tmpSheet;
    return true;
}

bool CSpreadsheet::save(std::ostream& os) const
{
    std::string check;

    for (const auto& [pos, builder] : m_Sheet)
    {
        if (!(os << pos.cellName() << "%" << builder.m_Content << "%"
                 << builder.m_ColMove << "%" << builder.m_RowMove << "%"))
            return false;

        check += pos.cellName() + builder.m_Content +
                 std::to_string(builder.m_ColMove) + std::to_string(builder.m_RowMove);
    }

    if (!(os << std::hash<std::string>{}(check))) return false;
    return true;
}

// ======================== ======================== ======================== ========================
// Cell Management
// ========================

bool CSpreadsheet::setCell(CPos pos, std::string contents)
{
    CBuilder build(contents);

    try
    {
        parseExpression(contents, build);
    }
    catch (...) { return false; }

    auto it = m_Sheet.find(pos);
    if (it != m_Sheet.end())
        it->second.changeExpr(build);
    else
        m_Sheet.insert({pos, build});

    return true;
}

CValue CSpreadsheet::getValue(CPos pos)
{
    std::unordered_map<CPos, bool, CPosHash> cyc;
    cyc.insert({pos, false});

    auto it = m_Sheet.find(pos);
    if (it != m_Sheet.end())
        return it->second.evaluate(m_Sheet, cyc);

    return CValue();
}

// ======================== ======================== ======================== ========================
// Copy Functionality
// ========================

void CSpreadsheet::copyRect(CPos dst, CPos src, int w, int h)
{
    std::vector<std::pair<CPos, CBuilder>> srcVec;
    std::vector<CPos> dstVec;

    for (int i = 0; i < w; ++i)
    {
        for (int j = 0; j < h; ++j)
        {
            CPos posSrc = src + std::make_pair(i, j);
            CPos posDst = dst + std::make_pair(i, j);

            auto cellSrc = m_Sheet.find(posSrc);
            if (cellSrc != m_Sheet.end())
            {
                srcVec.emplace_back(cellSrc->first, cellSrc->second);
                dstVec.push_back(posDst);
            }
            else
            {
                auto cellDst = m_Sheet.find(posDst);
                if (cellDst != m_Sheet.end())
                    setCell(posDst, "=\"undef\"");
            }
        }
    }

    for (size_t i = 0; i < srcVec.size(); ++i)
    {
        setCell(dstVec[i], srcVec[i].second.m_Content);

        auto& dstCell = m_Sheet.at(dstVec[i]);
        dstCell.setMove(
            dstVec[i].colIndex() - srcVec[i].first.colIndex() + srcVec[i].second.m_ColMove,
            dstVec[i].rowIndex() - srcVec[i].first.rowIndex() + srcVec[i].second.m_RowMove
        );
    }
}
