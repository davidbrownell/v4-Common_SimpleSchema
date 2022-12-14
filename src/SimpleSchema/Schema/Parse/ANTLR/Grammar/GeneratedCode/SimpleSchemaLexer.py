# Generated from C:\Code\v4\Common\SimpleSchema\src\SimpleSchema\Schema\Parse\ANTLR\Grammar\SimpleSchema.g4 by ANTLR 4.11.1
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
    from typing import TextIO
else:
    from typing.io import TextIO



from antlr_denter.DenterHelper import DenterHelper
from SimpleSchemaParser import SimpleSchemaParser



def serializedATN():
    return [
        4,0,61,440,6,-1,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,
        2,6,7,6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,
        13,7,13,2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,
        19,2,20,7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,
        26,7,26,2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,2,31,7,31,2,32,7,
        32,2,33,7,33,2,34,7,34,2,35,7,35,2,36,7,36,2,37,7,37,2,38,7,38,2,
        39,7,39,2,40,7,40,2,41,7,41,2,42,7,42,2,43,7,43,2,44,7,44,2,45,7,
        45,2,46,7,46,2,47,7,47,2,48,7,48,2,49,7,49,2,50,7,50,2,51,7,51,2,
        52,7,52,2,53,7,53,2,54,7,54,2,55,7,55,2,56,7,56,2,57,7,57,2,58,7,
        58,2,59,7,59,2,60,7,60,1,0,1,0,1,1,1,1,1,2,1,2,1,3,1,3,1,4,1,4,1,
        5,1,5,1,6,1,6,1,7,1,7,1,8,1,8,1,9,1,9,1,9,1,9,1,10,1,10,1,10,1,10,
        1,11,1,11,1,11,1,11,1,12,1,12,1,12,1,12,1,12,1,13,1,13,1,13,1,13,
        1,13,1,14,1,14,1,14,1,14,1,14,1,15,1,15,1,15,1,16,1,16,1,16,1,17,
        1,17,1,17,1,18,1,18,1,19,1,19,1,20,1,20,1,20,1,21,1,21,1,21,1,22,
        1,22,1,22,1,23,1,23,1,23,1,23,1,23,1,23,1,24,1,24,1,24,1,24,1,24,
        1,24,1,25,1,25,1,25,1,25,1,25,1,25,1,26,1,26,1,26,1,26,1,27,1,27,
        1,27,1,27,1,28,1,28,1,28,1,28,1,29,1,29,1,29,1,30,1,30,1,31,1,31,
        1,31,1,32,1,32,1,33,1,33,1,33,1,34,1,34,1,34,1,34,1,34,1,34,1,34,
        1,35,1,35,1,36,3,36,244,8,36,1,36,1,36,1,36,5,36,249,8,36,10,36,
        12,36,252,9,36,1,36,1,36,1,37,3,37,257,8,37,1,37,1,37,1,37,5,37,
        262,8,37,10,37,12,37,265,9,37,1,38,1,38,1,38,1,39,1,39,1,39,1,40,
        1,40,1,40,1,41,1,41,1,41,1,42,4,42,280,8,42,11,42,12,42,281,1,42,
        1,42,1,43,1,43,3,43,288,8,43,1,43,1,43,5,43,292,8,43,10,43,12,43,
        295,9,43,1,43,1,43,1,44,1,44,1,44,1,44,5,44,303,8,44,10,44,12,44,
        306,9,44,1,44,1,44,1,44,1,44,1,44,1,45,1,45,5,45,315,8,45,10,45,
        12,45,318,9,45,1,45,1,45,1,46,1,46,1,46,1,46,1,46,1,47,1,47,1,47,
        1,47,1,47,1,47,1,47,1,48,1,48,1,48,1,48,1,48,1,48,1,48,1,48,1,48,
        1,49,4,49,344,8,49,11,49,12,49,345,1,49,1,49,1,50,3,50,351,8,50,
        1,50,5,50,354,8,50,10,50,12,50,357,9,50,1,50,1,50,4,50,361,8,50,
        11,50,12,50,362,1,51,3,51,366,8,51,1,51,4,51,369,8,51,11,51,12,51,
        370,1,52,3,52,374,8,52,1,52,1,52,5,52,378,8,52,10,52,12,52,381,9,
        52,1,53,1,53,1,53,1,54,1,54,1,54,1,54,1,54,1,54,5,54,392,8,54,10,
        54,12,54,395,9,54,1,55,1,55,1,55,1,56,1,56,1,56,1,56,1,56,1,56,5,
        56,406,8,56,10,56,12,56,409,9,56,1,57,1,57,1,57,1,57,1,57,1,58,1,
        58,1,58,1,58,1,58,5,58,421,8,58,10,58,12,58,424,9,58,1,59,1,59,1,
        59,1,59,1,59,1,60,1,60,1,60,1,60,1,60,5,60,436,8,60,10,60,12,60,
        439,9,60,5,304,393,407,422,437,0,61,1,1,3,2,5,3,7,4,9,5,11,6,13,
        7,15,8,17,9,19,10,21,11,23,12,25,13,27,14,29,15,31,16,33,17,35,18,
        37,19,39,20,41,21,43,22,45,23,47,24,49,25,51,26,53,27,55,28,57,29,
        59,30,61,31,63,32,65,33,67,34,69,35,71,36,73,37,75,38,77,39,79,40,
        81,41,83,42,85,43,87,44,89,45,91,46,93,47,95,48,97,49,99,50,101,
        51,103,52,105,53,107,54,109,55,111,56,113,57,115,58,117,59,119,60,
        121,61,1,0,9,2,0,9,9,32,32,2,0,10,10,13,13,4,0,45,57,65,90,95,95,
        97,122,1,0,48,57,4,0,36,36,38,38,64,64,95,95,2,0,65,90,97,122,5,
        0,45,45,48,57,65,90,95,95,97,122,1,0,34,34,1,0,39,39,464,0,1,1,0,
        0,0,0,3,1,0,0,0,0,5,1,0,0,0,0,7,1,0,0,0,0,9,1,0,0,0,0,11,1,0,0,0,
        0,13,1,0,0,0,0,15,1,0,0,0,0,17,1,0,0,0,0,19,1,0,0,0,0,21,1,0,0,0,
        0,23,1,0,0,0,0,25,1,0,0,0,0,27,1,0,0,0,0,29,1,0,0,0,0,31,1,0,0,0,
        0,33,1,0,0,0,0,35,1,0,0,0,0,37,1,0,0,0,0,39,1,0,0,0,0,41,1,0,0,0,
        0,43,1,0,0,0,0,45,1,0,0,0,0,47,1,0,0,0,0,49,1,0,0,0,0,51,1,0,0,0,
        0,53,1,0,0,0,0,55,1,0,0,0,0,57,1,0,0,0,0,59,1,0,0,0,0,61,1,0,0,0,
        0,63,1,0,0,0,0,65,1,0,0,0,0,67,1,0,0,0,0,69,1,0,0,0,0,71,1,0,0,0,
        0,73,1,0,0,0,0,75,1,0,0,0,0,77,1,0,0,0,0,79,1,0,0,0,0,81,1,0,0,0,
        0,83,1,0,0,0,0,85,1,0,0,0,0,87,1,0,0,0,0,89,1,0,0,0,0,91,1,0,0,0,
        0,93,1,0,0,0,0,95,1,0,0,0,0,97,1,0,0,0,0,99,1,0,0,0,0,101,1,0,0,
        0,0,103,1,0,0,0,0,105,1,0,0,0,0,107,1,0,0,0,0,109,1,0,0,0,0,111,
        1,0,0,0,0,113,1,0,0,0,0,115,1,0,0,0,0,117,1,0,0,0,0,119,1,0,0,0,
        0,121,1,0,0,0,1,123,1,0,0,0,3,125,1,0,0,0,5,127,1,0,0,0,7,129,1,
        0,0,0,9,131,1,0,0,0,11,133,1,0,0,0,13,135,1,0,0,0,15,137,1,0,0,0,
        17,139,1,0,0,0,19,141,1,0,0,0,21,145,1,0,0,0,23,149,1,0,0,0,25,153,
        1,0,0,0,27,158,1,0,0,0,29,163,1,0,0,0,31,168,1,0,0,0,33,171,1,0,
        0,0,35,174,1,0,0,0,37,177,1,0,0,0,39,179,1,0,0,0,41,181,1,0,0,0,
        43,184,1,0,0,0,45,187,1,0,0,0,47,190,1,0,0,0,49,196,1,0,0,0,51,202,
        1,0,0,0,53,208,1,0,0,0,55,212,1,0,0,0,57,216,1,0,0,0,59,220,1,0,
        0,0,61,223,1,0,0,0,63,225,1,0,0,0,65,228,1,0,0,0,67,230,1,0,0,0,
        69,233,1,0,0,0,71,240,1,0,0,0,73,243,1,0,0,0,75,256,1,0,0,0,77,266,
        1,0,0,0,79,269,1,0,0,0,81,272,1,0,0,0,83,275,1,0,0,0,85,279,1,0,
        0,0,87,285,1,0,0,0,89,298,1,0,0,0,91,312,1,0,0,0,93,321,1,0,0,0,
        95,326,1,0,0,0,97,333,1,0,0,0,99,343,1,0,0,0,101,350,1,0,0,0,103,
        365,1,0,0,0,105,373,1,0,0,0,107,382,1,0,0,0,109,385,1,0,0,0,111,
        396,1,0,0,0,113,399,1,0,0,0,115,410,1,0,0,0,117,415,1,0,0,0,119,
        425,1,0,0,0,121,430,1,0,0,0,123,124,5,63,0,0,124,2,1,0,0,0,125,126,
        5,42,0,0,126,4,1,0,0,0,127,128,5,43,0,0,128,6,1,0,0,0,129,130,5,
        44,0,0,130,8,1,0,0,0,131,132,5,123,0,0,132,10,1,0,0,0,133,134,5,
        125,0,0,134,12,1,0,0,0,135,136,5,58,0,0,136,14,1,0,0,0,137,138,5,
        121,0,0,138,16,1,0,0,0,139,140,5,89,0,0,140,18,1,0,0,0,141,142,5,
        121,0,0,142,143,5,101,0,0,143,144,5,115,0,0,144,20,1,0,0,0,145,146,
        5,89,0,0,146,147,5,101,0,0,147,148,5,115,0,0,148,22,1,0,0,0,149,
        150,5,89,0,0,150,151,5,69,0,0,151,152,5,83,0,0,152,24,1,0,0,0,153,
        154,5,116,0,0,154,155,5,114,0,0,155,156,5,117,0,0,156,157,5,101,
        0,0,157,26,1,0,0,0,158,159,5,84,0,0,159,160,5,114,0,0,160,161,5,
        117,0,0,161,162,5,101,0,0,162,28,1,0,0,0,163,164,5,84,0,0,164,165,
        5,82,0,0,165,166,5,85,0,0,166,167,5,69,0,0,167,30,1,0,0,0,168,169,
        5,111,0,0,169,170,5,110,0,0,170,32,1,0,0,0,171,172,5,79,0,0,172,
        173,5,110,0,0,173,34,1,0,0,0,174,175,5,79,0,0,175,176,5,78,0,0,176,
        36,1,0,0,0,177,178,5,110,0,0,178,38,1,0,0,0,179,180,5,78,0,0,180,
        40,1,0,0,0,181,182,5,110,0,0,182,183,5,111,0,0,183,42,1,0,0,0,184,
        185,5,78,0,0,185,186,5,111,0,0,186,44,1,0,0,0,187,188,5,78,0,0,188,
        189,5,79,0,0,189,46,1,0,0,0,190,191,5,102,0,0,191,192,5,97,0,0,192,
        193,5,108,0,0,193,194,5,115,0,0,194,195,5,101,0,0,195,48,1,0,0,0,
        196,197,5,70,0,0,197,198,5,97,0,0,198,199,5,108,0,0,199,200,5,115,
        0,0,200,201,5,101,0,0,201,50,1,0,0,0,202,203,5,70,0,0,203,204,5,
        65,0,0,204,205,5,76,0,0,205,206,5,83,0,0,206,207,5,69,0,0,207,52,
        1,0,0,0,208,209,5,111,0,0,209,210,5,102,0,0,210,211,5,102,0,0,211,
        54,1,0,0,0,212,213,5,79,0,0,213,214,5,102,0,0,214,215,5,102,0,0,
        215,56,1,0,0,0,216,217,5,79,0,0,217,218,5,70,0,0,218,219,5,70,0,
        0,219,58,1,0,0,0,220,221,5,97,0,0,221,222,5,115,0,0,222,60,1,0,0,
        0,223,224,5,61,0,0,224,62,1,0,0,0,225,226,5,45,0,0,226,227,5,62,
        0,0,227,64,1,0,0,0,228,229,5,46,0,0,229,66,1,0,0,0,230,231,5,58,
        0,0,231,232,5,58,0,0,232,68,1,0,0,0,233,234,5,58,0,0,234,235,5,58,
        0,0,235,236,5,105,0,0,236,237,5,116,0,0,237,238,5,101,0,0,238,239,
        5,109,0,0,239,70,1,0,0,0,240,241,5,124,0,0,241,72,1,0,0,0,242,244,
        5,13,0,0,243,242,1,0,0,0,243,244,1,0,0,0,244,245,1,0,0,0,245,246,
        5,10,0,0,246,250,4,36,0,0,247,249,7,0,0,0,248,247,1,0,0,0,249,252,
        1,0,0,0,250,248,1,0,0,0,250,251,1,0,0,0,251,253,1,0,0,0,252,250,
        1,0,0,0,253,254,6,36,0,0,254,74,1,0,0,0,255,257,5,13,0,0,256,255,
        1,0,0,0,256,257,1,0,0,0,257,258,1,0,0,0,258,259,5,10,0,0,259,263,
        4,37,1,0,260,262,7,0,0,0,261,260,1,0,0,0,262,265,1,0,0,0,263,261,
        1,0,0,0,263,264,1,0,0,0,264,76,1,0,0,0,265,263,1,0,0,0,266,267,5,
        40,0,0,267,268,6,38,1,0,268,78,1,0,0,0,269,270,5,41,0,0,270,271,
        6,39,2,0,271,80,1,0,0,0,272,273,5,91,0,0,273,274,6,40,3,0,274,82,
        1,0,0,0,275,276,5,93,0,0,276,277,6,41,4,0,277,84,1,0,0,0,278,280,
        7,0,0,0,279,278,1,0,0,0,280,281,1,0,0,0,281,279,1,0,0,0,281,282,
        1,0,0,0,282,283,1,0,0,0,283,284,6,42,0,0,284,86,1,0,0,0,285,287,
        5,92,0,0,286,288,5,13,0,0,287,286,1,0,0,0,287,288,1,0,0,0,288,289,
        1,0,0,0,289,293,5,10,0,0,290,292,7,0,0,0,291,290,1,0,0,0,292,295,
        1,0,0,0,293,291,1,0,0,0,293,294,1,0,0,0,294,296,1,0,0,0,295,293,
        1,0,0,0,296,297,6,43,0,0,297,88,1,0,0,0,298,299,5,35,0,0,299,300,
        5,47,0,0,300,304,1,0,0,0,301,303,9,0,0,0,302,301,1,0,0,0,303,306,
        1,0,0,0,304,305,1,0,0,0,304,302,1,0,0,0,305,307,1,0,0,0,306,304,
        1,0,0,0,307,308,5,47,0,0,308,309,5,35,0,0,309,310,1,0,0,0,310,311,
        6,44,0,0,311,90,1,0,0,0,312,316,5,35,0,0,313,315,8,1,0,0,314,313,
        1,0,0,0,315,318,1,0,0,0,316,314,1,0,0,0,316,317,1,0,0,0,317,319,
        1,0,0,0,318,316,1,0,0,0,319,320,6,45,0,0,320,92,1,0,0,0,321,322,
        5,112,0,0,322,323,5,97,0,0,323,324,5,115,0,0,324,325,5,115,0,0,325,
        94,1,0,0,0,326,327,5,102,0,0,327,328,5,114,0,0,328,329,5,111,0,0,
        329,330,5,109,0,0,330,331,1,0,0,0,331,332,6,47,5,0,332,96,1,0,0,
        0,333,334,5,105,0,0,334,335,5,109,0,0,335,336,5,112,0,0,336,337,
        5,111,0,0,337,338,5,114,0,0,338,339,5,116,0,0,339,340,1,0,0,0,340,
        341,6,48,6,0,341,98,1,0,0,0,342,344,7,2,0,0,343,342,1,0,0,0,344,
        345,1,0,0,0,345,343,1,0,0,0,345,346,1,0,0,0,346,347,1,0,0,0,347,
        348,4,49,2,0,348,100,1,0,0,0,349,351,5,45,0,0,350,349,1,0,0,0,350,
        351,1,0,0,0,351,355,1,0,0,0,352,354,7,3,0,0,353,352,1,0,0,0,354,
        357,1,0,0,0,355,353,1,0,0,0,355,356,1,0,0,0,356,358,1,0,0,0,357,
        355,1,0,0,0,358,360,5,46,0,0,359,361,7,3,0,0,360,359,1,0,0,0,361,
        362,1,0,0,0,362,360,1,0,0,0,362,363,1,0,0,0,363,102,1,0,0,0,364,
        366,5,45,0,0,365,364,1,0,0,0,365,366,1,0,0,0,366,368,1,0,0,0,367,
        369,7,3,0,0,368,367,1,0,0,0,369,370,1,0,0,0,370,368,1,0,0,0,370,
        371,1,0,0,0,371,104,1,0,0,0,372,374,7,4,0,0,373,372,1,0,0,0,373,
        374,1,0,0,0,374,375,1,0,0,0,375,379,7,5,0,0,376,378,7,6,0,0,377,
        376,1,0,0,0,378,381,1,0,0,0,379,377,1,0,0,0,379,380,1,0,0,0,380,
        106,1,0,0,0,381,379,1,0,0,0,382,383,3,109,54,0,383,384,5,34,0,0,
        384,108,1,0,0,0,385,393,5,34,0,0,386,387,5,92,0,0,387,392,5,34,0,
        0,388,389,5,92,0,0,389,392,5,92,0,0,390,392,8,7,0,0,391,386,1,0,
        0,0,391,388,1,0,0,0,391,390,1,0,0,0,392,395,1,0,0,0,393,394,1,0,
        0,0,393,391,1,0,0,0,394,110,1,0,0,0,395,393,1,0,0,0,396,397,3,113,
        56,0,397,398,5,39,0,0,398,112,1,0,0,0,399,407,5,39,0,0,400,401,5,
        92,0,0,401,406,5,39,0,0,402,403,5,92,0,0,403,406,5,92,0,0,404,406,
        8,8,0,0,405,400,1,0,0,0,405,402,1,0,0,0,405,404,1,0,0,0,406,409,
        1,0,0,0,407,408,1,0,0,0,407,405,1,0,0,0,408,114,1,0,0,0,409,407,
        1,0,0,0,410,411,3,117,58,0,411,412,5,34,0,0,412,413,5,34,0,0,413,
        414,5,34,0,0,414,116,1,0,0,0,415,416,5,34,0,0,416,417,5,34,0,0,417,
        418,5,34,0,0,418,422,1,0,0,0,419,421,9,0,0,0,420,419,1,0,0,0,421,
        424,1,0,0,0,422,423,1,0,0,0,422,420,1,0,0,0,423,118,1,0,0,0,424,
        422,1,0,0,0,425,426,3,121,60,0,426,427,5,39,0,0,427,428,5,39,0,0,
        428,429,5,39,0,0,429,120,1,0,0,0,430,431,5,39,0,0,431,432,5,39,0,
        0,432,433,5,39,0,0,433,437,1,0,0,0,434,436,9,0,0,0,435,434,1,0,0,
        0,436,439,1,0,0,0,437,438,1,0,0,0,437,435,1,0,0,0,438,122,1,0,0,
        0,439,437,1,0,0,0,24,0,243,250,256,263,281,287,293,304,316,345,350,
        355,362,365,370,373,379,391,393,405,407,422,437,7,6,0,0,1,38,0,1,
        39,1,1,40,2,1,41,3,1,47,4,1,48,5
    ]

class SimpleSchemaLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    T__0 = 1
    T__1 = 2
    T__2 = 3
    T__3 = 4
    T__4 = 5
    T__5 = 6
    T__6 = 7
    T__7 = 8
    T__8 = 9
    T__9 = 10
    T__10 = 11
    T__11 = 12
    T__12 = 13
    T__13 = 14
    T__14 = 15
    T__15 = 16
    T__16 = 17
    T__17 = 18
    T__18 = 19
    T__19 = 20
    T__20 = 21
    T__21 = 22
    T__22 = 23
    T__23 = 24
    T__24 = 25
    T__25 = 26
    T__26 = 27
    T__27 = 28
    T__28 = 29
    T__29 = 30
    T__30 = 31
    T__31 = 32
    T__32 = 33
    T__33 = 34
    T__34 = 35
    T__35 = 36
    NESTED_NEWLINE = 37
    NEWLINE = 38
    LPAREN = 39
    RPAREN = 40
    LBRACK = 41
    RBRACK = 42
    HORIZONTAL_WHITESPACE = 43
    LINE_CONTINUATION = 44
    MULTI_LINE_COMMENT = 45
    SINGLE_LINE_COMMENT = 46
    PASS = 47
    INCLUDE_FROM = 48
    INCLUDE_IMPORT = 49
    INCLUDE_FILENAME = 50
    NUMBER = 51
    INTEGER = 52
    IDENTIFIER = 53
    DOUBLE_QUOTE_STRING = 54
    UNTERMINATED_DOUBLE_QUOTE_STRING = 55
    SINGLE_QUOTE_STRING = 56
    UNTERMINATED_SINGLE_QUOTE_STRING = 57
    TRIPLE_DOUBLE_QUOTE_STRING = 58
    UNTERMINATED_TRIPLE_DOUBLE_QUOTE_STRING = 59
    TRIPLE_SINGLE_QUOTE_STRING = 60
    UNTERMINATED_TRIPLE_SINGLE_QUOTE_STRING = 61

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'?'", "'*'", "'+'", "','", "'{'", "'}'", "':'", "'y'", "'Y'", 
            "'yes'", "'Yes'", "'YES'", "'true'", "'True'", "'TRUE'", "'on'", 
            "'On'", "'ON'", "'n'", "'N'", "'no'", "'No'", "'NO'", "'false'", 
            "'False'", "'FALSE'", "'off'", "'Off'", "'OFF'", "'as'", "'='", 
            "'->'", "'.'", "'::'", "'::item'", "'|'", "'('", "')'", "'['", 
            "']'", "'pass'", "'from'", "'import'" ]

    symbolicNames = [ "<INVALID>",
            "NESTED_NEWLINE", "NEWLINE", "LPAREN", "RPAREN", "LBRACK", "RBRACK", 
            "HORIZONTAL_WHITESPACE", "LINE_CONTINUATION", "MULTI_LINE_COMMENT", 
            "SINGLE_LINE_COMMENT", "PASS", "INCLUDE_FROM", "INCLUDE_IMPORT", 
            "INCLUDE_FILENAME", "NUMBER", "INTEGER", "IDENTIFIER", "DOUBLE_QUOTE_STRING", 
            "UNTERMINATED_DOUBLE_QUOTE_STRING", "SINGLE_QUOTE_STRING", "UNTERMINATED_SINGLE_QUOTE_STRING", 
            "TRIPLE_DOUBLE_QUOTE_STRING", "UNTERMINATED_TRIPLE_DOUBLE_QUOTE_STRING", 
            "TRIPLE_SINGLE_QUOTE_STRING", "UNTERMINATED_TRIPLE_SINGLE_QUOTE_STRING" ]

    ruleNames = [ "T__0", "T__1", "T__2", "T__3", "T__4", "T__5", "T__6", 
                  "T__7", "T__8", "T__9", "T__10", "T__11", "T__12", "T__13", 
                  "T__14", "T__15", "T__16", "T__17", "T__18", "T__19", 
                  "T__20", "T__21", "T__22", "T__23", "T__24", "T__25", 
                  "T__26", "T__27", "T__28", "T__29", "T__30", "T__31", 
                  "T__32", "T__33", "T__34", "T__35", "NESTED_NEWLINE", 
                  "NEWLINE", "LPAREN", "RPAREN", "LBRACK", "RBRACK", "HORIZONTAL_WHITESPACE", 
                  "LINE_CONTINUATION", "MULTI_LINE_COMMENT", "SINGLE_LINE_COMMENT", 
                  "PASS", "INCLUDE_FROM", "INCLUDE_IMPORT", "INCLUDE_FILENAME", 
                  "NUMBER", "INTEGER", "IDENTIFIER", "DOUBLE_QUOTE_STRING", 
                  "UNTERMINATED_DOUBLE_QUOTE_STRING", "SINGLE_QUOTE_STRING", 
                  "UNTERMINATED_SINGLE_QUOTE_STRING", "TRIPLE_DOUBLE_QUOTE_STRING", 
                  "UNTERMINATED_TRIPLE_DOUBLE_QUOTE_STRING", "TRIPLE_SINGLE_QUOTE_STRING", 
                  "UNTERMINATED_TRIPLE_SINGLE_QUOTE_STRING" ]

    grammarFileName = "SimpleSchema.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.11.1")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None



    def CustomInitialization(self):
        self._nested_pair_ctr = 0
        self._lexing_include_filename = False

    class SimpleSchemaDenter(DenterHelper):
        def __init__(self, lexer, newline_token, indent_token, dedent_token):
            super().__init__(newline_token, indent_token, dedent_token, should_ignore_eof=False)

            self.lexer: SimpleSchemaLexer = lexer

        def pull_token(self):
            return super(SimpleSchemaLexer, self.lexer).nextToken()

    def nextToken(self):
        if not hasattr(self, "_denter"):
            self._denter = self.__class__.SimpleSchemaDenter(
                self,
                SimpleSchemaParser.NEWLINE,
                SimpleSchemaParser.INDENT,
                SimpleSchemaParser.DEDENT,
            )

        return self._denter.next_token()


    def action(self, localctx:RuleContext, ruleIndex:int, actionIndex:int):
        if self._actions is None:
            actions = dict()
            actions[38] = self.LPAREN_action 
            actions[39] = self.RPAREN_action 
            actions[40] = self.LBRACK_action 
            actions[41] = self.RBRACK_action 
            actions[47] = self.INCLUDE_FROM_action 
            actions[48] = self.INCLUDE_IMPORT_action 
            self._actions = actions
        action = self._actions.get(ruleIndex, None)
        if action is not None:
            action(localctx, actionIndex)
        else:
            raise Exception("No registered action for:" + str(ruleIndex))


    def LPAREN_action(self, localctx:RuleContext , actionIndex:int):
        if actionIndex == 0:
            self._nested_pair_ctr += 1
     

    def RPAREN_action(self, localctx:RuleContext , actionIndex:int):
        if actionIndex == 1:
            self._nested_pair_ctr -= 1
     

    def LBRACK_action(self, localctx:RuleContext , actionIndex:int):
        if actionIndex == 2:
            self._nested_pair_ctr += 1
     

    def RBRACK_action(self, localctx:RuleContext , actionIndex:int):
        if actionIndex == 3:
            self._nested_pair_ctr -= 1
     

    def INCLUDE_FROM_action(self, localctx:RuleContext , actionIndex:int):
        if actionIndex == 4:
            self._lexing_include_filename = True
     

    def INCLUDE_IMPORT_action(self, localctx:RuleContext , actionIndex:int):
        if actionIndex == 5:
            self._lexing_include_filename = False
     

    def sempred(self, localctx:RuleContext, ruleIndex:int, predIndex:int):
        if self._predicates is None:
            preds = dict()
            preds[36] = self.NESTED_NEWLINE_sempred
            preds[37] = self.NEWLINE_sempred
            preds[49] = self.INCLUDE_FILENAME_sempred
            self._predicates = preds
        pred = self._predicates.get(ruleIndex, None)
        if pred is not None:
            return pred(localctx, predIndex)
        else:
            raise Exception("No registered predicate for:" + str(ruleIndex))

    def NESTED_NEWLINE_sempred(self, localctx:RuleContext, predIndex:int):
            if predIndex == 0:
                return self._nested_pair_ctr != 0
         

    def NEWLINE_sempred(self, localctx:RuleContext, predIndex:int):
            if predIndex == 1:
                return self._nested_pair_ctr == 0
         

    def INCLUDE_FILENAME_sempred(self, localctx:RuleContext, predIndex:int):
            if predIndex == 2:
                return self._lexing_include_filename
         


