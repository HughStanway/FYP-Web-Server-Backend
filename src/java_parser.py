from antlr4 import *

from antlr.Java20Lexer import Java20Lexer as JavaLexer
from antlr.Java20Parser import Java20Parser as JavaParser
from antlr.Java20ParserListener import Java20ParserListener as JavaParserListener


class MethodExtractor(JavaParserListener):
    def __init__(self):
        self.methods = []
        self.method_count = 0

    def enterMethodDeclaration(self, ctx):
        # Extract method text
        start = ctx.start.start  # Start of method
        stop = ctx.stop.stop  # End of method
        input_stream = ctx.start.getInputStream()
        method_text = input_stream.getText(start, stop)  # Get method text

        # Add method to list
        self.methods.append(method_text)
        self.method_count += 1


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


# Example usage
if __name__ == "__main__":
    with open("src/TicTacToe.java", 'r') as java_file:
        java_code = java_file.read()

    methods = extract_methods_from_java(java_code)
    for method in methods:
        print(method.encode().decode('unicode_escape'))
