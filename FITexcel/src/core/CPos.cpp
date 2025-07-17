#include "core/CPos.h"
#include <sstream>
#include <stdexcept>
#include <algorithm>
#include <cctype>
#include <cmath>

// ======================== ======================== ======================== ========================
// Constructors
// ========================

CPos::CPos() : m_Col(std::make_pair("A", 0)), m_Row(0) {}

CPos::CPos(std::string_view str)
{
    if (str.empty() || str.data() == nullptr || str.size() > str.max_size())
        throw std::invalid_argument("Invalid input in CPos::CPos(std::string_view)");

    auto parts = divide(str.data());

    m_Cell = parts.first + std::to_string(parts.second);
    m_Col  = std::make_pair(parts.first, stringToIndex(parts.first));
    m_Row  = parts.second;
}

// ======================== ======================== ======================== ========================
// Getters
// ========================

size_t CPos::colIndex() const
{
    return m_Col.second;
}

size_t CPos::rowIndex() const
{
    return m_Row;
}

std::string CPos::cellName() const
{
    return m_Cell;
}

// ======================== ======================== ======================== ========================
// Operators
// ========================

bool CPos::operator==(const CPos& pos) const
{
    return m_Col == pos.m_Col && m_Row == pos.m_Row;
}

bool CPos::operator<(const CPos& pos) const
{
    return m_Col.second == pos.m_Col.second ? m_Row < pos.m_Row : m_Col.second < pos.m_Col.second;
}

CPos operator+(const CPos& pos, const std::pair<int, int>& vec)
{
    CPos ret;
    int  newColIdx = pos.m_Col.second + vec.first;
    int  newRowIdx = pos.m_Row + vec.second;

    ret.m_Col = std::make_pair(pos.indexToString(newColIdx), newColIdx);
    ret.m_Row = newRowIdx;

    if (ret.m_Col.second >= 0)
        ret.m_Cell = ret.m_Col.first + std::to_string(ret.m_Row);

    return ret;
}

// ======================== ======================== ======================== ========================
// Internal Helpers
// ========================

std::pair<std::string, int> CPos::divide(const std::string& str) const
{
    std::istringstream iss(str);
    std::string        cellId, remaining;

    if (!(iss >> cellId) ||
        (iss.peek() != EOF && iss >> remaining && !std::all_of(remaining.begin(), remaining.end(), ::isspace)))
        throw std::invalid_argument("Invalid input in CPos::divide [1]");

    int         firstNum = str.find_first_of("0123456789");
    std::string col      = str.substr(0, firstNum);
    std::string row      = str.substr(firstNum);

    if (!std::all_of(col.begin(), col.end(), ::isalpha) || !std::all_of(row.begin(), row.end(), ::isdigit))
        throw std::invalid_argument("Invalid input in CPos::divide [2]");

    int rowNum = std::stoi(row);
    std::transform(col.begin(), col.end(), col.begin(), ::toupper);

    return {col, rowNum};
}

int CPos::stringToIndex(const std::string& str) const
{
    int index = 0;

    for (size_t i = 0, y = str.length() - 1; i < str.length(); ++i, --y)
    {
        index += (str[i] - 'A' + 1) * std::pow(ENG_ALPH_SIZE, y);
    }

    return index - 1;
}

std::string CPos::indexToString(int index) const
{
    std::string cell;

    for (size_t i = index + 1; i > 0; i /= ENG_ALPH_SIZE)
    {
        char tmp = (i % ENG_ALPH_SIZE) + ('A' - 1);
        cell     = tmp + cell;
    }

    return cell;
}
