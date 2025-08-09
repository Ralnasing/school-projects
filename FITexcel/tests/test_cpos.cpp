#include "doctest.h"

#include "CPos.h"

#include <unordered_set>

TEST_CASE("CPos test") {
    SUBCASE("Valid construction and indexes") {
        CPos p1("A1");
        CHECK(p1.colIndex() == 0);
        CHECK(p1.rowIndex() == 1);
        CHECK(p1.cellName() == "A1");

        CPos p2("B2");
        CHECK(p2.colIndex() == 1);
        CHECK(p2.rowIndex() == 2);
        CHECK(p2.cellName() == "B2");

        CPos p3("Z99");
        CHECK(p3.colIndex() == 25);
        CHECK(p3.rowIndex() == 99);
        CHECK(p3.cellName() == "Z99");

        CPos p4("AA10");
        CHECK(p4.colIndex() == 26);
        CHECK(p4.rowIndex() == 10);
        CHECK(p4.cellName() == "AA10");
    }

    SUBCASE("Operators") {
        CPos a("A1"), b("A1"), c("B2"), d("AA0");
        CHECK(a == b);
        CHECK(b == a);
        CHECK_FALSE(a == c);
        CHECK_FALSE(c == a);
        CHECK(a < c);
        CHECK(a < d);
        CHECK_FALSE(a < b);
        CHECK_FALSE(c < a);

        CPos moved = c + std::make_pair(2, 3);
        CHECK(moved.colIndex() == 3);
        CHECK(moved.rowIndex() == 5);
        CHECK(moved.cellName() == "D5");

        CPos moved2 = c + std::make_pair(-1, -1);
        CHECK(moved2.colIndex() == 0);
        CHECK(moved2.rowIndex() == 1);
    }

    SUBCASE("CPos Hash") {
        std::unordered_set<CPos, CPosHash> s;
        s.insert(CPos("A1"));
        s.insert(CPos("B2"));
        CHECK(s.find(CPos("A1")) != s.end());
        CHECK(s.find(CPos("B2")) != s.end());
        CHECK(s.find(CPos("C3")) == s.end());
    }

    SUBCASE("Invalid inputs") {
        CHECK_THROWS(CPos("0A")); 
        CHECK_THROWS(CPos("AAA9999A"));
        CHECK_THROWS(CPos("AAA9999A"));
        CHECK_THROWS(CPos("ZA 9"));
        CHECK_THROWS(CPos("      "));
        CHECK_THROWS(CPos("   AB$44  "));
    }
}