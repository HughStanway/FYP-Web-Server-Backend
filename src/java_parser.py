import logging
import os
import subprocess
import tempfile
from exceptions import JavaFormatterError

from antlr4 import *

from antlr.JavaLexer import JavaLexer
from antlr.JavaParser import JavaParser
from antlr.JavaParserListener import JavaParserListener


class MethodExtractor(JavaParserListener):
    def __init__(self):
        self.methods = []

    def format_java_method(self, method_code: str) -> str:
        with tempfile.NamedTemporaryFile(
            mode="w+", suffix=".java", delete=False
        ) as tmp:
            tmp.write(method_code)
            tmp_path = tmp.name

        result = subprocess.run(
            ["npx", "prettier", "--plugin=prettier-plugin-java", "--write", tmp_path],
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            os.unlink(tmp_path)
            raise JavaFormatterError(f"Prettier failed: {result.stderr}")

        with open(tmp_path, "r") as f:
            formatted_code = f.read().strip()

        logging.info("Method formatted successfully")
        os.unlink(tmp_path)
        return formatted_code

    def enterMethodDeclaration(self, ctx):
        # Extract method text
        start = ctx.start.start  # Start of method
        stop = ctx.stop.stop  # End of method
        input_stream = ctx.start.getInputStream()
        method_text = input_stream.getText(start, stop)  # Get method text

        # Ensure text is properly formatted
        try:
            formatted_method_text = self.format_java_method(method_text)
        except JavaFormatterError as e:
            logging.info(f"Formatter Error: {e}")
            formatted_method_text = method_text  # Use unformatted version on error

        # Add method to list
        self.methods.append(formatted_method_text)


def extract_methods_from_java(source_code: str) -> list[str]:
    input_stream = InputStream(source_code)
    lexer = JavaLexer(input_stream)
    token_stream = CommonTokenStream(lexer)
    parser = JavaParser(token_stream)
    tree = parser.compilationUnit()

    extractor = MethodExtractor()
    walker = ParseTreeWalker()
    walker.walk(extractor, tree)

    return extractor.methods
