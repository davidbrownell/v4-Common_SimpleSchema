# Generated from C:\Code\v4\Common\SimpleSchema\src\SimpleSchema\Schema\Grammar\SimpleSchema.g4 by ANTLR 4.11.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .SimpleSchemaParser import SimpleSchemaParser
else:
    from SimpleSchemaParser import SimpleSchemaParser

# This class defines a complete generic visitor for a parse tree produced by SimpleSchemaParser.

class SimpleSchemaVisitor(ParseTreeVisitor):

    # Visit a parse tree produced by SimpleSchemaParser#identifier.
    def visitIdentifier(self, ctx:SimpleSchemaParser.IdentifierContext):
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


    # Visit a parse tree produced by SimpleSchemaParser#none_expression.
    def visitNone_expression(self, ctx:SimpleSchemaParser.None_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#basic_string_expression.
    def visitBasic_string_expression(self, ctx:SimpleSchemaParser.Basic_string_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#string_expression.
    def visitString_expression(self, ctx:SimpleSchemaParser.String_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#metadata_group_expression.
    def visitMetadata_group_expression(self, ctx:SimpleSchemaParser.Metadata_group_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#metadata_group_expression_single_line__.
    def visitMetadata_group_expression_single_line__(self, ctx:SimpleSchemaParser.Metadata_group_expression_single_line__Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#metadata_group_expression_multi_line__.
    def visitMetadata_group_expression_multi_line__(self, ctx:SimpleSchemaParser.Metadata_group_expression_multi_line__Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#metadata_expression.
    def visitMetadata_expression(self, ctx:SimpleSchemaParser.Metadata_expressionContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#pass_expression__.
    def visitPass_expression__(self, ctx:SimpleSchemaParser.Pass_expression__Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#expression__.
    def visitExpression__(self, ctx:SimpleSchemaParser.Expression__Context):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#identifier_type.
    def visitIdentifier_type(self, ctx:SimpleSchemaParser.Identifier_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#tuple_type.
    def visitTuple_type(self, ctx:SimpleSchemaParser.Tuple_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#variant_type.
    def visitVariant_type(self, ctx:SimpleSchemaParser.Variant_typeContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#type__.
    def visitType__(self, ctx:SimpleSchemaParser.Type__Context):
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


    # Visit a parse tree produced by SimpleSchemaParser#compound_statement.
    def visitCompound_statement(self, ctx:SimpleSchemaParser.Compound_statementContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#compound_statement_single_line.
    def visitCompound_statement_single_line(self, ctx:SimpleSchemaParser.Compound_statement_single_lineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#compound_statement_multi_line.
    def visitCompound_statement_multi_line(self, ctx:SimpleSchemaParser.Compound_statement_multi_lineContext):
        return self.visitChildren(ctx)


    # Visit a parse tree produced by SimpleSchemaParser#data_member_statement.
    def visitData_member_statement(self, ctx:SimpleSchemaParser.Data_member_statementContext):
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


    # Visit a parse tree produced by SimpleSchemaParser#entry_point__.
    def visitEntry_point__(self, ctx:SimpleSchemaParser.Entry_point__Context):
        return self.visitChildren(ctx)



del SimpleSchemaParser