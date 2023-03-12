# ----------------------------------------------------------------------
# |
# |  Parse.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2023-01-19 14:03:00
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2023
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality that parses SimpleSchema files via ANTLR"""

import itertools
import sys
import threading

from functools import cached_property
from pathlib import Path
from typing import Any, Callable, cast, Optional, Protocol, Tuple, Union

import antlr4

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Streams.DoneManager import DoneManager

from Common_FoundationEx import ExecuteTasks

from .Elements.Common.ParseIdentifier import ParseIdentifier

from .Elements.Statements.ParseIncludeStatement import ParseIncludeStatement, ParseIncludeStatementItem, ParseIncludeStatementType
from .Elements.Statements.ParseItemStatement import ParseItemStatement
from .Elements.Statements.ParseStructureStatement import ParseStructureStatement

from .Elements.Types.ParseIdentifierType import ParseIdentifierType
from .Elements.Types.ParseType import ParseType
from .Elements.Types.ParseTupleType import ParseTupleType
from .Elements.Types.ParseVariantType import ParseVariantType

from ...Elements.Common.Cardinality import Cardinality
from ...Elements.Common.Element import Element
from ...Elements.Common.Metadata import Metadata, MetadataItem
from ...Elements.Common.SimpleElement import SimpleElement

from ...Elements.Expressions.BooleanExpression import BooleanExpression
from ...Elements.Expressions.Expression import Expression
from ...Elements.Expressions.IntegerExpression import IntegerExpression
from ...Elements.Expressions.ListExpression import ListExpression
from ...Elements.Expressions.NoneExpression import NoneExpression
from ...Elements.Expressions.NumberExpression import NumberExpression
from ...Elements.Expressions.StringExpression import StringExpression
from ...Elements.Expressions.TupleExpression import TupleExpression

from ...Elements.Statements.ExtensionStatement import ExtensionStatement, ExtensionStatementKeywordArg
from ...Elements.Statements.RootStatement import RootStatement
from ...Elements.Statements.Statement import Statement

from ....Common import Errors
from ....Common.Location import Location
from ....Common.Range import Range


# ----------------------------------------------------------------------
sys.path.insert(0, str(PathEx.EnsureDir(Path(__file__).parent / "Grammar" / "GeneratedCode")))
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
    """Exceptions raise for parsing-related errors"""

    # ----------------------------------------------------------------------
    def __init__(
        self,
        message: str,
        source: Path,
        line: int,
        column: int,
        ex: Optional[antlr4.RecognitionException],
    ):
        location = Location(line, column)

        super(AntlrException, self).__init__("{} ({} <{}>)".format(message, source, location))

        self.source                         = source
        self.location                       = location
        self.ex                             = ex


# ----------------------------------------------------------------------
DEFAULT_FILE_EXTENSIONS: list[str]          = [
    ".SimpleSchema",
]


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def Parse(
    dm: DoneManager,
    workspaces: dict[
        Path,                               # workspace root
        dict[
            Path,                           # relative path
            Callable[[], str],              # content
        ],
    ],
    file_extensions: Optional[list[str]]=None,
    *,
    single_threaded: bool=False,
    quiet: bool=False,
    raise_if_single_exception: bool=True,
) -> dict[
    Path,                                   # workspace root
    dict[
        Path,                               # relative path
        Union[Exception, RootStatement],
    ],
]:
    if file_extensions is None:
        file_extensions = DEFAULT_FILE_EXTENSIONS

    workspace_names: list[Path] = [workspace.resolve() for workspace in workspaces]

    workspace_names.sort(
        key=lambda value: len(str(value)),
        reverse=True,
    )

    results: dict[
        Path,                               # workspace root
        dict[
            Path,                           # relative path
            Union[None, Exception, RootStatement],
        ],
    ] = {}

    with ExecuteTasks.YieldQueueExecutor(
        dm,
        "Parsing...",
        quiet=quiet,
        max_num_threads=1 if single_threaded else None,
    ) as enqueue_func:
        results_lock = threading.Lock()

        # ----------------------------------------------------------------------
        def ResolveIncludeFilename(
            path: Path,
            *,
            allow_directory: bool,
        ) -> Optional[Path]:
            path = path.resolve()

            if path.is_file() or (allow_directory and path.is_dir()):
                return path

            for extension in file_extensions:
                potential_path = path.parent / (path.name + extension)
                if potential_path.is_file():
                    return potential_path

            return None

        # ----------------------------------------------------------------------
        def CreateIncludeStatement(
            including_filename: Path,
            range_value: Range,
            filename_or_directory: SimpleElement[Path],
            items: list[ParseIncludeStatementItem],
            *,
            is_star_include: bool,
        ) -> ParseIncludeStatement:
            root : Optional[Path] = None

            for potential_root in itertools.chain(
                [including_filename.parent, ],
                workspace_names,
            ):
                fullpath = ResolveIncludeFilename(
                    potential_root / filename_or_directory.value,
                    allow_directory=True,
                )
                if fullpath is not None:
                    root = fullpath
                    break

            if root is None:
                raise Errors.ParseCreateIncludeStatementInvalidPath.Create(
                    filename_or_directory.range,
                    filename_or_directory.value,
                )

            filename: Optional[Path] = None
            filename_range: Optional[Range] = None

            include_type: Optional[ParseIncludeStatementType] = None

            if root.is_dir():
                if is_star_include:
                    raise Errors.ParseCreateIncludeStatementDirWithStar.Create(range_value, root)

                if len(items) != 1:
                    raise Errors.ParseCreateIncludeStatementTooManyItems.Create(items[1].range)

                filename = ResolveIncludeFilename(
                    root / items[0].element_name.value,
                    allow_directory=False,
                )

                filename_range = Range(
                    filename_or_directory.range.filename,
                    filename_or_directory.range.begin,
                    items[0].element_name.range.end,
                )

                if filename is None:
                    raise Errors.ParseCreateIncludeStatementInvalidFilename.Create(filename_range, items[0].element_name.value)

                include_type = ParseIncludeStatementType.Module
                items = []
            else:
                if is_star_include:
                    assert not items
                    include_type = ParseIncludeStatementType.Star
                else:
                    include_type = ParseIncludeStatementType.Named

                filename = root
                filename_range = filename_or_directory.range

            assert filename is not None
            assert filename.is_file(), filename
            assert filename_range is not None
            assert include_type is not None

            # Get the workspace associated with the file
            workspace: Optional[Path] = None

            for workspace_name in workspace_names:
                if PathEx.IsDescendant(filename, workspace_name):
                    workspace = workspace_name
                    break

            if workspace is None:
                raise Errors.ParseCreateIncludeStatementInvalidWorkspace.Create(range_value, filename)

            # Get the relative path for the workspace
            relative_path = PathEx.CreateRelativePath(workspace, filename)
            assert relative_path is not None

            relative_path = cast(Path, relative_path)

            # Determine if this is a file that should be enqueued for parsing
            should_enqueue = False

            with results_lock:
                workspace_results = results[workspace]

                if relative_path not in workspace_results:
                    workspace_results[relative_path] = None
                    should_enqueue = True

            if should_enqueue:
                # ----------------------------------------------------------------------
                def GetContent() -> str:
                    with filename.open(encoding="UTF-8") as f:
                        return f.read()

                # ----------------------------------------------------------------------

                enqueue_func(
                    str(filename),
                    lambda _: Step1(
                        workspace,
                        relative_path,
                        GetContent,
                        is_included_file=True,
                    ),
                )

            return ParseIncludeStatement(
                range_value,
                include_type,
                SimpleElement(filename_range, filename),
                items,
            )

        # ----------------------------------------------------------------------
        def Step1(
            workspace_root: Path,
            relative_path: Path,
            content_func: Callable[[], str],
            *,
            is_included_file: bool,
        ) -> Tuple[Optional[int], ExecuteTasks.QueueStep2FuncType]:
            content = content_func()

            # ----------------------------------------------------------------------
            def Impl(
                status: ExecuteTasks.Status,
            ) -> Optional[str]:
                result: Union[None, Exception, RootStatement] = None

                # ----------------------------------------------------------------------
                def OnExit():
                    assert result is not None

                    with results_lock:
                        assert results[workspace_root][relative_path] is None, (workspace_root, relative_path)
                        results[workspace_root][relative_path] = result

                # ----------------------------------------------------------------------

                with ExitStack(OnExit):
                    fullpath = workspace_root / relative_path

                    try:
                        # Parse the object
                        antlr_stream = antlr4.InputStream(content)

                        lexer = SimpleSchemaLexer(antlr_stream)

                        # Initialize instance variables that we have explicitly added within the
                        # ANTLR grammar file.
                        lexer.CustomInitialization()

                        tokens = antlr4.CommonTokenStream(lexer)

                        tokens.fill()

                        parser = SimpleSchemaParser(tokens)
                        parser.addErrorListener(_ErrorListener(fullpath))

                        ast = parser.entry_point__()
                        assert ast

                        visitor = _Visitor(
                            fullpath,
                            lambda line: cast(None, status.OnProgress(line, None)),
                            CreateIncludeStatement,
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

        with results_lock:
            is_single_workspace = len(workspaces) == 1

            for workspace_root, sources in workspaces.items():
                these_results: dict[Path, Union[None, Exception, RootStatement]] = {}

                for relative_path, content_func in sources.items():
                    enqueue_func(
                        str(relative_path if is_single_workspace else workspace_root / relative_path),
                        lambda _, workspace_root=workspace_root, relative_path=relative_path, content_func=content_func: Step1(
                            workspace_root,
                            relative_path,
                            content_func,
                            is_included_file=False,
                        ),
                    )

                    these_results[relative_path] = None

                results[workspace_root] = these_results

    if dm.result != 0 and raise_if_single_exception:
        exceptions: list[Exception] = []

        for workspace_results in results.values():
            for result in workspace_results.values():
                if isinstance(result, Exception):
                    exceptions.append(result)

        if len(exceptions) == 1:
            raise exceptions[0]

    for workspace_root, workspace_results in results.items():
        for relative_path, result in workspace_results.items():
            assert result is not None, (workspace_root, relative_path)

    return cast(dict[Path, dict[Path, Union[Exception, RootStatement]]], results)


# ----------------------------------------------------------------------
# |
# |  Private Types
# |
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
    ):
        raise AntlrException(msg, self._source, line, column + 1, e)


# ----------------------------------------------------------------------
class _VisitorMixin(object):
    # ----------------------------------------------------------------------
    # |
    # |  Public Types
    # |
    # ----------------------------------------------------------------------
    class CreateIncludeStatementFunc(Protocol):
        def __call__(
            self,
            include_path: Path,
            range_value: Range,
            filename_or_directory: SimpleElement[Path],
            items: list[ParseIncludeStatementItem],
            *,
            is_star_include: bool,
        ) -> ParseIncludeStatement:
            ...  # pragma: no cover

    # ----------------------------------------------------------------------
    # |
    # |  Public Methods
    # |
    # ----------------------------------------------------------------------
    def __init__(
        self,
        filename: Path,
        on_progress_func: Callable[[int], None],
        create_include_statement_func: "_VisitorMixin.CreateIncludeStatementFunc",
        *,
        is_included_file: bool,
    ):
        self.filename                       = filename
        self.is_included_file               = is_included_file

        self._on_progress_func              = on_progress_func
        self._create_include_statement_func = create_include_statement_func

        self._current_line: int             = 0
        self._stack: list[Any]              = []

    # ----------------------------------------------------------------------
    @cached_property
    def root(self) -> RootStatement:
        if not self._stack:
            range_value = Range(self.filename, Location(1, 1), Location(1, 1))
        else:
            range_value = Range(self.filename, self._stack[0].range.begin, self._stack[-1].range.end)

        assert all(isinstance(item, Statement) for item in self._stack)
        return RootStatement(range_value, cast(list[Statement], self._stack))

    # ----------------------------------------------------------------------
    def CreateRange(
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

        self._OnProgress(stop_line)

        return Range.Create(
            self.filename,
            ctx.start.line,
            ctx.start.column + 1,
            stop_line,
            stop_col + 1,
        )

    # ----------------------------------------------------------------------
    # |
    # |  Protected Methods
    # |
    # ----------------------------------------------------------------------
    def _GetChildren(self, ctx) -> list[Any]:
        prev_num_stack_items = len(self._stack)

        cast(SimpleSchemaVisitor, self).visitChildren(ctx)

        results = self._stack[prev_num_stack_items:]

        self._stack = self._stack[:prev_num_stack_items]

        return results

    # ----------------------------------------------------------------------
    def _OnProgress(
        self,
        end_line: int,
    ):
        if end_line > self._current_line:
            self._current_line = end_line
            self._on_progress_func(self._current_line)


# ----------------------------------------------------------------------
class _Visitor(SimpleSchemaVisitor, _VisitorMixin):
    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        _VisitorMixin.__init__(self, *args, **kwargs)

    # ----------------------------------------------------------------------
    # |  Common
    # ----------------------------------------------------------------------
    def visitIdentifier(self, ctx:SimpleSchemaParser.IdentifierContext):
        id_value = ctx.IDENTIFIER().symbol.text
        id_range = self.CreateRange(ctx)

        self._stack.append(ParseIdentifier(id_range, id_value))

    # ----------------------------------------------------------------------
    def visitMetadata_clause(self, ctx:SimpleSchemaParser.Metadata_clauseContext):
        children = self._GetChildren(ctx)
        assert all(isinstance(child, MetadataItem) for child in children), children

        self._stack.append(Metadata(self.CreateRange(ctx), cast(list[MetadataItem], children)))

    # ----------------------------------------------------------------------
    def visitMetadata_clause_item(self, ctx:SimpleSchemaParser.Metadata_clause_itemContext):
        children = self._GetChildren(ctx)

        assert len(children) == 2, children
        assert isinstance(children[0], ParseIdentifier), children
        assert isinstance(children[1], Expression), children

        name = SimpleElement(children[0].range, children[0].value)
        value_expression = children[1]

        self._stack.append(MetadataItem(self.CreateRange(ctx), name, value_expression))

    # ----------------------------------------------------------------------
    def visitCardinality_clause(self, ctx:SimpleSchemaParser.Cardinality_clauseContext):
        children = self._GetChildren(ctx)

        assert len(children) == 2, children

        assert isinstance(children[0], IntegerExpression), children
        min_expression = cast(IntegerExpression, children[0])

        assert children[1] is None or isinstance(children[1], IntegerExpression), children
        max_expression = cast(Optional[IntegerExpression], children[1])

        self._stack.append(
            Cardinality(self.CreateRange(ctx), min_expression, max_expression),
        )

    # ----------------------------------------------------------------------
    def visitCardinality_clause_optional(self, ctx:SimpleSchemaParser.Cardinality_clause_optionalContext):
        range_value = self.CreateRange(ctx)

        self._stack += [
            IntegerExpression(range_value, 0),
            IntegerExpression(range_value, 1),
        ]

    # ----------------------------------------------------------------------
    def visitCardinality_clause_zero_or_more(self, ctx:SimpleSchemaParser.Cardinality_clause_zero_or_moreContext):
        range_value = self.CreateRange(ctx)

        self._stack += [
            IntegerExpression(range_value, 0),
            None,
        ]

    # ----------------------------------------------------------------------
    def visitCardinality_clause_one_or_more(self, ctx:SimpleSchemaParser.Cardinality_clause_one_or_moreContext):
        range_value = self.CreateRange(ctx)

        self._stack += [
            IntegerExpression(range_value, 1),
            None,
        ]

    # ----------------------------------------------------------------------
    def visitCardinality_clause_fixed(self, ctx:SimpleSchemaParser.Cardinality_clause_fixedContext):
        children = self._GetChildren(ctx)
        assert len(children) == 1, children
        assert isinstance(children[0], IntegerExpression), children

        # There have to be 2 distinct IntegerExpression objects so that the parent
        # can be set for each.
        self._stack += [
            children[0],
            IntegerExpression(children[0].range, children[0].value),
        ]

    # ----------------------------------------------------------------------
    # |  Expressions
    # ----------------------------------------------------------------------
    def visitNumber_expression(self, ctx:SimpleSchemaParser.Number_expressionContext):
        self._stack.append(NumberExpression(self.CreateRange(ctx), float(ctx.NUMBER().symbol.text)))

    # ----------------------------------------------------------------------
    def visitInteger_expression(self, ctx:SimpleSchemaParser.Integer_expressionContext):
        self._stack.append(IntegerExpression(self.CreateRange(ctx), int(ctx.INTEGER().symbol.text)))

    # ----------------------------------------------------------------------
    def visitTrue_expression(self, ctx:SimpleSchemaParser.True_expressionContext):
        self._stack.append(BooleanExpression(self.CreateRange(ctx), True))

    # ----------------------------------------------------------------------
    def visitFalse_expression(self, ctx:SimpleSchemaParser.False_expressionContext):
        self._stack.append(BooleanExpression(self.CreateRange(ctx), False))

    # ----------------------------------------------------------------------
    def visitNone_expression(self, ctx:SimpleSchemaParser.None_expressionContext):
        self._stack.append(NoneExpression(self.CreateRange(ctx)))

    # ----------------------------------------------------------------------
    def visitString_expression(self, ctx:SimpleSchemaParser.String_expressionContext):
        context = ctx

        while not isinstance(context, antlr4.TerminalNode):
            assert len(context.children) == 1
            context = context.children[0]

        token = context.symbol              # type: ignore
        value = token.text                  # type: ignore

        # At the very least, we should have a beginning and ending quote
        assert len(value) >= 2

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
                    else:
                        raise AntlrException(
                            Errors.antlr_invalid_indentation,
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
                    Errors.antlr_invalid_opening_token,
                    self.filename,
                    ctx.start.line,
                    ctx.start.column + 1 + 3,
                    None,
                )

            final_line = lines[-1]
            if len(TrimPrefix(final_line, len(lines))) != 3:
                raise AntlrException(
                    Errors.antlr_invalid_closing_token,
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

        self._stack.append(StringExpression(self.CreateRange(ctx), value))

    # ----------------------------------------------------------------------
    def visitList_expression(self, ctx:SimpleSchemaParser.List_expressionContext):
        children = self._GetChildren(ctx)
        assert all(isinstance(child, Expression) for child in children), children

        self._stack.append(ListExpression(self.CreateRange(ctx), cast(list[Expression], children)))

    # ----------------------------------------------------------------------
    def visitTuple_expression(self, ctx:SimpleSchemaParser.Tuple_expressionContext):
        children = self._GetChildren(ctx)
        assert all(isinstance(child, Expression) for child in children), children

        self._stack.append(TupleExpression(self.CreateRange(ctx), cast(tuple[Expression], tuple(children))))

    # ----------------------------------------------------------------------
    # |  Statements
    # ----------------------------------------------------------------------
    def visitInclude_statement(self, ctx:SimpleSchemaParser.Include_statementContext):
        children = self._GetChildren(ctx)
        assert len(children) >= 1, children

        range_value = self.CreateRange(ctx)

        filename = children.pop(0)

        if isinstance(filename, ParseIncludeStatementItem):
            children = [filename, ]
            filename = SimpleElement(range_value, self.filename.parent)

        assert isinstance(filename, SimpleElement) and isinstance(filename.value, Path), filename

        if len(children) == 1 and isinstance(children[0], str) and children[0] == "*":
            children = []
            is_star = True
        else:
            assert all(isinstance(child, ParseIncludeStatementItem) for child in children), children
            children = cast(list[ParseIncludeStatementItem], children)

            is_star = False

        self._stack.append(
            self._create_include_statement_func(
                self.filename,
                self.CreateRange(ctx),
                filename,
                children,
                is_star_include=is_star,
            ),
        )

    # ----------------------------------------------------------------------
    def visitInclude_statement_filename(self, ctx:SimpleSchemaParser.Include_statement_filenameContext):
        self._stack.append(
            SimpleElement(
                self.CreateRange(ctx),
                Path(ctx.INCLUDE_FILENAME().symbol.text),
            ),
        )

    # ----------------------------------------------------------------------
    def visitInclude_statement_star(self, ctx:SimpleSchemaParser.Include_statement_starContext):  # pylint: disable=unused-argument
        self._stack.append("*")

    # ----------------------------------------------------------------------
    def visitInclude_statement_element(self, ctx:SimpleSchemaParser.Include_statement_elementContext):
        children = self._GetChildren(ctx)

        num_children = len(children)
        assert 1 <= num_children <= 2, children

        assert isinstance(children[0], ParseIdentifier), children
        element_name = cast(ParseIdentifier, children[0])

        if num_children > 1:
            assert isinstance(children[1], ParseIdentifier), children
            reference_name = children[1]
        else:
            reference_name = ParseIdentifier(element_name.range, element_name.value)

        self._stack.append(ParseIncludeStatementItem(self.CreateRange(ctx), element_name, reference_name))

    # ----------------------------------------------------------------------
    def visitExtension_statement(self, ctx:SimpleSchemaParser.Extension_statementContext):
        children = self._GetChildren(ctx)

        num_children = len(children)
        assert 1 <= num_children <= 3, children

        assert isinstance(children[0], ParseIdentifier), children
        name = children[0].ToSimpleElement()

        positional_args: Optional[list[Element]] = None
        keyword_args: Optional[list[ExtensionStatementKeywordArg]] = None

        for index in range(1, num_children):
            child = children[index]
            assert isinstance(child, list) and child, child

            if isinstance(child[0], ExtensionStatementKeywordArg):
                assert keyword_args is None, (keyword_args, child)
                keyword_args = child
            else:
                assert positional_args is None, (positional_args, None)
                positional_args = child

        self._stack.append(
            ExtensionStatement(
                self.CreateRange(ctx),
                name,
                cast(list[Expression], positional_args or []),
                keyword_args or [],
            ),
        )

    # ----------------------------------------------------------------------
    def visitExtension_statement_positional_args(self, ctx:SimpleSchemaParser.Extension_statement_positional_argsContext):
        children = self._GetChildren(ctx)
        assert all(isinstance(child, Element) for child in children), children

        self._stack.append(children)

    # ----------------------------------------------------------------------
    def visitExtension_statement_keyword_args(self, ctx:SimpleSchemaParser.Extension_statement_keyword_argsContext):
        children = self._GetChildren(ctx)
        assert all(isinstance(child, ExtensionStatementKeywordArg) for child in children), children

        self._stack.append(children)

    # ----------------------------------------------------------------------
    def visitExtension_statement_keyword_arg(self, ctx:SimpleSchemaParser.Extension_statement_keyword_argContext):
        children = self._GetChildren(ctx)

        assert len(children) == 2, children
        assert isinstance(children[0], ParseIdentifier), children
        assert isinstance(children[1], Expression), children

        self._stack.append(
            ExtensionStatementKeywordArg(
                self.CreateRange(ctx),
                children[0].ToSimpleElement(),
                children[1],
            ),
        )

    # ----------------------------------------------------------------------
    def visitParse_item_statement(self, ctx:SimpleSchemaParser.Parse_item_statementContext):
        children = self._GetChildren(ctx)
        assert len(children) == 2

        assert isinstance(children[0], ParseIdentifier), children
        assert isinstance(children[1], ParseType), children

        self._stack.append(ParseItemStatement(self.CreateRange(ctx), children[0], children[1]))

    # ----------------------------------------------------------------------
    def visitParse_structure_statement(self, ctx:SimpleSchemaParser.Parse_structure_statementContext):
        children = self._GetChildren(ctx)

        num_children = len(children)
        assert num_children >= 1

        assert isinstance(children[0], ParseIdentifier), children
        name = children[0]

        bases: list[ParseIdentifierType] = []
        cardinality: Optional[Cardinality] = None
        metadata: Optional[Metadata] = None
        statements: list[Statement] = []

        for index in range(1, num_children):
            child = children[index]

            if isinstance(child, ParseType):
                if isinstance(child, ParseIdentifierType):
                    bases.append(child)
                else:
                    raise Errors.ParseStructureStatementInvalidBase.Create(child.range)

            elif isinstance(child, Cardinality):
                assert cardinality is None, (cardinality, child)
                cardinality = child

            elif isinstance(child, Metadata):
                assert metadata is None, (metadata, child)
                metadata = child

            elif isinstance(child, Statement):
                statements.append(child)

            else:
                assert False, child  # pragma: no cover

        range_value = self.CreateRange(ctx)

        if cardinality is None:
            cardinality = Cardinality(range_value, None, None)

        self._stack.append(
            ParseStructureStatement(
                range_value,
                name,
                bases or None,
                cardinality,
                metadata,
                statements,
            ),
        )

    # ----------------------------------------------------------------------
    def visitParse_structure_simplified_statement(self, ctx:SimpleSchemaParser.Parse_structure_simplified_statementContext):
        children = self._GetChildren(ctx)
        assert len(children) == 2
        assert isinstance(children[0], ParseIdentifier), children
        assert isinstance(children[1], Metadata), children

        range_value = self.CreateRange(ctx)

        self._stack.append(
            ParseStructureStatement(
                range_value,
                children[0],
                None,
                Cardinality(range_value, None, None),
                children[1],
                [],
            ),
        )

    # ----------------------------------------------------------------------
    # |  Types
    # ----------------------------------------------------------------------
    def visitParse_type(self, ctx:SimpleSchemaParser.Parse_typeContext):
        children = self._GetChildren(ctx)

        num_children = len(children)
        assert 1 <= num_children <= 3

        assert callable(children[0]), children
        create_func = cast(
            Callable[
                [
                    Range,
                    Cardinality,
                    Optional[Metadata],
                ],
                ParseType,
            ],
            children[0],
        )

        metadata: Optional[Metadata] = None
        cardinality: Optional[Cardinality] = None

        for index in range(1, num_children):
            child = children[index]

            if isinstance(child, Metadata):
                assert metadata is None, (metadata, child)
                metadata = child
            elif isinstance(child, Cardinality):
                assert cardinality is None, (cardinality, child)
                cardinality = child
            else:
                assert False, child  # pragma: no cover

        range_value = self.CreateRange(ctx)

        if cardinality is None:
            cardinality = Cardinality(range_value, None, None)

        self._stack.append(create_func(range_value, cardinality, metadata))

    # ----------------------------------------------------------------------
    def visitParse_identifier_type(self, ctx:SimpleSchemaParser.Parse_identifier_typeContext):
        children = self._GetChildren(ctx)
        assert len(children) >= 1, children

        identifiers: list[ParseIdentifier] = []
        is_global: Optional[Range] = None
        is_item: Optional[Range] = None

        for child_index, child in enumerate(children):
            if isinstance(child, ParseIdentifier):
                identifiers.append(child)

            elif isinstance(child, Range):
                # The global identifier comes before any identifiers and the item identifier comes
                # after, so it is enough to look at the child index to determine which one this
                # range value refers to.
                if child_index == 0:
                    assert is_global is None, (is_global, child)
                    is_global = child
                else:
                    assert is_item is None, (is_item, child)
                    is_item = child

            else:
                assert False, child  # pragma: no cover

        assert identifiers, children

        self._stack.append(
            lambda range_value, cardinality, metadata: ParseIdentifierType(
                range_value,
                cardinality,
                metadata,
                identifiers,
                is_global,
                is_item,
            ),
        )

    # ----------------------------------------------------------------------
    def visitParse_identifier_type_global(self, ctx:SimpleSchemaParser.Parse_identifier_type_globalContext):
        # It is enough to add a range value, as that will signal that the modifier exists when
        # creating the type.
        self._stack.append(self.CreateRange(ctx))

    # ----------------------------------------------------------------------
    def visitParse_identifier_type_item(self, ctx:SimpleSchemaParser.Parse_identifier_type_itemContext):
        # It is enough to add a range value, as that will signal that the modifier exists when
        # creating the type.
        self._stack.append(self.CreateRange(ctx))

    # ----------------------------------------------------------------------
    def visitParse_tuple_type(self, ctx:SimpleSchemaParser.Parse_tuple_typeContext):
        children = self._GetChildren(ctx)
        assert children
        assert all(isinstance(child, ParseType) for child in children), children

        self._stack.append(
            lambda range_value, cardinality, metadata: ParseTupleType(
                range_value,
                cardinality,
                metadata,
                cast(list[ParseType], children),
            ),
        )

    # ----------------------------------------------------------------------
    def visitParse_variant_type(self, ctx:SimpleSchemaParser.Parse_variant_typeContext):
        children = self._GetChildren(ctx)
        assert children
        assert all(isinstance(child, ParseType) for child in children), children

        self._stack.append(
            lambda range_value, cardinality, metadata: ParseVariantType(
                range_value,
                cardinality,
                metadata,
                cast(list[ParseType], children),
            ),
        )
