# ----------------------------------------------------------------------
# |
# |  __init__.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-12-20 15:06:41
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
import itertools
import sys
import threading

from pathlib import Path
from typing import Any, Callable, cast, Dict, List, Optional, Protocol, Tuple, Union

import antlr4

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Streams.DoneManager import DoneManager

from Common_FoundationEx import ExecuteTasks

from SimpleSchema.Schema.Elements.Common.Cardinality import Cardinality
from SimpleSchema.Schema.Elements.Common.Element import SimpleElement
from SimpleSchema.Schema.Elements.Common.Identifier import Visibility
from SimpleSchema.Schema.Elements.Common.Location import Location
from SimpleSchema.Schema.Elements.Common.Metadata import Metadata, MetadataItem
from SimpleSchema.Schema.Elements.Common.Range import Range

from SimpleSchema.Schema.Elements.Common.Element import Element
from SimpleSchema.Schema.Elements.Common.Identifier import Identifier
from SimpleSchema.Schema.Elements.Common.SimpleSchemaException import SimpleSchemaException

from SimpleSchema.Schema.Elements.Expressions.BooleanExpression import BooleanExpression
from SimpleSchema.Schema.Elements.Expressions.Expression import Expression
from SimpleSchema.Schema.Elements.Expressions.IntegerExpression import IntegerExpression
from SimpleSchema.Schema.Elements.Expressions.ListExpression import ListExpression
from SimpleSchema.Schema.Elements.Expressions.NumberExpression import NumberExpression
from SimpleSchema.Schema.Elements.Expressions.StringExpression import StringExpression

from SimpleSchema.Schema.Elements.Statements.ExtensionStatement import ExtensionStatement, ExtensionStatementKeywordArg
from SimpleSchema.Schema.Elements.Statements.RootStatement import RootStatement
from SimpleSchema.Schema.Elements.Statements.Statement import Statement

from SimpleSchema.Schema.Parse.ParseElements.Statements.ParseIncludeStatement import ParseIncludeStatement, ParseIncludeStatementItem, ParseIncludeStatementType
from SimpleSchema.Schema.Parse.ParseElements.Statements.ParseItemStatement import ParseItemStatement
from SimpleSchema.Schema.Parse.ParseElements.Statements.ParseStructureStatement import ParseStructureStatement

from SimpleSchema.Schema.Parse.ParseElements.Types.ParseIdentifierType import ParseIdentifierType
from SimpleSchema.Schema.Parse.ParseElements.Types.ParseTupleType import ParseTupleType
from SimpleSchema.Schema.Parse.ParseElements.Types.ParseType import ParseType
from SimpleSchema.Schema.Parse.ParseElements.Types.ParseVariantType import ParseVariantType


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
        location = Location(line, column)

        super(AntlrException, self).__init__(
            "{msg} ({source} {location})".format(
                msg=msg,
                source=source,
                location=location.ToString(),
            ),
        )

        self.source                         = source
        self.location                       = location
        self.ex                             = ex


# ----------------------------------------------------------------------
# |
# |  Public Functions
# |
# ----------------------------------------------------------------------
def Parse(
    dm: DoneManager,
    workspaces: Dict[
        Path,                               # workspace root
        Dict[
            Path,                           # relative path
            Callable[[], str],              # content
        ],
    ],
    *,
    single_threaded: bool=False,
    quiet: bool=False,
    raise_if_single_exception: bool=True,
) -> Dict[
    Path,                                   # workspace root
    Dict[
        Path,                               # relative path
        Union[Exception, RootStatement],
    ],
]:
    workspace_names: List[Path] = [workspace.resolve() for workspace in workspaces]
    workspace_names.sort(
        key=lambda value: len(str(value)),
        reverse=True,
    )

    filenames: Dict[
        Path,                               # workspace root
        Dict[
            Path,                           # relative path
            Union[None, Exception, RootStatement],
        ]
    ] = {}

    with ExecuteTasks.YieldQueueExecutor(
        dm,
        "Parsing...",
        quiet=quiet,
        max_num_threads=1 if single_threaded else None,
    ) as enqueue_func:
        filenames_lock = threading.Lock()

        # ----------------------------------------------------------------------
        def ResolveIncludeFilename(
            path: Path,
        ) -> Optional[Path]:
            path = path.resolve()

            if path.is_file():
                return path

            path = path.parent / (path.name + ".SimpleSchema")

            if path.is_file():
                return path

            return None

        # ----------------------------------------------------------------------
        def CreateIncludeStatement(
            including_filename: Path,
            range_value: Range,
            filename_or_directory: SimpleElement[Path],
            items: List[ParseIncludeStatementItem],
            *,
            is_star_include: bool,
        ) -> ParseIncludeStatement:
            # Get the filename
            root: Optional[Path] = None

            for potential_root in itertools.chain(
                [including_filename.parent, ],
                workspace_names,
            ):
                fullpath = (potential_root / filename_or_directory.value).resolve()

                if fullpath.exists():
                    root = fullpath
                    break

                fullpath = ResolveIncludeFilename(fullpath)
                if fullpath is not None:
                    root = fullpath
                    break

            if root is None:
                raise SimpleSchemaException(
                    "'{}' is not a recognized file or directory.".format(filename_or_directory.value),
                    filename_or_directory.range,
                )

            filename: Optional[Path] = None
            filename_range: Optional[Range] = None

            if root.is_dir():
                if is_star_include:
                    raise SimpleSchemaException(
                        "Filenames must be provided when using wildcard imports; '{}' is a directory.".format(root),
                        range_value,
                    )

                if len(items) != 1:
                    raise SimpleSchemaException(
                        "A single filename must be imported when including content from a directory.",
                        items[1].range,
                    )

                filename = ResolveIncludeFilename(root / items[0].element_name.id.value)
                filename_range = Range(
                    filename_or_directory.range.filename,
                    filename_or_directory.range.begin,
                    items[0].element_name.id.range.end,
                )

                if filename is None:
                    raise SimpleSchemaException(
                        "'{}' is not a recognized filename.".format(items[0].element_name.id.value),
                        filename_range,
                    )

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

            assert filename is not None and filename.is_file(), filename

            # Get the workspace for this file
            workspace: Optional[Path] = None

            for workspace_name in workspace_names:
                if PathEx.IsDescendant(filename, workspace_name):
                    workspace = workspace_name
                    break

            if workspace is None:
                raise SimpleSchemaException(
                    "The included file '{}' is not a descendant of any workspace.".format(filename),
                    range_value,
                )

            # Get the relative path
            relative_path = PathEx.CreateRelativePath(workspace, filename)
            assert relative_path is not None

            relative_path = cast(Path, relative_path)

            # Determine if the file should be enqueued
            should_enqueue = False

            with filenames_lock:
                workspace_items = filenames[workspace]

                if relative_path not in workspace_items:
                    workspace_items[relative_path] = None
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

                    with filenames_lock:
                        assert filenames[workspace_root][relative_path] is None, (workspace_root, relative_path)
                        filenames[workspace_root][relative_path] = result

                # ----------------------------------------------------------------------

                with ExitStack(OnExit):
                    fullpath = workspace_root / relative_path

                    try:
                        # Parse the object
                        antlr_stream = antlr4.InputStream(content)

                        lexer = SimpleSchemaLexer(antlr_stream)
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

        with filenames_lock:
            is_single_workspace = len(workspaces) == 1

            for workspace_root, sources in workspaces.items():
                these_filenames: Dict[Path, Union[None, Exception, RootStatement]] = {}

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

                    these_filenames[relative_path] = None

                filenames[workspace_root] = these_filenames

    if dm.result != 0 and raise_if_single_exception:
        exceptions: List[Exception] = []

        for workspace_values in filenames.values():
            for result in workspace_values.values():
                if isinstance(result, Exception):
                    exceptions.append(result)

        if len(exceptions) == 1:
            raise exceptions[0]

    for workspace_root, workspace_values in filenames.items():
        for relative_path, result in workspace_values.items():
            assert result is not None, (workspace_root, relative_path)

    return cast(Dict[Path, Dict[Path, Union[Exception, RootStatement]]], filenames)


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
    ) -> Any:
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
            items: List[ParseIncludeStatementItem],
            *,
            is_star_include: bool,
        ) -> ParseIncludeStatement:
            ...

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
        self._stack: List[Any]              = []

    # ----------------------------------------------------------------------
    @functools.cached_property
    def root(self) -> RootStatement:
        assert all(isinstance(item, Statement) for item in self._stack)

        if not self._stack:
            range_value = Range(self.filename, Location(1, 1), Location(1, 1))
        else:
            range_value = Range(self.filename, self._stack[0].range.begin, self._stack[-1].range.end)

        return RootStatement(range_value, cast(List[Statement], self._stack))

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

        return Range.Create(
            self.filename,
            ctx.start.line,
            ctx.start.column + 1,
            stop_line,
            stop_col + 1,
        )

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
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
class _Visitor(SimpleSchemaVisitor, _VisitorMixin):
    # ----------------------------------------------------------------------
    def __init__(self, *args, **kwargs):
        _VisitorMixin.__init__(self, *args, **kwargs)

    # ----------------------------------------------------------------------
    def visitIdentifier(self, ctx:SimpleSchemaParser.IdentifierContext):
        id_value = ctx.IDENTIFIER().symbol.text
        id_range = self.CreateRange(ctx)

        if id_value.startswith("_"):
            visibility = Visibility.Private
            visibility_range = Range(
                id_range.filename,
                id_range.begin,
                Location(id_range.begin.line, id_range.begin.column + 1),
            )

        elif id_value[0] in ["@", "$", "&"]:
            visibility = Visibility.Protected
            visibility_range = Range(
                id_range.filename,
                id_range.begin,
                Location(id_range.begin.line, id_range.begin.column + 1),
            )

        else:
            visibility = Visibility.Public
            visibility_range = id_range

        self._stack.append(
            Identifier(
                self.CreateRange(ctx),
                SimpleElement[str](id_range, id_value),
                SimpleElement[Visibility](visibility_range, visibility),
            ),
        )

    # ----------------------------------------------------------------------
    def visitCardinality_clause_optional(self, ctx:SimpleSchemaParser.Cardinality_clause_optionalContext):
        range_value = self.CreateRange(ctx)

        self._stack.append(
            Cardinality(
                range_value,
                IntegerExpression(range_value, 0),
                IntegerExpression(range_value, 1),
                None, # TODO: No metadata yet
            ),
        )

    # ----------------------------------------------------------------------
    def visitCardinality_clause_zero_or_more(self, ctx:SimpleSchemaParser.Cardinality_clause_zero_or_moreContext):
        range_value = self.CreateRange(ctx)

        self._stack.append(
            Cardinality(
                range_value,
                IntegerExpression(range_value, 0),
                None,
                None, # TODO: No metadata yet
            ),
        )

    # ----------------------------------------------------------------------
    def visitCardinality_clause_one_or_more(self, ctx:SimpleSchemaParser.Cardinality_clause_one_or_moreContext):
        range_value = self.CreateRange(ctx)

        self._stack.append(
            Cardinality(
                range_value,
                IntegerExpression(range_value, 1),
                None,
                None, # TODO: No metadata yet
            ),
        )

    # ----------------------------------------------------------------------
    def visitCardinality_clause_fixed(self, ctx:SimpleSchemaParser.Cardinality_clause_fixedContext):
        children = self._GetChildren(ctx)

        assert len(children) == 1, children
        assert isinstance(children[0], IntegerExpression), children

        value_expression = cast(IntegerExpression, children[0])

        self._stack.append(
            Cardinality(
                self.CreateRange(ctx),
                value_expression,
                value_expression,
                None, # TODO: No metadata yet
            ),
        )

    # ----------------------------------------------------------------------
    def visitCardinality_clause_range(self, ctx:SimpleSchemaParser.Cardinality_clause_rangeContext):
        children = self._GetChildren(ctx)

        assert len(children) == 2, children
        assert all(isinstance(child, IntegerExpression) for child in children), children

        min_expression = cast(IntegerExpression, children[0])
        max_expression = cast(IntegerExpression, children[1])

        self._stack.append(
            Cardinality(
                self.CreateRange(ctx),
                min_expression,
                max_expression,
                None, # TODO: No metadata yet
            ),
        )

    # ----------------------------------------------------------------------
    def visitMetadata_clause(self, ctx:SimpleSchemaParser.Metadata_clauseContext):
        children = self._GetChildren(ctx)
        assert all(isinstance(child, MetadataItem) for child in children), children

        metadata_items = cast(List[MetadataItem], children)

        self._stack.append(Metadata(self.CreateRange(ctx), metadata_items))

    # ----------------------------------------------------------------------
    def visitMetadata_clause_item(self, ctx:SimpleSchemaParser.Metadata_clause_itemContext):
        children = self._GetChildren(ctx)

        assert len(children) == 2, children
        assert isinstance(children[0], Identifier), children
        assert isinstance(children[1], Expression), children

        name = cast(Identifier, children[0])
        if not name.is_expression:
            raise SimpleSchemaException(
                "'{}' is not a valid expression; identifier expressions must begin with a lowercase letter.".format(name.id.value),
                name.id.range,
            )

        value_expression = cast(Expression, children[1])

        self._stack.append(MetadataItem(self.CreateRange(ctx), name, value_expression))

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
    def visitBasic_string_expression(self, ctx:SimpleSchemaParser.Basic_string_expressionContext):
        self.visitString_expression(ctx)

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
                    "Triple-quote delimiters that initiate multiline strings cannot have any content on the same line.",
                    self.filename,
                    ctx.start.line,
                    ctx.start.column + 1 + 3,
                    None,
                )

            final_line = lines[-1]
            if len(TrimPrefix(final_line, len(lines))) != 3:
                raise AntlrException(
                    "Triple-quote delimiters that terminate multiline strings cannot have any content on the same line.",
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
        assert all(isinstance(child, Expression) for child in children)

        items = cast(List[Expression], children)

        self._stack.append(ListExpression(self.CreateRange(ctx), items))

    # ----------------------------------------------------------------------
    def visitInclude_statement(self, ctx:SimpleSchemaParser.Include_statementContext):
        children = self._GetChildren(ctx)
        assert len(children) >= 2, children

        filename = children.pop(0)
        assert isinstance(filename, SimpleElement) and isinstance(filename.value, Path), filename

        if len(children) == 1 and children[0] == "*":
            children = []
            is_star = True
        else:
            assert all(isinstance(child, ParseIncludeStatementItem) for child in children), children
            children = cast(List[ParseIncludeStatementItem], children)

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
    def visitInclude_statement_star(self, ctx:SimpleSchemaParser.Include_statement_starContext):
        self._stack.append("*")

    # ----------------------------------------------------------------------
    def visitInclude_statement_element(self, ctx:SimpleSchemaParser.Include_statement_elementContext):
        children = self._GetChildren(ctx)

        num_children = len(children)
        assert 1 <= num_children <= 2

        assert isinstance(children[0], Identifier), children[0]
        element_name = children[0]

        reference_name: Optional[Identifier] = None

        if num_children > 1:
            assert isinstance(children[1], Identifier), children[1]
            reference_name = children[1]

        self._stack.append(ParseIncludeStatementItem(self.CreateRange(ctx), element_name, reference_name))

    # ----------------------------------------------------------------------
    def visitExtension_statement(self, ctx:SimpleSchemaParser.Extension_statementContext):
        children = self._GetChildren(ctx)

        num_children = len(children)
        assert 1 <= num_children <= 3, children

        assert isinstance(children[0], Identifier), children
        name = cast(Identifier, children[0])

        positional_args: Optional[List[Element]] = None
        keyword_args: Optional[List[ExtensionStatementKeywordArg]] = None

        for index in range(1, num_children):
            child = children[index]
            assert isinstance(child, list) and child, child

            if isinstance(child[0], ExtensionStatementKeywordArg):
                assert keyword_args is None, (keyword_args, child)
                keyword_args = child
            else:
                assert positional_args is None, (positional_args, child)
                positional_args = child

        self._stack.append(
            ExtensionStatement(
                self.CreateRange(ctx),
                name,
                positional_args or [],
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
        assert isinstance(children[0], Identifier), children
        assert isinstance(children[1], Expression), children

        name = cast(Identifier, children[0])
        value = cast(Expression, children[1])

        self._stack.append(ExtensionStatementKeywordArg(self.CreateRange(ctx), name, value))

    # ----------------------------------------------------------------------
    def visitItem_statement(self, ctx:SimpleSchemaParser.Item_statementContext):
        children = self._GetChildren(ctx)
        assert len(children) == 2

        name = cast(Identifier, children[0])
        the_type = cast(ParseType, children[1])

        self._stack.append(ParseItemStatement(self.CreateRange(ctx), name, the_type))

    # ----------------------------------------------------------------------
    def visitStructure_statement(self, ctx:SimpleSchemaParser.Structure_statementContext):
        children = self._GetChildren(ctx)

        num_children = len(children)
        assert 2 <= num_children <= 4, children

        assert isinstance(children[0], Identifier), children
        name = cast(Identifier, children[0])

        base_type: Optional[ParseType] = None
        cardinality: Optional[Cardinality] = None
        metadata: Optional[Metadata] = None
        statements: Optional[List[Statement]] = None

        for index in range(1, num_children):
            child = children[index]

            if isinstance(child, ParseType):
                assert base_type is None, (base_type, child)
                base_type = child
            elif isinstance(child, Cardinality):
                assert cardinality is None, (cardinality, child)
                cardinality = child
            elif isinstance(child, Metadata):
                assert metadata is None, (metadata, child)
                metadata = child
            elif isinstance(child, list):
                assert statements is None, (statements, child)
                statements = child
            else:
                assert False, child  # pragma: no cover

        range_value = self.CreateRange(ctx)

        # If we have a base class, extract the cardinality and metadata from that object and add it
        # to this one.
        if base_type is not None:
            assert cardinality is None, cardinality
            assert metadata is None, metadata

            if (
                (base_type.cardinality and not base_type.cardinality.is_single)
                or base_type.metadata
            ):
                cardinality = base_type.cardinality
                metadata = base_type.metadata

                # Update the base_type's info

                # This isn't perfect, as the updated range will include any whitespace
                # that separates the type information and the cardinality/metadata.
                object.__setattr__(base_type.range, "end", (cardinality or metadata).range.begin)

                object.__setattr__(
                    base_type,
                    "cardinality",
                    Cardinality(
                        base_type.range,
                        IntegerExpression(base_type.range, 1),
                        IntegerExpression(base_type.range, 1),
                        None,
                    ),
                )

                object.__setattr__(base_type, "metadata", None)

                # Update the current range to account for the new info
                object.__setattr__(range_value, "end", (metadata or cardinality).range.end)

        assert statements is not None, children

        if cardinality is None:
            cardinality = Cardinality(range_value, None, None, None)

        self._stack.append(
            ParseStructureStatement(
                range_value,
                name,
                base_type,
                cardinality,
                metadata,
                statements,
            ),
        )

    # ----------------------------------------------------------------------
    def visitStructure_statement_single_line(
        self,
        ctx:SimpleSchemaParser.Structure_statement_single_lineContext,  # pylint: disable=unused-argument
    ):
        # Single line implies pass, so there are no statements
        self._stack.append([])

    # ----------------------------------------------------------------------
    def visitStructure_statement_multi_line(self, ctx:SimpleSchemaParser.Structure_statement_multi_lineContext):
        children = self._GetChildren(ctx)
        assert all(isinstance(child, Statement) for child in children), children

        self._stack.append(children)

    # ----------------------------------------------------------------------
    def visitParse_identifier_type(self, ctx:SimpleSchemaParser.Parse_identifier_typeContext):
        children = self._GetChildren(ctx)

        assert len(children) >= 1, children

        identifiers: List[Identifier] = []
        identifier_type_element: Optional[Range] = None
        cardinality: Optional[Cardinality] = None
        metadata: Optional[Metadata] = None

        for child in children:
            if isinstance(child, Identifier):
                identifiers.append(child)
            elif isinstance(child, Range):
                assert identifier_type_element is None, (identifier_type_element, child)
                identifier_type_element = child
            elif isinstance(child, Cardinality):
                assert cardinality is None, (cardinality, child)
                cardinality = child
            elif isinstance(child, Metadata):
                assert metadata is None, (metadata, child)
                metadata = child
            else:
                assert False, child  # pragma: no cover

        assert identifiers, children

        range_value = self.CreateRange(ctx)

        if cardinality is None:
            cardinality = Cardinality(range_value, None, None, None)

        self._stack.append(
            ParseIdentifierType(range_value, cardinality, metadata, identifiers, identifier_type_element),
        )

    # ----------------------------------------------------------------------
    def visitParse_identifier_type_element(self, ctx:SimpleSchemaParser.Parse_identifier_type_elementContext):
        # It is enough to add a range value as that will signal that the modifier exists when
        # creating the IdentifierType.
        self._stack.append(self.CreateRange(ctx))

    # ----------------------------------------------------------------------
    def visitParse_tuple_type(self, ctx:SimpleSchemaParser.Parse_tuple_typeContext):
        children = self._GetChildren(ctx)

        types: List[ParseType] = []
        cardinality: Optional[Cardinality] = None
        metadata: Optional[Metadata] = None

        for child in children:
            if isinstance(child, ParseType):
                types.append(child)
            elif isinstance(child, Cardinality):
                assert cardinality is None, (cardinality, child)
                cardinality = child
            elif isinstance(child, Metadata):
                assert metadata is None, (metadata, child)
                metadata = child
            else:
                assert False, child  # pragma: no cover

        assert types

        range_value = self.CreateRange(ctx)

        if cardinality is None:
            cardinality = Cardinality(range_value, None, None, None)

        self._stack.append(ParseTupleType(range_value, cardinality, metadata, types))

    # ----------------------------------------------------------------------
    def visitParse_variant_type(self, ctx:SimpleSchemaParser.Parse_variant_typeContext):
        children = self._GetChildren(ctx)

        types: List[ParseType] = []
        cardinality: Optional[Cardinality] = None
        metadata: Optional[Metadata] = None

        for child in children:
            if isinstance(child, ParseType):
                types.append(child)
            elif isinstance(child, Cardinality):
                assert cardinality is None, (cardinality, child)
                cardinality = child
            elif isinstance(child, Metadata):
                assert metadata is None, (metadata, child)
                metadata = child
            else:
                assert False, child  # pragma: no cover

        assert types

        range_value = self.CreateRange(ctx)

        if cardinality is None:
            cardinality = Cardinality(range_value, None, None, None)

        self._stack.append(ParseVariantType(range_value, cardinality, metadata, types))
