#include "doctest.h"

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
#include "CPos.h"
#include "CBuilder.h"

#include <unordered_map>
#include <memory>

std::unordered_map<CPos, CBuilder, CPosHash> dummyMap;
std::unordered_map<CPos, bool, CPosHash> dummyCyc;

TEST_CASE("Arithmetic operators") {
    SUBCASE("CAdd") {
        // Numbers
        CHECK(CAdd(std::make_shared<CValNum>(2), std::make_shared<CValNum>(3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(5.0));
        CHECK(CAdd(std::make_shared<CValNum>(0), std::make_shared<CValNum>(3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(3.0));
        CHECK(CAdd(std::make_shared<CValNum>(221), std::make_shared<CValNum>(42)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(263.0));
        CHECK(CAdd(std::make_shared<CValNum>(-2), std::make_shared<CValNum>(-3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(-5.0));
        CHECK(CAdd(std::make_shared<CValNum>(-2), std::make_shared<CValNum>(3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(1.0));

        // Strings/Numbers
        CHECK(CAdd(std::make_shared<CValStr>("ahoj"), std::make_shared<CValNum>(3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue("ahoj3.000000"));
        CHECK(CAdd(std::make_shared<CValStr>("ahoj"), std::make_shared<CValStr>(", jak se mas?")).getValue(dummyMap, dummyCyc, 0, 0) == CValue("ahoj, jak se mas?"));
        CHECK(CAdd(std::make_shared<CValNum>(221), std::make_shared<CValStr>("ahoj")).getValue(dummyMap, dummyCyc, 0, 0) == CValue("221.000000ahoj"));
    }
    SUBCASE("CSub") {
        CHECK(CSub(std::make_shared<CValNum>(5), std::make_shared<CValNum>(3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(2.0));
        CHECK(CSub(std::make_shared<CValNum>(0), std::make_shared<CValNum>(3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(-3.0));
        CHECK(CSub(std::make_shared<CValNum>(221), std::make_shared<CValNum>(42)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(179.0));
        CHECK(CSub(std::make_shared<CValNum>(-2), std::make_shared<CValNum>(-3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(1.0));
        CHECK(CSub(std::make_shared<CValNum>(-2), std::make_shared<CValNum>(3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(-5.0));
    }
    SUBCASE("CMul") {
        CHECK(CMul(std::make_shared<CValNum>(4), std::make_shared<CValNum>(3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(12.0));
        CHECK(CMul(std::make_shared<CValNum>(0), std::make_shared<CValNum>(3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(0.0));
        CHECK(CMul(std::make_shared<CValNum>(-4), std::make_shared<CValNum>(2)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(-8.0));
        CHECK(CMul(std::make_shared<CValNum>(7), std::make_shared<CValNum>(-3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(-21.0));
    }
    SUBCASE("CDiv") {
        CHECK(CDiv(std::make_shared<CValNum>(10), std::make_shared<CValNum>(2)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(5.0));
        CHECK(CDiv(std::make_shared<CValNum>(0), std::make_shared<CValNum>(5)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(0.0));
        CHECK(CDiv(std::make_shared<CValNum>(-9), std::make_shared<CValNum>(3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(-3.0));
        CHECK(CDiv(std::make_shared<CValNum>(7), std::make_shared<CValNum>(2)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(3.5));
    }
    SUBCASE("CPow") {
        CHECK(CPow(std::make_shared<CValNum>(2), std::make_shared<CValNum>(3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(8.0));
        CHECK(CPow(std::make_shared<CValNum>(5), std::make_shared<CValNum>(0)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(1.0));
        CHECK(CPow(std::make_shared<CValNum>(2), std::make_shared<CValNum>(-2)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(0.25));
        CHECK(CPow(std::make_shared<CValNum>(-2), std::make_shared<CValNum>(3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(-8.0));
    }
    SUBCASE("CNeg") {
        CHECK(CNeg(std::make_shared<CValNum>(5)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(-5.0));
        CHECK(CNeg(std::make_shared<CValNum>(-5)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(5.0));
        CHECK(CNeg(std::make_shared<CValNum>(0)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(0.0));
        CHECK(CNeg(std::make_shared<CValNum>(-0)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(0.0));
    }
}

TEST_CASE("Relational operators") {
    SUBCASE("CEq") {
        CHECK(CEq(std::make_shared<CValNum>(2), std::make_shared<CValNum>(2)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(1.0));
        CHECK(CEq(std::make_shared<CValNum>(2), std::make_shared<CValNum>(3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(0.0));
        CHECK(CEq(std::make_shared<CValNum>(-2), std::make_shared<CValNum>(2)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(0.0));
        CHECK(CEq(std::make_shared<CValNum>(-0), std::make_shared<CValNum>(0)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(1.0));
    }
    SUBCASE("CNe") {
        CHECK(CNe(std::make_shared<CValNum>(2), std::make_shared<CValNum>(2)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(0.0));
        CHECK(CNe(std::make_shared<CValNum>(2), std::make_shared<CValNum>(3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(1.0));
        CHECK(CNe(std::make_shared<CValNum>(-2), std::make_shared<CValNum>(2)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(1.0));
        CHECK(CNe(std::make_shared<CValNum>(-0), std::make_shared<CValNum>(0)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(0.0));
    }
    SUBCASE("CLt") {
        CHECK(CLt(std::make_shared<CValNum>(2), std::make_shared<CValNum>(2)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(0.0));
        CHECK(CLt(std::make_shared<CValNum>(2), std::make_shared<CValNum>(3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(1.0));
        CHECK(CLt(std::make_shared<CValNum>(-2), std::make_shared<CValNum>(2)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(1.0));
        CHECK(CLt(std::make_shared<CValNum>(-0), std::make_shared<CValNum>(0)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(0.0));
    }
    SUBCASE("CLe") {
        CHECK(CLe(std::make_shared<CValNum>(2), std::make_shared<CValNum>(2)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(1.0));
        CHECK(CLe(std::make_shared<CValNum>(2), std::make_shared<CValNum>(3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(1.0));
        CHECK(CLe(std::make_shared<CValNum>(-2), std::make_shared<CValNum>(2)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(1.0));
        CHECK(CLe(std::make_shared<CValNum>(-0), std::make_shared<CValNum>(0)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(1.0));
    }
    SUBCASE("CGt") {
        CHECK(CGt(std::make_shared<CValNum>(2), std::make_shared<CValNum>(2)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(0.0));
        CHECK(CGt(std::make_shared<CValNum>(2), std::make_shared<CValNum>(3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(0.0));
        CHECK(CGt(std::make_shared<CValNum>(-2), std::make_shared<CValNum>(2)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(0.0));
        CHECK(CGt(std::make_shared<CValNum>(-0), std::make_shared<CValNum>(0)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(0.0));
    }
    SUBCASE("CGe") {
        CHECK(CGe(std::make_shared<CValNum>(2), std::make_shared<CValNum>(2)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(1.0));
        CHECK(CGe(std::make_shared<CValNum>(2), std::make_shared<CValNum>(3)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(0.0));
        CHECK(CGe(std::make_shared<CValNum>(-2), std::make_shared<CValNum>(2)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(0.0));
        CHECK(CGe(std::make_shared<CValNum>(-0), std::make_shared<CValNum>(0)).getValue(dummyMap, dummyCyc, 0, 0) == CValue(1.0));
    }
}
