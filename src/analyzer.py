# This file is part of: glwssa-compiler 
# Copyright (C) 2025  @theolaos
# glwssa-compiler is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

from .error import ErrorStack

class TreeAnalyzer:
    def analyze_types_tree(self, ast, error_stack: ErrorStack) -> None:
        """
        Analyzes everything in the program tree. If there are any errors it pushes them to the error stack.

        Checks:

        Variable types = Checks Expressions and the type they should give
        checks conditions and if they are boolean
        checks the right functions/procedures have the right amount of arguments.

        :param ast: Should be the tree produced by the ParserAST
        """

        self.ast = ast
        self.error_stack = error_stack