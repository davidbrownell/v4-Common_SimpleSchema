# ----------------------------------------------------------------------
# |
# |  Parse.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-12 08:29:24
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that Parses SimpleSchema configuration elements"""

import functools
import sys
import threading

from pathlib import Path
from typing import Any, Callable, cast, Dict, Iterable, List, Optional, Tuple, Union

import antlr4

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Streams.DoneManager import DoneManager

from Common_FoundationEx import ExecuteTasks

from SimpleSchema.Schema.Impl.Common.Location import Location
from SimpleSchema.Schema.Impl.Common.Range import Range

from SimpleSchema.Schema.Impl.Common.Element import Element
from SimpleSchema.Schema.Impl.Common.Identifier import Identifier
from SimpleSchema.Schema.Impl.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Impl.Expressions.BooleanExpression import BooleanExpression
from SimpleSchema.Schema.Impl.Expressions.Expression import Expression
from SimpleSchema.Schema.Impl.Expressions.IdentifierExpression import IdentifierExpression
from SimpleSchema.Schema.Impl.Expressions.IntegerExpression import IntegerExpression
from SimpleSchema.Schema.Impl.Expressions.MetadataExpression import MetadataExpression, MetadataExpressionItem
from SimpleSchema.Schema.Impl.Expressions.NoneExpression import NoneExpression
from SimpleSchema.Schema.Impl.Expressions.NumberExpression import NumberExpression
from SimpleSchema.Schema.Impl.Expressions.StringExpression import StringExpression

from SimpleSchema.Schema.Impl.Statements.CompoundStatement import CompoundStatement
from SimpleSchema.Schema.Impl.Statements.DataMemberStatement import DataMemberStatement
from SimpleSchema.Schema.Impl.Statements.ExtensionStatement import ExtensionStatement, ExtensionStatementKeywordArg
from SimpleSchema.Schema.Impl.Statements.RootStatement import RootStatement
from SimpleSchema.Schema.Impl.Statements.Statement import Statement

from SimpleSchema.Schema.Impl.Types.Type import Type
from SimpleSchema.Schema.Impl.Types.IdentifierType import IdentifierType
from SimpleSchema.Schema.Impl.Types.TupleType import TupleType
from SimpleSchema.Schema.Impl.Types.VariantType import VariantType


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent.parent / "Grammar" / "GeneratedCode")))
with ExitStack(lambda: sys.path.pop(0)):
    from SimpleSchemaLexer import SimpleSchemaLexer     # type: ignore # pylint: disable=import-error
    from SimpleSchemaParser import SimpleSchemaParser   # type: ignore # pylint: disable=import-error
    from SimpleSchemaVisitor import SimpleSchemaVisitor # type: ignore # pylint: disable=import-error


# ----------------------------------------------------------------------
# |
# |  Public Types
# |
# ----------------------------------------------------------------------
class AntlrException(Exception):
    """Exception raised for parsing-related errors"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        msg: str,
        source: Path,
        line: int,
        column: int,
        ex: Optional[antlr4.RecognitionException],
    ):
        super(AntlrException, self).__init__(
            "{msg} ({source} [{line}, {column}])".format(
                msg=msg,
                source=source,
                line=line,
                column=column,
            ),
        )

        self.source                         = source
        self.line                           = line
        self.column                         = column
        self.ex                             = ex


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def Parse(
    dm: DoneManager,
    source_and_content_items: Iterable[Tuple[Path, Callable[[], str]]],
    *,
    single_threaded: bool=False,
    quiet: bool=False,
    raise_if_single_exception: bool=True,
) -> Dict[Path, Union[Exception, RootStatement]]:
    filenames: Dict[Path, Union[None, Exception, RootStatement]] = {}

    with ExecuteTasks.YieldQueueExecutor(
        dm,
        "Parsing...",
        quiet=quiet,
        max_num_threads=1 if single_threaded else None,
    ) as enqueue_func:
        filenames_lock = threading.Lock()

        # ----------------------------------------------------------------------
        def OnInclude(
            current_filename: Path,
            filename: StringExpression,
        ) -> None:
            fullpath = current_filename.parent / filename.value

            if not fullpath.is_file():
                raise SimpleSchemaException(
                    "The included file '{}' is not valid.".format(fullpath),
                    filename.range,
                )

            with filenames_lock:
                if fullpath in filenames:
                    return

                filenames[fullpath] = None

            with fullpath.open() as f:
                content = f.read()

            enqueue_func(str(fullpath), lambda _: Step1(fullpath, content, is_included_file=True))

        # ----------------------------------------------------------------------
        def Step1(
            filename: Path,
            content: str,
            *,
            is_included_file: bool,
        ) -> Tuple[Optional[int], ExecuteTasks.QueueStep2FuncType]:
            # ----------------------------------------------------------------------
            def Impl(
                status: ExecuteTasks.Status,
            ) -> Optional[str]:
                result: Union[None, Exception, RootStatement] = None

                # ----------------------------------------------------------------------
                def OnExit():
                    assert result is not None

                    with filenames_lock:
                        assert filenames[filename] is None, (filename, filenames[filename])
                        filenames[filename] = result

                # ----------------------------------------------------------------------

                with ExitStack(OnExit):
                    try:
                        antlr_stream = antlr4.InputStream(content)

                        lexer = SimpleSchemaLexer(antlr_stream)
                        tokens = antlr4.CommonTokenStream(lexer)

                        tokens.fill()

                        parser = SimpleSchemaParser(tokens)
                        parser.addErrorListener(_ErrorListener(filename))

                        ast = parser.entry_point__()
                        assert ast

                        visitor = _Visitor(
                            filename,
                            lambda line: cast(None, status.OnProgress(line, None)),
                            OnInclude,
                            is_included_file=is_included_file,
                        )

                        ast.accept(visitor)

                        result = visitor.root

                    except Exception as ex:
                        result = ex
                        raise

            # ----------------------------------------------------------------------

            return len(content.split("\n")), Impl

        # ----------------------------------------------------------------------

        with filenames_lock:
            for source, content_func in source_and_content_items:
                enqueue_func(
                    str(source),
                    lambda _, source=source, content_func=content_func: Step1(
                        source,
                        content_func(),
                        is_included_file=False,
                    ),
                )

                filenames[source] = None

    if dm.result != 0 and raise_if_single_exception:
        exceptions: List[Exception] = [value for value in filenames.values() if isinstance(value, Exception)]

        if len(exceptions) == 1:
            raise exceptions[0]

    results: Dict[Path, Union[Exception, RootStatement]] = {}

    for source, result in filenames.items():
        assert result is not None, source
        results[source] = result

    return results


# ----------------------------------------------------------------------
# |
# |  Private Types
# |
# ----------------------------------------------------------------------
class _VisitorMixin(object):
    # ----------------------------------------------------------------------
    def ToRange(
        self,
        ctx: antlr4.ParserRuleContext,
    ) -> Range:
        assert isinstance(ctx.start, antlr4.Token), ctx.start
        assert isinstance(ctx.stop, antlr4.Token), ctx.stop

        if ctx.stop.type == SimpleSchemaParser.DEDENT:
            stop_line = ctx.stop.line
            stop_col = ctx.stop.column

        elif (
            ctx.stop.type == SimpleSchemaParser.NEWLINE
            and ctx.stop.text == "newLine"
        ):
            if ctx.stop.line == ctx.start.line:
                # This is the scenario where the statement is followed by a dedent followed by another
                # statement. We don't want the range of this item to overlap with the range of the next
                # item, so use the values as they are, event though it means that a statement that
                # terminates with a newline will not have that newline here.
                stop_line = ctx.stop.line
                stop_col = ctx.stop.column
            else:
                stop_line = ctx.stop.line
                stop_col = ctx.stop.column if ctx.stop.column == 0 else ctx.start.column

        else:
            content = ctx.stop.text
            stop_line = ctx.stop.line

            if ctx.stop.type == SimpleSchemaParser.NEWLINE:
                stop_line += 1 # We have to update the line number manually

                assert content.startswith("\n"), content

                lines = content.split("\n")
                assert len(lines) == 2, lines

                last_line = lines[-1]

            else:
                lines = content.split("\n")

                stop_line += len(lines) - 1
                last_line = lines[-1]

            stop_col = len(last_line)

            if stop_line == ctx.stop.line:
                stop_col += ctx.stop.column

        return Range.Create(
            self.filename,
            ctx.start.line,
            ctx.start.column + 1,
            stop_line,
            stop_col + 1,
        )

    # ----------------------------------------------------------------------
    def __init__(
        self,
        filename: Path,
        on_progress_func: Callable[[int], None],
        on_include_func: Callable[[Path, StringExpression], None],
        *,
        is_included_file: bool,
    ):
        self.filename                       = filename
        self.is_included_file               = is_included_file

        self._on_progress_func              = on_progress_func
        self._on_include_func               = on_include_func

        self._current_line: int             = 0
        self._stack: List[Any]              = []

    # ----------------------------------------------------------------------
    @functools.cached_property
    def root(self) -> RootStatement:
        assert all(isinstance(item, Statement) for item in self._stack)

        if not self._stack:
            range_value = Range(self.filename, Location(1, 1), Location(1, 1))
        else:
            range_value = Range(self.filename, self._stack[0].range.start, self._stack[-1].range.end)

        return RootStatement(range_value, cast(List[Statement], self._stack))

    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    # ----------------------------------------------------------------------
    def _GetChildren(self, ctx) -> List[Union[Expression, Statement]]:
        prev_num_stack_items = len(self._stack)

        cast(SimpleSchemaVisitor, self).visitChildren(ctx)

        results = self._stack[prev_num_stack_items:]

        self._stack = self._stack[:prev_num_stack_items]

        return results

    # ----------------------------------------------------------------------
    def _OnProgress(self, ctx):
        if ctx.stop.line > self._current_line:
            self._current_line = ctx.stop.line
            self._on_progress_func(self._current_line)


# ----------------------------------------------------------------------
class _ErrorListener(antlr4.DiagnosticErrorListener):
    # ----------------------------------------------------------------------
    def __init__(
        self,
        source: Path,
        *args,
        **kwargs,
    ):
        super(_ErrorListener, self).__init__(*args, **kwargs)

        self._source                        = source

    # ----------------------------------------------------------------------
    def syntaxError(
        self,
        recognizer: SimpleSchemaParser,     # pylint: disable=unused-argument
        offendingSymbol: antlr4.Token,      # pylint: disable=unused-argument
        line: int,
        column: int,
        msg: str,
        e: antlr4.RecognitionException,
    ) -> Any:
        raise AntlrException(msg, self._source, line, column + 1, e)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _Visitor(SimpleSchemaVisitor, _VisitorMixin):
    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        _VisitorMixin.__init__(self, *args, **kwargs)

    # ----------------------------------------------------------------------
    def visitIdentifier(self, ctx:SimpleSchemaParser.IdentifierContext):
        symbol = ctx.IDENTIFIER().symbol
        self._stack.append(Identifier(self.ToRange(ctx), symbol.text))

    # ----------------------------------------------------------------------
    def visitIdentifier_expression(self, ctx:SimpleSchemaParser.Identifier_expressionContext):
        children = self._GetChildren(ctx)
        assert len(children) == 1

        child = children[0]
        assert isinstance(child, Identifier), child

        self._stack.append(IdentifierExpression(child.range, child.value))

    # ----------------------------------------------------------------------
    def visitNumber_expression(self, ctx:SimpleSchemaParser.Number_expressionContext):
        symbol = ctx.NUMBER().symbol
        self._stack.append(NumberExpression(self.ToRange(ctx), float(symbol.text)))

    # ----------------------------------------------------------------------
    def visitInteger_expression(self, ctx:SimpleSchemaParser.Integer_expressionContext):
        symbol = ctx.INTEGER().symbol
        self._stack.append(IntegerExpression(self.ToRange(ctx), int(symbol.text)))

    # ----------------------------------------------------------------------
    def visitTrue_expression(self, ctx:SimpleSchemaParser.True_expressionContext):
        self._stack.append(BooleanExpression(self.ToRange(ctx), True))

    # ----------------------------------------------------------------------
    def visitFalse_expression(self, ctx:SimpleSchemaParser.False_expressionContext):
        self._stack.append(BooleanExpression(self.ToRange(ctx), False))

    # ----------------------------------------------------------------------
    def visitNone_expression(self, ctx:SimpleSchemaParser.None_expressionContext):
        self._stack.append(NoneExpression(self.ToRange(ctx)))

    # ----------------------------------------------------------------------
    def visitBasic_string_expression(self, ctx:SimpleSchemaParser.Basic_string_expressionContext):
        return self.visitString_expression(ctx)

    # ----------------------------------------------------------------------
    def visitString_expression(self, ctx:SimpleSchemaParser.String_expressionContext):
        context = ctx

        while not isinstance(context, antlr4.TerminalNode):
            assert len(context.children) == 1
            context = context.children[0]

        token = context.symbol  # type: ignore
        value = token.text  # type: ignore

        # At the very least, we should have a beginning and ending quote
        assert len(value) >= 2, value

        if value.startswith('"""') or value.startswith("'''"):
            initial_whitespace = token.column

            # ----------------------------------------------------------------------
            def TrimPrefix(
                line: str,
                line_offset: int,
            ) -> str:
                index = 0
                whitespace = 0

                while index < len(line) and whitespace < initial_whitespace:
                    if line[index] == " ":
                        whitespace += 1
                    elif line[index] == "\t":
                        whitespace += 4
                    elif line[index] == "\r":
                        break
                    else:
                        raise AntlrException(
                            "Invalid multiline string indentation.",
                            self.filename,
                            ctx.start.line + line_offset,
                            whitespace + 1,
                            None,
                        )

                    index += 1

                return line[index:]

            # ----------------------------------------------------------------------

            lines = value.split("\n")

            initial_line = lines[0].rstrip()
            if len(initial_line) != 3:
                raise AntlrException(
                    "Triple-quote delimiters that initiate multiline strings must not have any trailing content.",
                    self.filename,
                    ctx.start.line,
                    ctx.start.column + 1 + 3,
                    None,
                )

            final_line = lines[-1]
            if len(TrimPrefix(final_line, len(lines))) != 3:
                raise AntlrException(
                    "Triple-quote delimiters that terminate multiline strings must not have any preceding content.",
                    self.filename,
                    ctx.start.line + len(lines) - 1,
                    ctx.start.column + 1,
                    None,
                )

            lines = [TrimPrefix(line, index + 1) for index, line in enumerate(lines[1:-1])]

            value = "\n".join(lines)

        elif value[0] == '"' and value[-1] == '"':
            value = value[1:-1].replace('\\"', '"')

        elif value[0] == "'" and value[-1] == "'":
            value = value[1:-1].replace("\\'", "'")

        else:
            assert False, value  # pragma: no cover

        self._stack.append(StringExpression(self.ToRange(ctx), value))

    # ----------------------------------------------------------------------
    def visitMetadata_group_expression(self, ctx:SimpleSchemaParser.Metadata_group_expressionContext):
        children = self._GetChildren(ctx)
        assert all(isinstance(child, MetadataExpressionItem) for child in children), children

        self._stack.append(
            MetadataExpression(
                self.ToRange(ctx),
                cast(List[MetadataExpressionItem], children),
            ),
        )

        self._OnProgress(ctx)

    # ----------------------------------------------------------------------
    def visitMetadata_expression(self, ctx:SimpleSchemaParser.Metadata_expressionContext):
        children = self._GetChildren(ctx)
        assert len(children) == 2

        name = children[0]
        assert isinstance(name, IdentifierExpression), name

        value = children[1]
        assert isinstance(name, Expression), name

        self._stack.append(MetadataExpressionItem(self.ToRange(ctx), name, value))

    # ----------------------------------------------------------------------
    def visitIdentifier_type(self, ctx:SimpleSchemaParser.Identifier_typeContext):
        children = self._GetChildren(ctx)
        assert len(children) == 1

        child = children[0]
        assert isinstance(child, Identifier), child

        self._stack.append(IdentifierType(child.range, child.value))

    # ----------------------------------------------------------------------
    def visitTuple_type(self, ctx:SimpleSchemaParser.Tuple_typeContext):
        children = self._GetChildren(ctx)

        assert all(isinstance(child, Type) for child in children)
        children = cast(List[Type], children)

        self._stack.append(TupleType(self.ToRange(ctx), children))

    # ----------------------------------------------------------------------
    def visitVariant_type(self, ctx:SimpleSchemaParser.Variant_typeContext):
        children = self._GetChildren(ctx)

        assert all(isinstance(child, Type) for child in children)
        children = cast(List[Type], children)

        self._stack.append(VariantType(self.ToRange(ctx), children))

    # ----------------------------------------------------------------------
    def visitInclude_statement(self, ctx:SimpleSchemaParser.Include_statementContext):
        children = self._GetChildren(ctx)
        assert len(children) == 1, children

        child = children[0]
        assert isinstance(child, StringExpression), child

        self._on_include_func(self.filename, child)

    # ----------------------------------------------------------------------
    def visitCompound_statement(self, ctx:SimpleSchemaParser.Compound_statementContext):
        children = self._GetChildren(ctx)

        num_children = len(children)
        assert 2 <= num_children <= 4

        name = children[0]
        assert isinstance(name, Identifier), name

        base_type: Optional[Type] = None
        metadata: Optional[MetadataExpression] = None
        statements: Optional[List[Statement]] = None

        for index in range(1, num_children):
            child = children[index]

            if isinstance(child, Type):
                assert base_type is None, base_type
                base_type = child
            elif isinstance(child, MetadataExpression):
                assert metadata is None, metadata
                metadata = child
            elif isinstance(child, list):
                assert all(isinstance(statement, Statement) for statement in child), child
                assert statements is None, statements
                statements = child
            else:
                assert False, child  # pragma: no cover

        assert statements is not None

        self._stack.append(
            CompoundStatement(self.ToRange(ctx), name, base_type, metadata, statements),
        )

        self._OnProgress(ctx)

    # ----------------------------------------------------------------------
    def visitCompound_statement_single_line(
        self,
        ctx:SimpleSchemaParser.Compound_statement_single_lineContext,  # pylint: disable=unused-argument
    ):
        # pass is the only thing that can appear on a single line, so it is safe to generate an empty list
        self._stack.append([])

    # ----------------------------------------------------------------------
    def visitCompound_statement_multi_line(self, ctx:SimpleSchemaParser.Compound_statement_multi_lineContext):
        children = self._GetChildren(ctx)
        assert all(isinstance(child, Statement) for child in children), children

        self._stack.append(children)

    # ----------------------------------------------------------------------
    def visitData_member_statement(self, ctx:SimpleSchemaParser.Data_member_statementContext):
        children = self._GetChildren(ctx)
        assert 2 <= len(children) <= 3

        name = children[0]
        assert isinstance(name, IdentifierExpression), name

        the_type = children[1]
        assert isinstance(the_type, Type), the_type

        if len(children) == 3:
            metadata = children[2]
            assert isinstance(metadata, MetadataExpression), metadata
        else:
            metadata = None

        self._stack.append(DataMemberStatement(self.ToRange(ctx), name, the_type, metadata))

        self._OnProgress(ctx)

    # ----------------------------------------------------------------------
    def visitExtension_statement(self, ctx:SimpleSchemaParser.Extension_statementContext):
        children = self._GetChildren(ctx)
        num_children = len(children)

        assert 1 <= num_children <= 3

        name = children[0]
        assert isinstance(name, Identifier), name

        positional_arguments: Optional[List[Element]] = None
        keyword_arguments: Optional[List[ExtensionStatementKeywordArg]] = None

        for index in range(1, num_children):
            arguments = children[index]

            assert isinstance(arguments, list) and arguments

            if isinstance(arguments[0], ExtensionStatementKeywordArg):
                assert keyword_arguments is None
                keyword_arguments = arguments
            elif isinstance(arguments[0], Element):
                assert positional_arguments is None
                positional_arguments = arguments
            else:
                assert False, arguments  # pragma: no cover

        self._stack.append(
            ExtensionStatement(
                self.ToRange(ctx),
                name,
                positional_arguments or [],
                keyword_arguments or [],
            ),
        )

        self._OnProgress(ctx)

    # ----------------------------------------------------------------------
    def visitExtension_statement_positional_args(self, ctx:SimpleSchemaParser.Extension_statement_positional_argsContext):
        children = self._GetChildren(ctx)
        assert children
        assert all(isinstance(child, Element) for child in children)

        self._stack.append(children)

    # ----------------------------------------------------------------------
    def visitExtension_statement_keyword_args(self, ctx:SimpleSchemaParser.Extension_statement_keyword_argsContext):
        children = self._GetChildren(ctx)
        assert children
        assert all(isinstance(child, ExtensionStatementKeywordArg) for child in children)

        self._stack.append(children)

    # ----------------------------------------------------------------------
    def visitExtension_statement_keyword_arg(self, ctx:SimpleSchemaParser.Extension_statement_keyword_argContext):
        children = self._GetChildren(ctx)
        assert len(children) == 2

        name = children[0]
        assert isinstance(name, Identifier), name

        value = children[1]
        assert isinstance(value, Element), value

        self._stack.append(ExtensionStatementKeywordArg(self.ToRange(ctx), name, value))
