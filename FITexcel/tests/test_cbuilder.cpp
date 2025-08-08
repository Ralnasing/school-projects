#include "doctest.h"

#include "CBuilder.h"

#include <unordered_map>

TEST_CASE("CBuilder test") {

    std::unordered_map<CPos, CBuilder, CPosHash> dummyMap;
    std::unordered_map<CPos, bool, CPosHash> dummyCyc;

    SUBCASE("Literals and operators") {
        CBuilder a( "" );
        a.valNumber(2);
        a.valNumber(3);
        a.opAdd();
        CHECK(a.evaluate(dummyMap, dummyCyc) == CValue(5.0));

        CBuilder b( "" );
        b.valNumber(2);
        b.valNumber(3);
        b.opSub();
        CHECK(b.evaluate(dummyMap, dummyCyc) == CValue(-1.0));
        
        CBuilder c( "" );
        c.valNumber(3);
        c.valNumber(2);
        c.opDiv();
        CHECK(c.evaluate(dummyMap, dummyCyc) == CValue(1.5));

        CBuilder d( "" );
        d.valNumber(2);
        d.valNumber(3);
        d.opPow();
        CHECK(d.evaluate(dummyMap, dummyCyc) == CValue(8.0));

        CBuilder e( "" );
        e.valNumber(2);
        e.opNeg();
        CHECK(e.evaluate(dummyMap, dummyCyc) == CValue(-2.0));

        CBuilder f( "" );
        f.valNumber(2);
        f.valNumber(2);
        f.opEq();
        CHECK(f.evaluate(dummyMap, dummyCyc) == CValue(1.0));

        CBuilder g( "" );
        g.valNumber(2);
        g.valNumber(3);
        g.opNe();
        CHECK(g.evaluate(dummyMap, dummyCyc) == CValue(1.0));

        CBuilder h( "" );
        h.valNumber(2);
        h.valNumber(3);
        h.opLt();
        CHECK(h.evaluate(dummyMap, dummyCyc) == CValue(1.0));

        CBuilder i( "" );
        i.valNumber(2);
        i.valNumber(3);
        i.opLe();
        CHECK(i.evaluate(dummyMap, dummyCyc) == CValue(1.0));

        CBuilder j( "" );
        j.valNumber(2);
        j.valNumber(3);
        j.opGt();
        CHECK(j.evaluate(dummyMap, dummyCyc) == CValue(0.0));

        CBuilder k( "" );
        k.valNumber(2);
        k.valNumber(3);
        k.opGe();
        CHECK(k.evaluate(dummyMap, dummyCyc) == CValue(0.0));

        CBuilder l( "" );
        l.valNumber(2);
        l.valNumber(3);
        l.opMul();
        CHECK(l.evaluate(dummyMap, dummyCyc) == CValue(6.0));
    }

    SUBCASE("Copy and assignment") {
        CBuilder b1( "" );
        b1.valNumber(7);

        CBuilder b2 = b1;
        CBuilder b3( b2 );

        CHECK(b1.evaluate(dummyMap, dummyCyc) == CValue(7.0));
        CHECK(b2.evaluate(dummyMap, dummyCyc) == CValue(7.0));
        CHECK(b3.evaluate(dummyMap, dummyCyc) == CValue(7.0));

        b1.valNumber(8);

        CHECK(b1.evaluate(dummyMap, dummyCyc) == CValue(8.0));
        CHECK(b2.evaluate(dummyMap, dummyCyc) == CValue(7.0));
        CHECK(b3.evaluate(dummyMap, dummyCyc) == CValue(7.0));
    }

    SUBCASE("valString test") {
        CBuilder b( "" );
        b.valString("Hello");
        CHECK(b.evaluate(dummyMap, dummyCyc) == CValue("Hello"));

        b.valString(" there");
        b.opAdd();
        CHECK(b.evaluate(dummyMap, dummyCyc) == CValue("Hello there"));

        b.valNumber(1000);
        b.opAdd();
        CHECK(b.evaluate(dummyMap, dummyCyc) == CValue("Hello there1000.000000"));
    }

    SUBCASE("valReference absolute/relative") {
        CBuilder refA( "" );
        refA.valNumber(42);

        std::unordered_map<CPos, CBuilder, CPosHash> map;
        map.emplace(CPos("B2"), refA);

        CBuilder b( "" );
        b.valReference("B2");

        std::unordered_map<CPos, bool, CPosHash> cyc;
        CHECK(b.evaluate(map, cyc) == CValue(42.0));
    }
}