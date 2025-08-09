#include "CSpreadsheet.h"
#include "CBuilder.h"
#include "CPos.h"
#include <string>
#include <vector>
#include <unordered_map>
#include <utility>
#include <sstream>
#include <functional>
#include <algorithm>

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
    std::string line;
    
    while (std::getline(is, line)) {
        if (line.empty()) continue;
        
        std::vector<std::string> parts;
        std::string current;
        
        for (size_t i = 0; i < line.length(); i++) {
            if (line[i] == '\\' && i + 1 < line.length()) {
                if (line[i + 1] == '|') {
                    current += '|';
                    i++;
                } else if (line[i + 1] == '\\') {
                    current += '\\';
                    i++;
                } else if (line[i + 1] == 'n') {
                    current += '\n';
                    i++;
                } else {
                    current += line[i];
                }
            } else if (line[i] == '|') {
                parts.push_back(current);
                current.clear();
            } else {
                current += line[i];
            }
        }
        parts.push_back(current);
        
        if (parts.size() != 4) return false;
        
        try {
            CPos pos(parts[0]);
            int colMove = std::stoi(parts[2]);
            int rowMove = std::stoi(parts[3]);
            
            if (!tmpSheet.setCell(pos, parts[1])) return false;
            
            auto cell = tmpSheet.m_Sheet.find(pos);
            if (cell == tmpSheet.m_Sheet.end()) return false;
            cell->second.setMove(colMove, rowMove);
            
        } catch (...) {
            return false;
        }
    }
    
    *this = tmpSheet;
    return true;
}

bool CSpreadsheet::save(std::ostream& os) const
{
    for (const auto& [pos, builder] : m_Sheet) {
        std::string escapedContent = builder.m_Content;
        
        size_t pos_char = 0;
        while ((pos_char = escapedContent.find('|', pos_char)) != std::string::npos) {
            escapedContent.replace(pos_char, 1, "\\|");
            pos_char += 2;
        }
        pos_char = 0;
        while ((pos_char = escapedContent.find('\\', pos_char)) != std::string::npos) {
            if (pos_char + 1 >= escapedContent.length() || escapedContent[pos_char + 1] != '|') {
                escapedContent.replace(pos_char, 1, "\\\\");
                pos_char += 2;
            } else {
                pos_char += 2;
            }
        }
        pos_char = 0;
        while ((pos_char = escapedContent.find('\n', pos_char)) != std::string::npos) {
            escapedContent.replace(pos_char, 1, "\\n");
            pos_char += 2;
        }
        
        os << pos.cellName() << "|" << escapedContent << "|" 
           << builder.m_ColMove << "|" << builder.m_RowMove << "\n";
        
        if (!os.good()) return false;
    }
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
                    m_Sheet.erase(posDst);
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
