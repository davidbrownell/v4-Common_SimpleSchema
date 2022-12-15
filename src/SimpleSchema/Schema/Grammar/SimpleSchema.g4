// ----------------------------------------------------------------------
// |
// |  SimpleSchema.g4
// |
// |  David Brownell <db@DavidBrownell.com>
// |      2022-12-08 13:21:12
// |
// ----------------------------------------------------------------------
// |
// |  Copyright David Brownell 2022
// |  Distributed under the Boost Software License, Version 1.0. See
// |  accompanying file LICENSE_1_0.txt or copy at
// |  http://www.boost.org/LICENSE_1_0.txt.
// |
// ----------------------------------------------------------------------
grammar SimpleSchema;

tokens { INDENT, DEDENT }

@lexer::header {

from antlr_denter.DenterHelper import DenterHelper
from SimpleSchemaParser import SimpleSchemaParser

}

@lexer::members {

multiline_statement_ctr = 0

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
}

// ----------------------------------------------------------------------
// |
// |  Lexer Rules
// |
// ----------------------------------------------------------------------
NESTED_NEWLINE:                             '\r'? '\n' { SimpleSchemaLexer.multiline_statement_ctr != 0 }? [ \t]* -> skip;
NEWLINE:                                    '\r'? '\n' { SimpleSchemaLexer.multiline_statement_ctr == 0 }? [ \t]*;

LPAREN:                                     '(' { SimpleSchemaLexer.multiline_statement_ctr += 1 };
RPAREN:                                     ')' { SimpleSchemaLexer.multiline_statement_ctr -= 1 };

HORIZONTAL_WHITESPACE:                      [ \t]+ -> skip;
LINE_CONTINUATION:                          '\\' '\r'? '\n' [ \t]* -> skip;

MULTILINE_COMMENT:                          '#/' .*? '/#' -> skip;
COMMENT:                                    '#' ~[\r\n]* -> skip;

NUMBER:                                     '-'? [0-9]* '.' [0-9]+;
INTEGER:                                    '-'? [0-9]+;
IDENTIFIER:                                 '_'? [a-zA-Z][a-zA-Z_0-9\-.]*;

DOUBLE_QUOTE_STRING:                        UNTERMINATED_DOUBLE_QUOTE_STRING '"';
UNTERMINATED_DOUBLE_QUOTE_STRING:           '"' ('\\"' | '\\\\' | ~'"')*?;

SINGLE_QUOTE_STRING:                        UNTERMINATED_SINGLE_QUOTE_STRING '\'';
UNTERMINATED_SINGLE_QUOTE_STRING:           '\'' ('\\\'' | '\\\\' | ~'\'')*?;

TRIPLE_DOUBLE_QUOTE_STRING:                 UNTERMINATED_TRIPLE_DOUBLE_QUOTE_STRING '"""';
UNTERMINATED_TRIPLE_DOUBLE_QUOTE_STRING:    '"""' .*?;

TRIPLE_SINGLE_QUOTE_STRING:                 UNTERMINATED_TRIPLE_SINGLE_QUOTE_STRING '\'\'\'';
UNTERMINATED_TRIPLE_SINGLE_QUOTE_STRING:    '\'\'\'' .*?;

// ----------------------------------------------------------------------
// |
// |  Parser Rules
// |
// ----------------------------------------------------------------------
// Note that any rule with a '__' suffix represents a non-binding rule (meaning a rule without
// backing code only here for organizational purposes).

// ----------------------------------------------------------------------
// |  Common
identifier:                                 IDENTIFIER;

// ----------------------------------------------------------------------
// |  Expressions
identifier_expression:                      identifier;
number_expression:                          NUMBER;
integer_expression:                         INTEGER;
true_expression:                            'y' | 'Y' | 'yes' | 'Yes' | 'YES' | 'true' | 'True' | 'TRUE' | 'on' | 'On' | 'ON';
false_expression:                           'n' | 'N' | 'no' | 'No' | 'NO' | 'false' | 'False' | 'FALSE' | 'off' | 'Off' | 'OFF';
none_expression:                            'null' | '~';

basic_string_expression:                    DOUBLE_QUOTE_STRING | SINGLE_QUOTE_STRING | UNTERMINATED_DOUBLE_QUOTE_STRING | UNTERMINATED_SINGLE_QUOTE_STRING;
string_expression:                          basic_string_expression | TRIPLE_DOUBLE_QUOTE_STRING | TRIPLE_SINGLE_QUOTE_STRING;

metadata_group_expression:                  '{' (metadata_group_expression_single_line__ | metadata_group_expression_multi_line__) '}';
metadata_group_expression_single_line__:    pass_expression__ | (metadata_expression (',' metadata_expression)* ','?);
metadata_group_expression_multi_line__:     INDENT ((pass_expression__ NEWLINE+) | (metadata_expression NEWLINE+)+) DEDENT;
metadata_expression:                        identifier_expression ':' expression__;

pass_expression__:                          'pass';

expression__:                               integer_expression | number_expression | true_expression | false_expression | none_expression | string_expression | identifier;

// ----------------------------------------------------------------------
// |  Types
identifier_type:                            identifier;
tuple_type:                                 identifier_type (',' identifier_type)* ',';
variant_type:                               identifier_type ('|' identifier_type)* '|' identifier_type;

type__:                                     tuple_type | variant_type | identifier_type;

// ----------------------------------------------------------------------
// |  Statements

// Header Statmeents
header_statement__:                         include_statement;

include_statement:                          'simple_schema_include' basic_string_expression NEWLINE+;

// config_statement:                           'simple_schema_config'; // TODO: Not sure what this does

// Body Statements
body_statement__:                           compound_statement | data_member_statement | extension_statement;

compound_statement:                         identifier (':' type__)? metadata_group_expression? '->' (compound_statement_single_line | compound_statement_multi_line);
compound_statement_single_line:             pass_expression__ NEWLINE+;
compound_statement_multi_line:              INDENT ((pass_expression__ NEWLINE+) | body_statement__+) DEDENT;

data_member_statement:                      identifier_expression ':' type__ metadata_group_expression? NEWLINE+;

extension_statement:                        identifier LPAREN extension_statement_positional_args? extension_statement_keyword_args? RPAREN NEWLINE+;
extension_statement_positional_args:        expression__ (',' expression__)* ','?;
extension_statement_keyword_args:           extension_statement_keyword_arg (',' extension_statement_keyword_arg)* ','?;
extension_statement_keyword_arg:            identifier '=' expression__;

// ----------------------------------------------------------------------
// |  Entry Point
entry_point__:                              header_statement__* body_statement__* EOF;
