#include "doctest.h"

#include "CSpreadsheet.h"

#include "sstream"

TEST_CASE("CSpreadsheet test") {

    std::ostringstream oss;
    std::istringstream iss;
    std::string data;

    SUBCASE("Construction and basic functions") {
        CSpreadsheet s;

        CHECK(s.setCell( CPos("A0"), "5" ));
        CHECK(s.setCell( CPos("A1"), "ahoj" ));
        CHECK(s.setCell( CPos("A2"), "jak se mas?" ));
        CHECK(s.setCell( CPos("A3"), " " ));
        CHECK(s.setCell( CPos("CC10"), "20"));
        CHECK(s.setCell( CPos("B23"), "=A0*$CC$10" ));
        CHECK(s.setCell( CPos("ACG1"), "=5^2+$A1" ));
        CHECK(s.setCell( CPos("YZ90"), "=A$1+A3+A2+A0" ));
        CHECK(s.setCell( CPos("CCC0"), "=10/2+A0" ));

        CHECK(s.getValue(CPos ( "A0" ) ) == CValue(5.0));
        CHECK(s.getValue(CPos ( "A1" ) ) == CValue("ahoj"));
        CHECK(s.getValue(CPos ( "A2" ) ) == CValue("jak se mas?"));
        CHECK(s.getValue(CPos ( "A3" ) ) == CValue(" "));
        CHECK(s.getValue(CPos ( "CC10" ) ) == CValue(20.0));
        CHECK(s.getValue(CPos ( "B23" ) ) == CValue(100.0));
        CHECK(s.getValue(CPos ( "ACG1" ) ) == CValue("25.000000ahoj"));
        CHECK(s.getValue(CPos ( "YZ90" ) ) == CValue("ahoj jak se mas?5.000000"));
        CHECK(s.getValue(CPos ( "CCC0" ) ) == CValue(10.0));
    }

    SUBCASE("Copy sheet test, load/save") {
        CSpreadsheet x0, x1;

        CHECK(x0.setCell(CPos("A1"), "10"));
        CHECK(x0.setCell(CPos("A2"), "20.5"));
        CHECK(x0.setCell(CPos("A3"), "3e1"));
        CHECK(x0.setCell(CPos("A4"), "=40"));
        CHECK(x0.setCell(CPos("A5"), "=5e+1"));
        CHECK(x0.setCell(CPos("A6"), "raw text with any characters, including a quote \" or a newline\n"));
        CHECK(x0.setCell(CPos("A7"), "=\"quoted string, quotes must be doubled: \"\". Moreover, backslashes are needed for C++.\""));
        
        CHECK(x0.getValue(CPos( "A1" )) == CValue(10.0));
        CHECK(x0.getValue(CPos( "A2" )) == CValue(20.5));
        CHECK(x0.getValue(CPos( "A3" )) == CValue(30.0));
        CHECK(x0.getValue(CPos( "A4" )) == CValue(40.0));
        CHECK(x0.getValue(CPos( "A5" )) == CValue(50.0));
        CHECK(x0.getValue(CPos( "A6" )) == CValue("raw text with any characters, including a quote \" or a newline\n"));
        CHECK(x0.getValue(CPos( "A7" )) == CValue("quoted string, quotes must be doubled: \". Moreover, backslashes are needed for C++."));
        CHECK(x0.getValue(CPos( "A8" )) == CValue() );
        CHECK(x0.getValue(CPos( "AAAA9999" ) ) == CValue() );

        CHECK(x0.setCell(CPos("B1"), "=A1+A2*A3"));
        CHECK(x0.setCell(CPos("B2"), "= -A1 ^ 2 - A2 / 2   "));
        CHECK(x0.setCell(CPos("B3"), "= 2 ^ $A$1"));
        CHECK(x0.setCell(CPos("B4"), "=($A1+A$2)^2"));
        CHECK(x0.setCell(CPos("B5"), "=B1+B2+B3+B4"));
        CHECK(x0.setCell(CPos("B6"), "=B1+B2+B3+B4+B5"));

        CHECK(x0.getValue(CPos("B1")) == CValue(625.0));
        CHECK(x0.getValue(CPos("B2")) == CValue(-110.25));
        CHECK(x0.getValue(CPos("B3")) == CValue(1024.0));
        CHECK(x0.getValue(CPos("B4")) == CValue(930.25));
        CHECK(x0.getValue(CPos("B5")) == CValue(2469.0));
        CHECK(x0.getValue(CPos("B6")) == CValue(4938.0));
        
        CHECK(x0.setCell(CPos ("A1"), "12"));
        
        CHECK(x0.getValue(CPos("B1")) == CValue(627.0 ));
        CHECK(x0.getValue(CPos("B2")) == CValue(-154.25 ));
        CHECK(x0.getValue(CPos("B3")) == CValue(4096.0 ));
        CHECK(x0.getValue(CPos("B4")) == CValue(1056.25 ));
        CHECK(x0.getValue(CPos("B5")) == CValue(5625.0 ));
        CHECK(x0.getValue(CPos("B6")) == CValue(11250.0 ));
        
        x1 = x0;
        
        CHECK (x0.setCell(CPos("A2"), "100"));
        CHECK (x1.setCell(CPos("A2"), "=A3+A5+A4"));
        
        CHECK(x0.getValue(CPos("B1")) == CValue(3012.0));
        CHECK(x0.getValue(CPos("B2")) == CValue(-194.0));
        CHECK(x0.getValue(CPos("B3")) == CValue(4096.0));
        CHECK(x0.getValue(CPos("B4")) == CValue(12544.0));
        CHECK(x0.getValue(CPos("B5")) == CValue(19458.0));
        CHECK(x0.getValue(CPos("B6")) == CValue(38916.0));
        CHECK(x1.getValue(CPos("A2")) == CValue (120.0));

        CHECK(x1.getValue(CPos("B1")) == CValue(3612.0));
        CHECK(x1.getValue(CPos("B2")) == CValue(-204.0));
        CHECK(x1.getValue(CPos("B3")) == CValue(4096.0));
        CHECK(x1.getValue(CPos("B4")) == CValue(17424.0));
        CHECK(x1.getValue(CPos("B5")) == CValue(24928.0));
        CHECK(x1.getValue(CPos("B6")) == CValue(49856.0));

        oss.clear();
        oss.str("");

        CHECK(x0.save(oss));
        
        data = oss.str();
        iss.clear();
        iss.str(data);
        
        CHECK(x1.load(iss));
        
        CHECK(x1.getValue(CPos("B1")) == CValue(3012.0));
        CHECK(x1.getValue(CPos("B2")) == CValue(-194.0));
        CHECK(x1.getValue(CPos("B3")) == CValue(4096.0));
        CHECK(x1.getValue(CPos("B4")) == CValue(12544.0));
        CHECK(x1.getValue(CPos("B5")) == CValue(19458.0));
        CHECK(x1.getValue(CPos("B6")) == CValue(38916.0));
        
        CHECK(x0.setCell(CPos("A3"), "4e1"));
        
        CHECK(x1.getValue(CPos("B1")) == CValue(3012.0));
        CHECK(x1.getValue(CPos("B2")) == CValue(-194.0));
        CHECK(x1.getValue(CPos("B3")) == CValue(4096.0));
        CHECK(x1.getValue(CPos("B4")) == CValue(12544.0));
        CHECK(x1.getValue(CPos("B5")) == CValue(19458.0));
        CHECK(x1.getValue(CPos("B6")) == CValue(38916.0));
        
        oss.clear();
        oss.str("");
        
        CHECK(x0.save(oss));
        
        data = oss.str();
        for (size_t i = 0; i < std::min<size_t>(data.length(), 10); i++)
            data[i] ^= 0x5a;
        
        iss.clear();
        iss.str(data);
        
        CHECK_FALSE(x1.load(iss));
    }

    SUBCASE("copyRect test") {
        CSpreadsheet copy;
        
        CHECK(copy.setCell(CPos("A1"), "10"));
        CHECK(copy.setCell(CPos("A2"), "=A1*A1"));
        CHECK(copy.setCell(CPos("A3"), "30"));
        CHECK(copy.setCell(CPos("A4"), "=A1"));
        CHECK(copy.setCell(CPos("A5"), "=-\"abc\""));
        CHECK(copy.setCell(CPos("A6"), "=B2"));
        
        copy.copyRect(CPos("A1"), CPos("A1"), 1, 1);
        
        CHECK(copy.getValue(CPos("A1")) == CValue(10.0));
        CHECK(copy.getValue(CPos("A2")) == CValue(100.0));
        
        copy.copyRect(CPos("A1"), CPos("A3"), 1, 1);
        
        CHECK(copy.getValue(CPos("A2")) == CValue(900.0));
        CHECK(copy.getValue(CPos("A4")) == CValue(30.0));
        CHECK(copy.getValue(CPos("A5")) == CValue());
        CHECK(copy.getValue(CPos("A6")) == CValue());
        
        copy.copyRect(CPos("B2"), CPos("A1"), 1, 1);
        
        CHECK(copy.getValue(CPos("A6")) == CValue(30.0));
        CHECK(copy.getValue(CPos("B2")) == CValue(30.0));
        
        copy.copyRect(CPos("B2"), CPos("B3"), 1, 1);
        
        CHECK(copy.getValue(CPos("B2")) == CValue());
        
        CHECK(copy.setCell(CPos("H10"), "=H11 * 3"));
        CHECK(copy.setCell(CPos("H11"), "=H10"));
        
        CHECK(copy.getValue(CPos("H10")) == CValue());
        CHECK(copy.getValue(CPos("H11")) == CValue());
    }
}