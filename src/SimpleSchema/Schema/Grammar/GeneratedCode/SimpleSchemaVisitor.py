# Generated from C:\Code\v4\Common\SimpleSchema\src\SimpleSchema\Schema\Grammar\SimpleSchema.g4 by ANTLR 4.11.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .SimpleSchemaParser import SimpleSchemaParser
else:
    from SimpleSchemaParser import SimpleSchemaParser

# This class defines a complete generic visitor for a parse tree produced by SimpleSchemaParser.

class SimpleSchemaVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by SimpleSchemaParser#entry_point__.
    def visitEntry_point__(self, ctx:SimpleSchemaParser.Entry_point__Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#identifier.
    def visitIdentifier(self, ctx:SimpleSchemaParser.IdentifierContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#expression__.
    def visitExpression__(self, ctx:SimpleSchemaParser.Expression__Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#identifier_expression.
    def visitIdentifier_expression(self, ctx:SimpleSchemaParser.Identifier_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#number_expression.
    def visitNumber_expression(self, ctx:SimpleSchemaParser.Number_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#integer_expression.
    def visitInteger_expression(self, ctx:SimpleSchemaParser.Integer_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#true_expression.
    def visitTrue_expression(self, ctx:SimpleSchemaParser.True_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#false_expression.
    def visitFalse_expression(self, ctx:SimpleSchemaParser.False_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#basic_string_expression.
    def visitBasic_string_expression(self, ctx:SimpleSchemaParser.Basic_string_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#string_expression.
    def visitString_expression(self, ctx:SimpleSchemaParser.String_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#list_expression.
    def visitList_expression(self, ctx:SimpleSchemaParser.List_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#header_statement__.
    def visitHeader_statement__(self, ctx:SimpleSchemaParser.Header_statement__Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#include_statement.
    def visitInclude_statement(self, ctx:SimpleSchemaParser.Include_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#body_statement__.
    def visitBody_statement__(self, ctx:SimpleSchemaParser.Body_statement__Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#extension_statement.
    def visitExtension_statement(self, ctx:SimpleSchemaParser.Extension_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#extension_statement_positional_args.
    def visitExtension_statement_positional_args(self, ctx:SimpleSchemaParser.Extension_statement_positional_argsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#extension_statement_keyword_args.
    def visitExtension_statement_keyword_args(self, ctx:SimpleSchemaParser.Extension_statement_keyword_argsContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#extension_statement_keyword_arg.
    def visitExtension_statement_keyword_arg(self, ctx:SimpleSchemaParser.Extension_statement_keyword_argContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#item_statement.
    def visitItem_statement(self, ctx:SimpleSchemaParser.Item_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#structure_statement.
    def visitStructure_statement(self, ctx:SimpleSchemaParser.Structure_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#structure_statement_single_line.
    def visitStructure_statement_single_line(self, ctx:SimpleSchemaParser.Structure_statement_single_lineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#structure_statement_multi_line.
    def visitStructure_statement_multi_line(self, ctx:SimpleSchemaParser.Structure_statement_multi_lineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#cardinality_clause__.
    def visitCardinality_clause__(self, ctx:SimpleSchemaParser.Cardinality_clause__Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#cardinality_clause_optional.
    def visitCardinality_clause_optional(self, ctx:SimpleSchemaParser.Cardinality_clause_optionalContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#cardinality_clause_zero_or_more.
    def visitCardinality_clause_zero_or_more(self, ctx:SimpleSchemaParser.Cardinality_clause_zero_or_moreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#cardinality_clause_one_or_more.
    def visitCardinality_clause_one_or_more(self, ctx:SimpleSchemaParser.Cardinality_clause_one_or_moreContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#cardinality_clause_fixed.
    def visitCardinality_clause_fixed(self, ctx:SimpleSchemaParser.Cardinality_clause_fixedContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#cardinality_clause_range.
    def visitCardinality_clause_range(self, ctx:SimpleSchemaParser.Cardinality_clause_rangeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#metadata_clause.
    def visitMetadata_clause(self, ctx:SimpleSchemaParser.Metadata_clauseContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#metadata_clause_single_line__.
    def visitMetadata_clause_single_line__(self, ctx:SimpleSchemaParser.Metadata_clause_single_line__Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#metadata_clause_multi_line__.
    def visitMetadata_clause_multi_line__(self, ctx:SimpleSchemaParser.Metadata_clause_multi_line__Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#metadata_clause_item.
    def visitMetadata_clause_item(self, ctx:SimpleSchemaParser.Metadata_clause_itemContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#type__.
    def visitType__(self, ctx:SimpleSchemaParser.Type__Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#identifier_type.
    def visitIdentifier_type(self, ctx:SimpleSchemaParser.Identifier_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#identifier_type_element.
    def visitIdentifier_type_element(self, ctx:SimpleSchemaParser.Identifier_type_elementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#tuple_type.
    def visitTuple_type(self, ctx:SimpleSchemaParser.Tuple_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#tuple_type_single_item__.
    def visitTuple_type_single_item__(self, ctx:SimpleSchemaParser.Tuple_type_single_item__Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#tuple_type_multi_item__.
    def visitTuple_type_multi_item__(self, ctx:SimpleSchemaParser.Tuple_type_multi_item__Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#variant_type.
    def visitVariant_type(self, ctx:SimpleSchemaParser.Variant_typeContext):
        return self.visitChildren(ctx)



del SimpleSchemaParser