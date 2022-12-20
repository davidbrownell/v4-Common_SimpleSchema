// ----------------------------------------------------------------------
// |
// |  SimpleSchema.g4
// |
// |  David Brownell <db@DavidBrownell.com>
// |      2022-12-16 08:00:02
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

// ----------------------------------------------------------------------
tokens { INDENT, DEDENT }

@lexer::header {

from antlr_denter.DenterHelper import DenterHelper
from SimpleSchemaParser import SimpleSchemaParser

}

@lexer::members {

nested_pair_ctr = 0

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

// Newlines nested within paired brackets where newlines are considered to be unimportant.
NESTED_NEWLINE:                             '\r'? '\n' { SimpleSchemaLexer.nested_pair_ctr != 0 }? [ \t]* -> skip;

// Standard newlines
NEWLINE:                                    '\r'? '\n' { SimpleSchemaLexer.nested_pair_ctr == 0 }? [ \t]*;

LPAREN:                                     '(' { SimpleSchemaLexer.nested_pair_ctr += 1 };
RPAREN:                                     ')' { SimpleSchemaLexer.nested_pair_ctr -= 1 };
LBRACK:                                     '[' { SimpleSchemaLexer.nested_pair_ctr += 1 };
RBRACK:                                     ']' { SimpleSchemaLexer.nested_pair_ctr -= 1 };

HORIZONTAL_WHITESPACE:                      [ \t]+ -> skip;
LINE_CONTINUATION:                          '\\' '\r'? '\n' [ \t]* -> skip;

MULTI_LINE_COMMENT:                         '#/' .*? '/#' -> skip;
SINGLE_LINE_COMMENT:                        '#' ~[\r\n]* -> skip;

PASS:                                       'pass';

NUMBER:                                     '-'? [0-9]* '.' [0-9]+;
INTEGER:                                    '-'? [0-9]+;
IDENTIFIER:                                 [_@$&]? [a-zA-Z][a-zA-Z0-9_\-]*;

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

entry_point__:                              NEWLINE* header_statement__* body_statement__* EOF;

// ----------------------------------------------------------------------
// |  Common
identifier:                                 IDENTIFIER;

// ----------------------------------------------------------------------
// |  Expressions
expression__:                               (
                                                identifier_expression
                                                | number_expression
                                                | integer_expression
                                                | true_expression
                                                | false_expression
                                                | string_expression
                                                | list_expression
                                            );


identifier_expression:                      identifier;
number_expression:                          NUMBER;
integer_expression:                         INTEGER;
true_expression:                            'y' | 'Y' | 'yes' | 'Yes' | 'YES' | 'true' | 'True' | 'TRUE' | 'on' | 'On' | 'ON';
false_expression:                           'n' | 'N' | 'no' | 'No' | 'NO' | 'false' | 'False' | 'FALSE' | 'off' | 'Off' | 'OFF';

basic_string_expression:                    DOUBLE_QUOTE_STRING | SINGLE_QUOTE_STRING | UNTERMINATED_DOUBLE_QUOTE_STRING | UNTERMINATED_SINGLE_QUOTE_STRING;
string_expression:                          basic_string_expression | TRIPLE_DOUBLE_QUOTE_STRING | TRIPLE_SINGLE_QUOTE_STRING;

list_expression:                            LBRACK (expression__ (',' expression__)* ','?)? RBRACK;

// ----------------------------------------------------------------------
// |  Statements

// Header Statements
header_statement__:                         include_statement;

// TODO: this statement needs work
include_statement:                          'simple_schema_include' basic_string_expression NEWLINE+;

// Body Statements
body_statement__:                           structure_statement | item_statement | extension_statement;

extension_statement:                        identifier LPAREN (
                                                (
                                                    (
                                                        (extension_statement_positional_args ',' extension_statement_keyword_args)
                                                        | (extension_statement_keyword_args)
                                                        | (extension_statement_positional_args)
                                                    )
                                                    ','?
                                                )?
                                            ) RPAREN NEWLINE+;

extension_statement_positional_args:        expression__ (',' expression__)*;
extension_statement_keyword_args:           extension_statement_keyword_arg (',' extension_statement_keyword_arg)*;
extension_statement_keyword_arg:            identifier '=' expression__;

item_statement:                             identifier ':' type__ NEWLINE+;

structure_statement:                        identifier (
                                                (':' type__)
                                                | (cardinality_clause__ metadata_clause)
                                                | cardinality_clause__
                                                | metadata_clause
                                            )? '->' (structure_statement_single_line | structure_statement_multi_line);

structure_statement_single_line:            PASS NEWLINE+;
structure_statement_multi_line:             INDENT (
                                                (PASS NEWLINE+)
                                                | body_statement__+
                                            ) DEDENT;

// Statement Clauses
cardinality_clause__:                       (
                                                cardinality_clause_optional
                                                | cardinality_clause_zero_or_more
                                                | cardinality_clause_one_or_more
                                                | cardinality_clause_fixed
                                                | cardinality_clause_range
                                            );

cardinality_clause_optional:                '?';
cardinality_clause_zero_or_more:            '*';
cardinality_clause_one_or_more:             '+';
cardinality_clause_fixed:                   LBRACK integer_expression RBRACK;
cardinality_clause_range:                   LBRACK integer_expression ',' integer_expression RBRACK;

metadata_clause:                            '{' (metadata_clause_single_line__ | metadata_clause_multi_line__) '}';
metadata_clause_single_line__:              PASS | (metadata_clause_item (',' metadata_clause_item)* ','?);
metadata_clause_multi_line__:               INDENT (
                                                (PASS NEWLINE+)
                                                | (metadata_clause_item NEWLINE+)+
                                            ) DEDENT;
metadata_clause_item:                       identifier_expression ':' expression__;

// ----------------------------------------------------------------------
// |  Types
type__:                                     (
                                                tuple_type
                                                | variant_type
                                                | identifier_type
                                            );

identifier_type:                            identifier ('.' identifier)* identifier_type_element? cardinality_clause__? metadata_clause?;
identifier_type_element:                    '::element';

tuple_type:                                 LPAREN (tuple_type_single_item__ | tuple_type_multi_item__) RPAREN cardinality_clause__? metadata_clause?;
tuple_type_single_item__:                   type__ ',';
tuple_type_multi_item__:                    type__ (',' type__)+ ','?;

variant_type:                               LPAREN type__ ('|' type__)* '|' type__ RPAREN cardinality_clause__? metadata_clause?;
