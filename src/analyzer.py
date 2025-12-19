class TreeAnalyzer:
    def analyze_types_tree(self, ast) -> None:
        """
        Analyzes everything in the program tree. If there are any errors it pushes them to the error stack.
        
        :param ast: Should be the tree produced by the ParserAST
        """