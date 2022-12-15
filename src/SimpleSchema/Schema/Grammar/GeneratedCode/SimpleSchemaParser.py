# Generated from C:\Code\v4\Common\SimpleSchema\src\SimpleSchema\Schema\Grammar\SimpleSchema.g4 by ANTLR 4.11.1
# encoding: utf-8
from antlr4 import *
from io import StringIO
import sys
if sys.version_info[1] > 5:
	from typing import TextIO
else:
	from typing.io import TextIO

def serializedATN():
    return [
        4,1,54,283,2,0,7,0,2,1,7,1,2,2,7,2,2,3,7,3,2,4,7,4,2,5,7,5,2,6,7,
        6,2,7,7,7,2,8,7,8,2,9,7,9,2,10,7,10,2,11,7,11,2,12,7,12,2,13,7,13,
        2,14,7,14,2,15,7,15,2,16,7,16,2,17,7,17,2,18,7,18,2,19,7,19,2,20,
        7,20,2,21,7,21,2,22,7,22,2,23,7,23,2,24,7,24,2,25,7,25,2,26,7,26,
        2,27,7,27,2,28,7,28,2,29,7,29,2,30,7,30,1,0,1,0,1,1,1,1,1,2,1,2,
        1,3,1,3,1,4,1,4,1,5,1,5,1,6,1,6,1,7,1,7,1,8,1,8,1,8,3,8,82,8,8,1,
        9,1,9,1,9,3,9,87,8,9,1,9,1,9,1,10,1,10,1,10,1,10,5,10,95,8,10,10,
        10,12,10,98,9,10,1,10,3,10,101,8,10,3,10,103,8,10,1,11,1,11,1,11,
        4,11,108,8,11,11,11,12,11,109,1,11,1,11,4,11,114,8,11,11,11,12,11,
        115,4,11,118,8,11,11,11,12,11,119,3,11,122,8,11,1,11,1,11,1,12,1,
        12,1,12,1,12,1,13,1,13,1,14,1,14,1,14,1,14,1,14,1,14,1,14,3,14,139,
        8,14,1,15,1,15,1,16,1,16,1,16,5,16,146,8,16,10,16,12,16,149,9,16,
        1,16,1,16,1,17,1,17,1,17,5,17,156,8,17,10,17,12,17,159,9,17,1,17,
        1,17,1,17,1,18,1,18,1,18,3,18,167,8,18,1,19,1,19,1,20,1,20,1,20,
        4,20,174,8,20,11,20,12,20,175,1,21,1,21,1,21,3,21,181,8,21,1,22,
        1,22,1,22,3,22,186,8,22,1,22,3,22,189,8,22,1,22,1,22,1,22,3,22,194,
        8,22,1,23,1,23,4,23,198,8,23,11,23,12,23,199,1,24,1,24,1,24,4,24,
        205,8,24,11,24,12,24,206,1,24,4,24,210,8,24,11,24,12,24,211,3,24,
        214,8,24,1,24,1,24,1,25,1,25,1,25,1,25,3,25,222,8,25,1,25,4,25,225,
        8,25,11,25,12,25,226,1,26,1,26,1,26,3,26,232,8,26,1,26,3,26,235,
        8,26,1,26,1,26,4,26,239,8,26,11,26,12,26,240,1,27,1,27,1,27,5,27,
        246,8,27,10,27,12,27,249,9,27,1,27,3,27,252,8,27,1,28,1,28,1,28,
        5,28,257,8,28,10,28,12,28,260,9,28,1,28,3,28,263,8,28,1,29,1,29,
        1,29,1,29,1,30,5,30,270,8,30,10,30,12,30,273,9,30,1,30,5,30,276,
        8,30,10,30,12,30,279,9,30,1,30,1,30,1,30,0,0,31,0,2,4,6,8,10,12,
        14,16,18,20,22,24,26,28,30,32,34,36,38,40,42,44,46,48,50,52,54,56,
        58,60,0,4,1,0,1,11,1,0,12,22,1,0,23,24,1,0,45,48,292,0,62,1,0,0,
        0,2,64,1,0,0,0,4,66,1,0,0,0,6,68,1,0,0,0,8,70,1,0,0,0,10,72,1,0,
        0,0,12,74,1,0,0,0,14,76,1,0,0,0,16,81,1,0,0,0,18,83,1,0,0,0,20,102,
        1,0,0,0,22,104,1,0,0,0,24,125,1,0,0,0,26,129,1,0,0,0,28,138,1,0,
        0,0,30,140,1,0,0,0,32,142,1,0,0,0,34,152,1,0,0,0,36,166,1,0,0,0,
        38,168,1,0,0,0,40,170,1,0,0,0,42,180,1,0,0,0,44,182,1,0,0,0,46,195,
        1,0,0,0,48,201,1,0,0,0,50,217,1,0,0,0,52,228,1,0,0,0,54,242,1,0,
        0,0,56,253,1,0,0,0,58,264,1,0,0,0,60,271,1,0,0,0,62,63,5,44,0,0,
        63,1,1,0,0,0,64,65,3,0,0,0,65,3,1,0,0,0,66,67,5,42,0,0,67,5,1,0,
        0,0,68,69,5,43,0,0,69,7,1,0,0,0,70,71,7,0,0,0,71,9,1,0,0,0,72,73,
        7,1,0,0,73,11,1,0,0,0,74,75,7,2,0,0,75,13,1,0,0,0,76,77,7,3,0,0,
        77,15,1,0,0,0,78,82,3,14,7,0,79,82,5,49,0,0,80,82,5,51,0,0,81,78,
        1,0,0,0,81,79,1,0,0,0,81,80,1,0,0,0,82,17,1,0,0,0,83,86,5,25,0,0,
        84,87,3,20,10,0,85,87,3,22,11,0,86,84,1,0,0,0,86,85,1,0,0,0,87,88,
        1,0,0,0,88,89,5,26,0,0,89,19,1,0,0,0,90,103,3,26,13,0,91,96,3,24,
        12,0,92,93,5,27,0,0,93,95,3,24,12,0,94,92,1,0,0,0,95,98,1,0,0,0,
        96,94,1,0,0,0,96,97,1,0,0,0,97,100,1,0,0,0,98,96,1,0,0,0,99,101,
        5,27,0,0,100,99,1,0,0,0,100,101,1,0,0,0,101,103,1,0,0,0,102,90,1,
        0,0,0,102,91,1,0,0,0,103,21,1,0,0,0,104,121,5,53,0,0,105,107,3,26,
        13,0,106,108,5,35,0,0,107,106,1,0,0,0,108,109,1,0,0,0,109,107,1,
        0,0,0,109,110,1,0,0,0,110,122,1,0,0,0,111,113,3,24,12,0,112,114,
        5,35,0,0,113,112,1,0,0,0,114,115,1,0,0,0,115,113,1,0,0,0,115,116,
        1,0,0,0,116,118,1,0,0,0,117,111,1,0,0,0,118,119,1,0,0,0,119,117,
        1,0,0,0,119,120,1,0,0,0,120,122,1,0,0,0,121,105,1,0,0,0,121,117,
        1,0,0,0,122,123,1,0,0,0,123,124,5,54,0,0,124,23,1,0,0,0,125,126,
        3,2,1,0,126,127,5,28,0,0,127,128,3,28,14,0,128,25,1,0,0,0,129,130,
        5,29,0,0,130,27,1,0,0,0,131,139,3,6,3,0,132,139,3,4,2,0,133,139,
        3,8,4,0,134,139,3,10,5,0,135,139,3,12,6,0,136,139,3,16,8,0,137,139,
        3,0,0,0,138,131,1,0,0,0,138,132,1,0,0,0,138,133,1,0,0,0,138,134,
        1,0,0,0,138,135,1,0,0,0,138,136,1,0,0,0,138,137,1,0,0,0,139,29,1,
        0,0,0,140,141,3,0,0,0,141,31,1,0,0,0,142,147,3,30,15,0,143,144,5,
        27,0,0,144,146,3,30,15,0,145,143,1,0,0,0,146,149,1,0,0,0,147,145,
        1,0,0,0,147,148,1,0,0,0,148,150,1,0,0,0,149,147,1,0,0,0,150,151,
        5,27,0,0,151,33,1,0,0,0,152,157,3,30,15,0,153,154,5,30,0,0,154,156,
        3,30,15,0,155,153,1,0,0,0,156,159,1,0,0,0,157,155,1,0,0,0,157,158,
        1,0,0,0,158,160,1,0,0,0,159,157,1,0,0,0,160,161,5,30,0,0,161,162,
        3,30,15,0,162,35,1,0,0,0,163,167,3,32,16,0,164,167,3,34,17,0,165,
        167,3,30,15,0,166,163,1,0,0,0,166,164,1,0,0,0,166,165,1,0,0,0,167,
        37,1,0,0,0,168,169,3,40,20,0,169,39,1,0,0,0,170,171,5,31,0,0,171,
        173,3,14,7,0,172,174,5,35,0,0,173,172,1,0,0,0,174,175,1,0,0,0,175,
        173,1,0,0,0,175,176,1,0,0,0,176,41,1,0,0,0,177,181,3,44,22,0,178,
        181,3,50,25,0,179,181,3,52,26,0,180,177,1,0,0,0,180,178,1,0,0,0,
        180,179,1,0,0,0,181,43,1,0,0,0,182,185,3,0,0,0,183,184,5,28,0,0,
        184,186,3,36,18,0,185,183,1,0,0,0,185,186,1,0,0,0,186,188,1,0,0,
        0,187,189,3,18,9,0,188,187,1,0,0,0,188,189,1,0,0,0,189,190,1,0,0,
        0,190,193,5,32,0,0,191,194,3,46,23,0,192,194,3,48,24,0,193,191,1,
        0,0,0,193,192,1,0,0,0,194,45,1,0,0,0,195,197,3,26,13,0,196,198,5,
        35,0,0,197,196,1,0,0,0,198,199,1,0,0,0,199,197,1,0,0,0,199,200,1,
        0,0,0,200,47,1,0,0,0,201,213,5,53,0,0,202,204,3,26,13,0,203,205,
        5,35,0,0,204,203,1,0,0,0,205,206,1,0,0,0,206,204,1,0,0,0,206,207,
        1,0,0,0,207,214,1,0,0,0,208,210,3,42,21,0,209,208,1,0,0,0,210,211,
        1,0,0,0,211,209,1,0,0,0,211,212,1,0,0,0,212,214,1,0,0,0,213,202,
        1,0,0,0,213,209,1,0,0,0,214,215,1,0,0,0,215,216,5,54,0,0,216,49,
        1,0,0,0,217,218,3,2,1,0,218,219,5,28,0,0,219,221,3,36,18,0,220,222,
        3,18,9,0,221,220,1,0,0,0,221,222,1,0,0,0,222,224,1,0,0,0,223,225,
        5,35,0,0,224,223,1,0,0,0,225,226,1,0,0,0,226,224,1,0,0,0,226,227,
        1,0,0,0,227,51,1,0,0,0,228,229,3,0,0,0,229,231,5,36,0,0,230,232,
        3,54,27,0,231,230,1,0,0,0,231,232,1,0,0,0,232,234,1,0,0,0,233,235,
        3,56,28,0,234,233,1,0,0,0,234,235,1,0,0,0,235,236,1,0,0,0,236,238,
        5,37,0,0,237,239,5,35,0,0,238,237,1,0,0,0,239,240,1,0,0,0,240,238,
        1,0,0,0,240,241,1,0,0,0,241,53,1,0,0,0,242,247,3,28,14,0,243,244,
        5,27,0,0,244,246,3,28,14,0,245,243,1,0,0,0,246,249,1,0,0,0,247,245,
        1,0,0,0,247,248,1,0,0,0,248,251,1,0,0,0,249,247,1,0,0,0,250,252,
        5,27,0,0,251,250,1,0,0,0,251,252,1,0,0,0,252,55,1,0,0,0,253,258,
        3,58,29,0,254,255,5,27,0,0,255,257,3,58,29,0,256,254,1,0,0,0,257,
        260,1,0,0,0,258,256,1,0,0,0,258,259,1,0,0,0,259,262,1,0,0,0,260,
        258,1,0,0,0,261,263,5,27,0,0,262,261,1,0,0,0,262,263,1,0,0,0,263,
        57,1,0,0,0,264,265,3,0,0,0,265,266,5,33,0,0,266,267,3,28,14,0,267,
        59,1,0,0,0,268,270,3,38,19,0,269,268,1,0,0,0,270,273,1,0,0,0,271,
        269,1,0,0,0,271,272,1,0,0,0,272,277,1,0,0,0,273,271,1,0,0,0,274,
        276,3,42,21,0,275,274,1,0,0,0,276,279,1,0,0,0,277,275,1,0,0,0,277,
        278,1,0,0,0,278,280,1,0,0,0,279,277,1,0,0,0,280,281,5,0,0,1,281,
        61,1,0,0,0,33,81,86,96,100,102,109,115,119,121,138,147,157,166,175,
        180,185,188,193,199,206,211,213,221,226,231,234,240,247,251,258,
        262,271,277
    ]

class SimpleSchemaParser ( Parser ):

    grammarFileName = "SimpleSchema.g4"

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    sharedContextCache = PredictionContextCache()

    literalNames = [ "<INVALID>", "'y'", "'Y'", "'yes'", "'Yes'", "'YES'", 
                     "'true'", "'True'", "'TRUE'", "'on'", "'On'", "'ON'", 
                     "'n'", "'N'", "'no'", "'No'", "'NO'", "'false'", "'False'", 
                     "'FALSE'", "'off'", "'Off'", "'OFF'", "'null'", "'~'", 
                     "'{'", "'}'", "','", "':'", "'pass'", "'|'", "'simple_schema_include'", 
                     "'->'", "'='", "<INVALID>", "<INVALID>", "'('", "')'" ]

    symbolicNames = [ "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "<INVALID>", "<INVALID>", 
                      "<INVALID>", "<INVALID>", "NESTED_NEWLINE", "NEWLINE", 
                      "LPAREN", "RPAREN", "HORIZONTAL_WHITESPACE", "LINE_CONTINUATION", 
                      "MULTILINE_COMMENT", "COMMENT", "NUMBER", "INTEGER", 
                      "IDENTIFIER", "DOUBLE_QUOTE_STRING", "UNTERMINATED_DOUBLE_QUOTE_STRING", 
                      "SINGLE_QUOTE_STRING", "UNTERMINATED_SINGLE_QUOTE_STRING", 
                      "TRIPLE_DOUBLE_QUOTE_STRING", "UNTERMINATED_TRIPLE_DOUBLE_QUOTE_STRING", 
                      "TRIPLE_SINGLE_QUOTE_STRING", "UNTERMINATED_TRIPLE_SINGLE_QUOTE_STRING", 
                      "INDENT", "DEDENT" ]

    RULE_identifier = 0
    RULE_identifier_expression = 1
    RULE_number_expression = 2
    RULE_integer_expression = 3
    RULE_true_expression = 4
    RULE_false_expression = 5
    RULE_none_expression = 6
    RULE_basic_string_expression = 7
    RULE_string_expression = 8
    RULE_metadata_group_expression = 9
    RULE_metadata_group_expression_single_line__ = 10
    RULE_metadata_group_expression_multi_line__ = 11
    RULE_metadata_expression = 12
    RULE_pass_expression__ = 13
    RULE_expression__ = 14
    RULE_identifier_type = 15
    RULE_tuple_type = 16
    RULE_variant_type = 17
    RULE_type__ = 18
    RULE_header_statement__ = 19
    RULE_include_statement = 20
    RULE_body_statement__ = 21
    RULE_compound_statement = 22
    RULE_compound_statement_single_line = 23
    RULE_compound_statement_multi_line = 24
    RULE_data_member_statement = 25
    RULE_extension_statement = 26
    RULE_extension_statement_positional_args = 27
    RULE_extension_statement_keyword_args = 28
    RULE_extension_statement_keyword_arg = 29
    RULE_entry_point__ = 30

    ruleNames =  [ "identifier", "identifier_expression", "number_expression", 
                   "integer_expression", "true_expression", "false_expression", 
                   "none_expression", "basic_string_expression", "string_expression", 
                   "metadata_group_expression", "metadata_group_expression_single_line__", 
                   "metadata_group_expression_multi_line__", "metadata_expression", 
                   "pass_expression__", "expression__", "identifier_type", 
                   "tuple_type", "variant_type", "type__", "header_statement__", 
                   "include_statement", "body_statement__", "compound_statement", 
                   "compound_statement_single_line", "compound_statement_multi_line", 
                   "data_member_statement", "extension_statement", "extension_statement_positional_args", 
                   "extension_statement_keyword_args", "extension_statement_keyword_arg", 
                   "entry_point__" ]

    EOF = Token.EOF
    T__0=1
    T__1=2
    T__2=3
    T__3=4
    T__4=5
    T__5=6
    T__6=7
    T__7=8
    T__8=9
    T__9=10
    T__10=11
    T__11=12
    T__12=13
    T__13=14
    T__14=15
    T__15=16
    T__16=17
    T__17=18
    T__18=19
    T__19=20
    T__20=21
    T__21=22
    T__22=23
    T__23=24
    T__24=25
    T__25=26
    T__26=27
    T__27=28
    T__28=29
    T__29=30
    T__30=31
    T__31=32
    T__32=33
    NESTED_NEWLINE=34
    NEWLINE=35
    LPAREN=36
    RPAREN=37
    HORIZONTAL_WHITESPACE=38
    LINE_CONTINUATION=39
    MULTILINE_COMMENT=40
    COMMENT=41
    NUMBER=42
    INTEGER=43
    IDENTIFIER=44
    DOUBLE_QUOTE_STRING=45
    UNTERMINATED_DOUBLE_QUOTE_STRING=46
    SINGLE_QUOTE_STRING=47
    UNTERMINATED_SINGLE_QUOTE_STRING=48
    TRIPLE_DOUBLE_QUOTE_STRING=49
    UNTERMINATED_TRIPLE_DOUBLE_QUOTE_STRING=50
    TRIPLE_SINGLE_QUOTE_STRING=51
    UNTERMINATED_TRIPLE_SINGLE_QUOTE_STRING=52
    INDENT=53
    DEDENT=54

    def __init__(self, input:TokenStream, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.11.1")
        self._interp = ParserATNSimulator(self, self.atn, self.decisionsToDFA, self.sharedContextCache)
        self._predicates = None




    class IdentifierContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def IDENTIFIER(self):
            return self.getToken(SimpleSchemaParser.IDENTIFIER, 0)

        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_identifier

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIdentifier" ):
                return visitor.visitIdentifier(self)
            else:
                return visitor.visitChildren(self)




    def identifier(self):

        localctx = SimpleSchemaParser.IdentifierContext(self, self._ctx, self.state)
        self.enterRule(localctx, 0, self.RULE_identifier)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 62
            self.match(SimpleSchemaParser.IDENTIFIER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Identifier_expressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(SimpleSchemaParser.IdentifierContext,0)


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_identifier_expression

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIdentifier_expression" ):
                return visitor.visitIdentifier_expression(self)
            else:
                return visitor.visitChildren(self)




    def identifier_expression(self):

        localctx = SimpleSchemaParser.Identifier_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 2, self.RULE_identifier_expression)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 64
            self.identifier()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Number_expressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def NUMBER(self):
            return self.getToken(SimpleSchemaParser.NUMBER, 0)

        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_number_expression

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNumber_expression" ):
                return visitor.visitNumber_expression(self)
            else:
                return visitor.visitChildren(self)




    def number_expression(self):

        localctx = SimpleSchemaParser.Number_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 4, self.RULE_number_expression)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 66
            self.match(SimpleSchemaParser.NUMBER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Integer_expressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INTEGER(self):
            return self.getToken(SimpleSchemaParser.INTEGER, 0)

        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_integer_expression

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitInteger_expression" ):
                return visitor.visitInteger_expression(self)
            else:
                return visitor.visitChildren(self)




    def integer_expression(self):

        localctx = SimpleSchemaParser.Integer_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 6, self.RULE_integer_expression)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 68
            self.match(SimpleSchemaParser.INTEGER)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class True_expressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_true_expression

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTrue_expression" ):
                return visitor.visitTrue_expression(self)
            else:
                return visitor.visitChildren(self)




    def true_expression(self):

        localctx = SimpleSchemaParser.True_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 8, self.RULE_true_expression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 70
            _la = self._input.LA(1)
            if not(((_la) & ~0x3f) == 0 and ((1 << _la) & 4094) != 0):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class False_expressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_false_expression

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitFalse_expression" ):
                return visitor.visitFalse_expression(self)
            else:
                return visitor.visitChildren(self)




    def false_expression(self):

        localctx = SimpleSchemaParser.False_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 10, self.RULE_false_expression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 72
            _la = self._input.LA(1)
            if not(((_la) & ~0x3f) == 0 and ((1 << _la) & 8384512) != 0):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class None_expressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_none_expression

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitNone_expression" ):
                return visitor.visitNone_expression(self)
            else:
                return visitor.visitChildren(self)




    def none_expression(self):

        localctx = SimpleSchemaParser.None_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 12, self.RULE_none_expression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 74
            _la = self._input.LA(1)
            if not(_la==23 or _la==24):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Basic_string_expressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def DOUBLE_QUOTE_STRING(self):
            return self.getToken(SimpleSchemaParser.DOUBLE_QUOTE_STRING, 0)

        def SINGLE_QUOTE_STRING(self):
            return self.getToken(SimpleSchemaParser.SINGLE_QUOTE_STRING, 0)

        def UNTERMINATED_DOUBLE_QUOTE_STRING(self):
            return self.getToken(SimpleSchemaParser.UNTERMINATED_DOUBLE_QUOTE_STRING, 0)

        def UNTERMINATED_SINGLE_QUOTE_STRING(self):
            return self.getToken(SimpleSchemaParser.UNTERMINATED_SINGLE_QUOTE_STRING, 0)

        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_basic_string_expression

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBasic_string_expression" ):
                return visitor.visitBasic_string_expression(self)
            else:
                return visitor.visitChildren(self)




    def basic_string_expression(self):

        localctx = SimpleSchemaParser.Basic_string_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 14, self.RULE_basic_string_expression)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 76
            _la = self._input.LA(1)
            if not(((_la) & ~0x3f) == 0 and ((1 << _la) & 527765581332480) != 0):
                self._errHandler.recoverInline(self)
            else:
                self._errHandler.reportMatch(self)
                self.consume()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class String_expressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def basic_string_expression(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Basic_string_expressionContext,0)


        def TRIPLE_DOUBLE_QUOTE_STRING(self):
            return self.getToken(SimpleSchemaParser.TRIPLE_DOUBLE_QUOTE_STRING, 0)

        def TRIPLE_SINGLE_QUOTE_STRING(self):
            return self.getToken(SimpleSchemaParser.TRIPLE_SINGLE_QUOTE_STRING, 0)

        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_string_expression

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitString_expression" ):
                return visitor.visitString_expression(self)
            else:
                return visitor.visitChildren(self)




    def string_expression(self):

        localctx = SimpleSchemaParser.String_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 16, self.RULE_string_expression)
        try:
            self.state = 81
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [45, 46, 47, 48]:
                self.enterOuterAlt(localctx, 1)
                self.state = 78
                self.basic_string_expression()
                pass
            elif token in [49]:
                self.enterOuterAlt(localctx, 2)
                self.state = 79
                self.match(SimpleSchemaParser.TRIPLE_DOUBLE_QUOTE_STRING)
                pass
            elif token in [51]:
                self.enterOuterAlt(localctx, 3)
                self.state = 80
                self.match(SimpleSchemaParser.TRIPLE_SINGLE_QUOTE_STRING)
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Metadata_group_expressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def metadata_group_expression_single_line__(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Metadata_group_expression_single_line__Context,0)


        def metadata_group_expression_multi_line__(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Metadata_group_expression_multi_line__Context,0)


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_metadata_group_expression

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMetadata_group_expression" ):
                return visitor.visitMetadata_group_expression(self)
            else:
                return visitor.visitChildren(self)




    def metadata_group_expression(self):

        localctx = SimpleSchemaParser.Metadata_group_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 18, self.RULE_metadata_group_expression)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 83
            self.match(SimpleSchemaParser.T__24)
            self.state = 86
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [29, 44]:
                self.state = 84
                self.metadata_group_expression_single_line__()
                pass
            elif token in [53]:
                self.state = 85
                self.metadata_group_expression_multi_line__()
                pass
            else:
                raise NoViableAltException(self)

            self.state = 88
            self.match(SimpleSchemaParser.T__25)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Metadata_group_expression_single_line__Context(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def pass_expression__(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Pass_expression__Context,0)


        def metadata_expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SimpleSchemaParser.Metadata_expressionContext)
            else:
                return self.getTypedRuleContext(SimpleSchemaParser.Metadata_expressionContext,i)


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_metadata_group_expression_single_line__

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMetadata_group_expression_single_line__" ):
                return visitor.visitMetadata_group_expression_single_line__(self)
            else:
                return visitor.visitChildren(self)




    def metadata_group_expression_single_line__(self):

        localctx = SimpleSchemaParser.Metadata_group_expression_single_line__Context(self, self._ctx, self.state)
        self.enterRule(localctx, 20, self.RULE_metadata_group_expression_single_line__)
        self._la = 0 # Token type
        try:
            self.state = 102
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [29]:
                self.enterOuterAlt(localctx, 1)
                self.state = 90
                self.pass_expression__()
                pass
            elif token in [44]:
                self.enterOuterAlt(localctx, 2)
                self.state = 91
                self.metadata_expression()
                self.state = 96
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,2,self._ctx)
                while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                    if _alt==1:
                        self.state = 92
                        self.match(SimpleSchemaParser.T__26)
                        self.state = 93
                        self.metadata_expression() 
                    self.state = 98
                    self._errHandler.sync(self)
                    _alt = self._interp.adaptivePredict(self._input,2,self._ctx)

                self.state = 100
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if _la==27:
                    self.state = 99
                    self.match(SimpleSchemaParser.T__26)


                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Metadata_group_expression_multi_line__Context(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INDENT(self):
            return self.getToken(SimpleSchemaParser.INDENT, 0)

        def DEDENT(self):
            return self.getToken(SimpleSchemaParser.DEDENT, 0)

        def pass_expression__(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Pass_expression__Context,0)


        def metadata_expression(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SimpleSchemaParser.Metadata_expressionContext)
            else:
                return self.getTypedRuleContext(SimpleSchemaParser.Metadata_expressionContext,i)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(SimpleSchemaParser.NEWLINE)
            else:
                return self.getToken(SimpleSchemaParser.NEWLINE, i)

        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_metadata_group_expression_multi_line__

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMetadata_group_expression_multi_line__" ):
                return visitor.visitMetadata_group_expression_multi_line__(self)
            else:
                return visitor.visitChildren(self)




    def metadata_group_expression_multi_line__(self):

        localctx = SimpleSchemaParser.Metadata_group_expression_multi_line__Context(self, self._ctx, self.state)
        self.enterRule(localctx, 22, self.RULE_metadata_group_expression_multi_line__)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 104
            self.match(SimpleSchemaParser.INDENT)
            self.state = 121
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [29]:
                self.state = 105
                self.pass_expression__()
                self.state = 107 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 106
                    self.match(SimpleSchemaParser.NEWLINE)
                    self.state = 109 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==35):
                        break

                pass
            elif token in [44]:
                self.state = 117 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 111
                    self.metadata_expression()
                    self.state = 113 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    while True:
                        self.state = 112
                        self.match(SimpleSchemaParser.NEWLINE)
                        self.state = 115 
                        self._errHandler.sync(self)
                        _la = self._input.LA(1)
                        if not (_la==35):
                            break

                    self.state = 119 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==44):
                        break

                pass
            else:
                raise NoViableAltException(self)

            self.state = 123
            self.match(SimpleSchemaParser.DEDENT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Metadata_expressionContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier_expression(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Identifier_expressionContext,0)


        def expression__(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Expression__Context,0)


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_metadata_expression

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitMetadata_expression" ):
                return visitor.visitMetadata_expression(self)
            else:
                return visitor.visitChildren(self)




    def metadata_expression(self):

        localctx = SimpleSchemaParser.Metadata_expressionContext(self, self._ctx, self.state)
        self.enterRule(localctx, 24, self.RULE_metadata_expression)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 125
            self.identifier_expression()
            self.state = 126
            self.match(SimpleSchemaParser.T__27)
            self.state = 127
            self.expression__()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Pass_expression__Context(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_pass_expression__

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitPass_expression__" ):
                return visitor.visitPass_expression__(self)
            else:
                return visitor.visitChildren(self)




    def pass_expression__(self):

        localctx = SimpleSchemaParser.Pass_expression__Context(self, self._ctx, self.state)
        self.enterRule(localctx, 26, self.RULE_pass_expression__)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 129
            self.match(SimpleSchemaParser.T__28)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Expression__Context(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def integer_expression(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Integer_expressionContext,0)


        def number_expression(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Number_expressionContext,0)


        def true_expression(self):
            return self.getTypedRuleContext(SimpleSchemaParser.True_expressionContext,0)


        def false_expression(self):
            return self.getTypedRuleContext(SimpleSchemaParser.False_expressionContext,0)


        def none_expression(self):
            return self.getTypedRuleContext(SimpleSchemaParser.None_expressionContext,0)


        def string_expression(self):
            return self.getTypedRuleContext(SimpleSchemaParser.String_expressionContext,0)


        def identifier(self):
            return self.getTypedRuleContext(SimpleSchemaParser.IdentifierContext,0)


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_expression__

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExpression__" ):
                return visitor.visitExpression__(self)
            else:
                return visitor.visitChildren(self)




    def expression__(self):

        localctx = SimpleSchemaParser.Expression__Context(self, self._ctx, self.state)
        self.enterRule(localctx, 28, self.RULE_expression__)
        try:
            self.state = 138
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [43]:
                self.enterOuterAlt(localctx, 1)
                self.state = 131
                self.integer_expression()
                pass
            elif token in [42]:
                self.enterOuterAlt(localctx, 2)
                self.state = 132
                self.number_expression()
                pass
            elif token in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]:
                self.enterOuterAlt(localctx, 3)
                self.state = 133
                self.true_expression()
                pass
            elif token in [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22]:
                self.enterOuterAlt(localctx, 4)
                self.state = 134
                self.false_expression()
                pass
            elif token in [23, 24]:
                self.enterOuterAlt(localctx, 5)
                self.state = 135
                self.none_expression()
                pass
            elif token in [45, 46, 47, 48, 49, 51]:
                self.enterOuterAlt(localctx, 6)
                self.state = 136
                self.string_expression()
                pass
            elif token in [44]:
                self.enterOuterAlt(localctx, 7)
                self.state = 137
                self.identifier()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Identifier_typeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(SimpleSchemaParser.IdentifierContext,0)


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_identifier_type

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitIdentifier_type" ):
                return visitor.visitIdentifier_type(self)
            else:
                return visitor.visitChildren(self)




    def identifier_type(self):

        localctx = SimpleSchemaParser.Identifier_typeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 30, self.RULE_identifier_type)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 140
            self.identifier()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Tuple_typeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier_type(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SimpleSchemaParser.Identifier_typeContext)
            else:
                return self.getTypedRuleContext(SimpleSchemaParser.Identifier_typeContext,i)


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_tuple_type

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitTuple_type" ):
                return visitor.visitTuple_type(self)
            else:
                return visitor.visitChildren(self)




    def tuple_type(self):

        localctx = SimpleSchemaParser.Tuple_typeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 32, self.RULE_tuple_type)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 142
            self.identifier_type()
            self.state = 147
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,10,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 143
                    self.match(SimpleSchemaParser.T__26)
                    self.state = 144
                    self.identifier_type() 
                self.state = 149
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,10,self._ctx)

            self.state = 150
            self.match(SimpleSchemaParser.T__26)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Variant_typeContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier_type(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SimpleSchemaParser.Identifier_typeContext)
            else:
                return self.getTypedRuleContext(SimpleSchemaParser.Identifier_typeContext,i)


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_variant_type

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitVariant_type" ):
                return visitor.visitVariant_type(self)
            else:
                return visitor.visitChildren(self)




    def variant_type(self):

        localctx = SimpleSchemaParser.Variant_typeContext(self, self._ctx, self.state)
        self.enterRule(localctx, 34, self.RULE_variant_type)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 152
            self.identifier_type()
            self.state = 157
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,11,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 153
                    self.match(SimpleSchemaParser.T__29)
                    self.state = 154
                    self.identifier_type() 
                self.state = 159
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,11,self._ctx)

            self.state = 160
            self.match(SimpleSchemaParser.T__29)
            self.state = 161
            self.identifier_type()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Type__Context(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def tuple_type(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Tuple_typeContext,0)


        def variant_type(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Variant_typeContext,0)


        def identifier_type(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Identifier_typeContext,0)


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_type__

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitType__" ):
                return visitor.visitType__(self)
            else:
                return visitor.visitChildren(self)




    def type__(self):

        localctx = SimpleSchemaParser.Type__Context(self, self._ctx, self.state)
        self.enterRule(localctx, 36, self.RULE_type__)
        try:
            self.state = 166
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,12,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 163
                self.tuple_type()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 164
                self.variant_type()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 165
                self.identifier_type()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Header_statement__Context(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def include_statement(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Include_statementContext,0)


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_header_statement__

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitHeader_statement__" ):
                return visitor.visitHeader_statement__(self)
            else:
                return visitor.visitChildren(self)




    def header_statement__(self):

        localctx = SimpleSchemaParser.Header_statement__Context(self, self._ctx, self.state)
        self.enterRule(localctx, 38, self.RULE_header_statement__)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 168
            self.include_statement()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Include_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def basic_string_expression(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Basic_string_expressionContext,0)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(SimpleSchemaParser.NEWLINE)
            else:
                return self.getToken(SimpleSchemaParser.NEWLINE, i)

        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_include_statement

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitInclude_statement" ):
                return visitor.visitInclude_statement(self)
            else:
                return visitor.visitChildren(self)




    def include_statement(self):

        localctx = SimpleSchemaParser.Include_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 40, self.RULE_include_statement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 170
            self.match(SimpleSchemaParser.T__30)
            self.state = 171
            self.basic_string_expression()
            self.state = 173 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 172
                self.match(SimpleSchemaParser.NEWLINE)
                self.state = 175 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==35):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Body_statement__Context(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def compound_statement(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Compound_statementContext,0)


        def data_member_statement(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Data_member_statementContext,0)


        def extension_statement(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Extension_statementContext,0)


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_body_statement__

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitBody_statement__" ):
                return visitor.visitBody_statement__(self)
            else:
                return visitor.visitChildren(self)




    def body_statement__(self):

        localctx = SimpleSchemaParser.Body_statement__Context(self, self._ctx, self.state)
        self.enterRule(localctx, 42, self.RULE_body_statement__)
        try:
            self.state = 180
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,14,self._ctx)
            if la_ == 1:
                self.enterOuterAlt(localctx, 1)
                self.state = 177
                self.compound_statement()
                pass

            elif la_ == 2:
                self.enterOuterAlt(localctx, 2)
                self.state = 178
                self.data_member_statement()
                pass

            elif la_ == 3:
                self.enterOuterAlt(localctx, 3)
                self.state = 179
                self.extension_statement()
                pass


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Compound_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(SimpleSchemaParser.IdentifierContext,0)


        def compound_statement_single_line(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Compound_statement_single_lineContext,0)


        def compound_statement_multi_line(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Compound_statement_multi_lineContext,0)


        def type__(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Type__Context,0)


        def metadata_group_expression(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Metadata_group_expressionContext,0)


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_compound_statement

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCompound_statement" ):
                return visitor.visitCompound_statement(self)
            else:
                return visitor.visitChildren(self)




    def compound_statement(self):

        localctx = SimpleSchemaParser.Compound_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 44, self.RULE_compound_statement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 182
            self.identifier()
            self.state = 185
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==28:
                self.state = 183
                self.match(SimpleSchemaParser.T__27)
                self.state = 184
                self.type__()


            self.state = 188
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==25:
                self.state = 187
                self.metadata_group_expression()


            self.state = 190
            self.match(SimpleSchemaParser.T__31)
            self.state = 193
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [29]:
                self.state = 191
                self.compound_statement_single_line()
                pass
            elif token in [53]:
                self.state = 192
                self.compound_statement_multi_line()
                pass
            else:
                raise NoViableAltException(self)

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Compound_statement_single_lineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def pass_expression__(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Pass_expression__Context,0)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(SimpleSchemaParser.NEWLINE)
            else:
                return self.getToken(SimpleSchemaParser.NEWLINE, i)

        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_compound_statement_single_line

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCompound_statement_single_line" ):
                return visitor.visitCompound_statement_single_line(self)
            else:
                return visitor.visitChildren(self)




    def compound_statement_single_line(self):

        localctx = SimpleSchemaParser.Compound_statement_single_lineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 46, self.RULE_compound_statement_single_line)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 195
            self.pass_expression__()
            self.state = 197 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 196
                self.match(SimpleSchemaParser.NEWLINE)
                self.state = 199 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==35):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Compound_statement_multi_lineContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def INDENT(self):
            return self.getToken(SimpleSchemaParser.INDENT, 0)

        def DEDENT(self):
            return self.getToken(SimpleSchemaParser.DEDENT, 0)

        def pass_expression__(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Pass_expression__Context,0)


        def body_statement__(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SimpleSchemaParser.Body_statement__Context)
            else:
                return self.getTypedRuleContext(SimpleSchemaParser.Body_statement__Context,i)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(SimpleSchemaParser.NEWLINE)
            else:
                return self.getToken(SimpleSchemaParser.NEWLINE, i)

        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_compound_statement_multi_line

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitCompound_statement_multi_line" ):
                return visitor.visitCompound_statement_multi_line(self)
            else:
                return visitor.visitChildren(self)




    def compound_statement_multi_line(self):

        localctx = SimpleSchemaParser.Compound_statement_multi_lineContext(self, self._ctx, self.state)
        self.enterRule(localctx, 48, self.RULE_compound_statement_multi_line)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 201
            self.match(SimpleSchemaParser.INDENT)
            self.state = 213
            self._errHandler.sync(self)
            token = self._input.LA(1)
            if token in [29]:
                self.state = 202
                self.pass_expression__()
                self.state = 204 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 203
                    self.match(SimpleSchemaParser.NEWLINE)
                    self.state = 206 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==35):
                        break

                pass
            elif token in [44]:
                self.state = 209 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                while True:
                    self.state = 208
                    self.body_statement__()
                    self.state = 211 
                    self._errHandler.sync(self)
                    _la = self._input.LA(1)
                    if not (_la==44):
                        break

                pass
            else:
                raise NoViableAltException(self)

            self.state = 215
            self.match(SimpleSchemaParser.DEDENT)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Data_member_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier_expression(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Identifier_expressionContext,0)


        def type__(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Type__Context,0)


        def metadata_group_expression(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Metadata_group_expressionContext,0)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(SimpleSchemaParser.NEWLINE)
            else:
                return self.getToken(SimpleSchemaParser.NEWLINE, i)

        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_data_member_statement

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitData_member_statement" ):
                return visitor.visitData_member_statement(self)
            else:
                return visitor.visitChildren(self)




    def data_member_statement(self):

        localctx = SimpleSchemaParser.Data_member_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 50, self.RULE_data_member_statement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 217
            self.identifier_expression()
            self.state = 218
            self.match(SimpleSchemaParser.T__27)
            self.state = 219
            self.type__()
            self.state = 221
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==25:
                self.state = 220
                self.metadata_group_expression()


            self.state = 224 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 223
                self.match(SimpleSchemaParser.NEWLINE)
                self.state = 226 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==35):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Extension_statementContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(SimpleSchemaParser.IdentifierContext,0)


        def LPAREN(self):
            return self.getToken(SimpleSchemaParser.LPAREN, 0)

        def RPAREN(self):
            return self.getToken(SimpleSchemaParser.RPAREN, 0)

        def extension_statement_positional_args(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Extension_statement_positional_argsContext,0)


        def extension_statement_keyword_args(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Extension_statement_keyword_argsContext,0)


        def NEWLINE(self, i:int=None):
            if i is None:
                return self.getTokens(SimpleSchemaParser.NEWLINE)
            else:
                return self.getToken(SimpleSchemaParser.NEWLINE, i)

        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_extension_statement

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExtension_statement" ):
                return visitor.visitExtension_statement(self)
            else:
                return visitor.visitChildren(self)




    def extension_statement(self):

        localctx = SimpleSchemaParser.Extension_statementContext(self, self._ctx, self.state)
        self.enterRule(localctx, 52, self.RULE_extension_statement)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 228
            self.identifier()
            self.state = 229
            self.match(SimpleSchemaParser.LPAREN)
            self.state = 231
            self._errHandler.sync(self)
            la_ = self._interp.adaptivePredict(self._input,24,self._ctx)
            if la_ == 1:
                self.state = 230
                self.extension_statement_positional_args()


            self.state = 234
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==44:
                self.state = 233
                self.extension_statement_keyword_args()


            self.state = 236
            self.match(SimpleSchemaParser.RPAREN)
            self.state = 238 
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while True:
                self.state = 237
                self.match(SimpleSchemaParser.NEWLINE)
                self.state = 240 
                self._errHandler.sync(self)
                _la = self._input.LA(1)
                if not (_la==35):
                    break

        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Extension_statement_positional_argsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def expression__(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SimpleSchemaParser.Expression__Context)
            else:
                return self.getTypedRuleContext(SimpleSchemaParser.Expression__Context,i)


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_extension_statement_positional_args

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExtension_statement_positional_args" ):
                return visitor.visitExtension_statement_positional_args(self)
            else:
                return visitor.visitChildren(self)




    def extension_statement_positional_args(self):

        localctx = SimpleSchemaParser.Extension_statement_positional_argsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 54, self.RULE_extension_statement_positional_args)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 242
            self.expression__()
            self.state = 247
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,27,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 243
                    self.match(SimpleSchemaParser.T__26)
                    self.state = 244
                    self.expression__() 
                self.state = 249
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,27,self._ctx)

            self.state = 251
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==27:
                self.state = 250
                self.match(SimpleSchemaParser.T__26)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Extension_statement_keyword_argsContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def extension_statement_keyword_arg(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SimpleSchemaParser.Extension_statement_keyword_argContext)
            else:
                return self.getTypedRuleContext(SimpleSchemaParser.Extension_statement_keyword_argContext,i)


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_extension_statement_keyword_args

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExtension_statement_keyword_args" ):
                return visitor.visitExtension_statement_keyword_args(self)
            else:
                return visitor.visitChildren(self)




    def extension_statement_keyword_args(self):

        localctx = SimpleSchemaParser.Extension_statement_keyword_argsContext(self, self._ctx, self.state)
        self.enterRule(localctx, 56, self.RULE_extension_statement_keyword_args)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 253
            self.extension_statement_keyword_arg()
            self.state = 258
            self._errHandler.sync(self)
            _alt = self._interp.adaptivePredict(self._input,29,self._ctx)
            while _alt!=2 and _alt!=ATN.INVALID_ALT_NUMBER:
                if _alt==1:
                    self.state = 254
                    self.match(SimpleSchemaParser.T__26)
                    self.state = 255
                    self.extension_statement_keyword_arg() 
                self.state = 260
                self._errHandler.sync(self)
                _alt = self._interp.adaptivePredict(self._input,29,self._ctx)

            self.state = 262
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            if _la==27:
                self.state = 261
                self.match(SimpleSchemaParser.T__26)


        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Extension_statement_keyword_argContext(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def identifier(self):
            return self.getTypedRuleContext(SimpleSchemaParser.IdentifierContext,0)


        def expression__(self):
            return self.getTypedRuleContext(SimpleSchemaParser.Expression__Context,0)


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_extension_statement_keyword_arg

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitExtension_statement_keyword_arg" ):
                return visitor.visitExtension_statement_keyword_arg(self)
            else:
                return visitor.visitChildren(self)




    def extension_statement_keyword_arg(self):

        localctx = SimpleSchemaParser.Extension_statement_keyword_argContext(self, self._ctx, self.state)
        self.enterRule(localctx, 58, self.RULE_extension_statement_keyword_arg)
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 264
            self.identifier()
            self.state = 265
            self.match(SimpleSchemaParser.T__32)
            self.state = 266
            self.expression__()
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx


    class Entry_point__Context(ParserRuleContext):
        __slots__ = 'parser'

        def __init__(self, parser, parent:ParserRuleContext=None, invokingState:int=-1):
            super().__init__(parent, invokingState)
            self.parser = parser

        def EOF(self):
            return self.getToken(SimpleSchemaParser.EOF, 0)

        def header_statement__(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SimpleSchemaParser.Header_statement__Context)
            else:
                return self.getTypedRuleContext(SimpleSchemaParser.Header_statement__Context,i)


        def body_statement__(self, i:int=None):
            if i is None:
                return self.getTypedRuleContexts(SimpleSchemaParser.Body_statement__Context)
            else:
                return self.getTypedRuleContext(SimpleSchemaParser.Body_statement__Context,i)


        def getRuleIndex(self):
            return SimpleSchemaParser.RULE_entry_point__

        def accept(self, visitor:ParseTreeVisitor):
            if hasattr( visitor, "visitEntry_point__" ):
                return visitor.visitEntry_point__(self)
            else:
                return visitor.visitChildren(self)




    def entry_point__(self):

        localctx = SimpleSchemaParser.Entry_point__Context(self, self._ctx, self.state)
        self.enterRule(localctx, 60, self.RULE_entry_point__)
        self._la = 0 # Token type
        try:
            self.enterOuterAlt(localctx, 1)
            self.state = 271
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==31:
                self.state = 268
                self.header_statement__()
                self.state = 273
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 277
            self._errHandler.sync(self)
            _la = self._input.LA(1)
            while _la==44:
                self.state = 274
                self.body_statement__()
                self.state = 279
                self._errHandler.sync(self)
                _la = self._input.LA(1)

            self.state = 280
            self.match(SimpleSchemaParser.EOF)
        except RecognitionException as re:
            localctx.exception = re
            self._errHandler.reportError(self, re)
            self._errHandler.recover(self, re)
        finally:
            self.exitRule()
        return localctx





