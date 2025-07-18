#ifndef CVALUE_H
#define CVALUE_H

#include <variant>
#include <string>

/**
 * @typedef CValue
 * @brief Represents a possible value of an expression: number, text, or empty.
 */
using CValue = std::variant<std::monostate, double, std::string>;

#endif // CVALUE_H
