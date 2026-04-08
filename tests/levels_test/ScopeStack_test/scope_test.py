import pytest
from glwssa_compiler import ScopeStack, Scope, ErrorStack
from glwssa_compiler.log import log

class Error():
    def __init__(self):
        self.stack = []

    def push(self, info):
        self.stack.append(info)
        print(self.stack)


class DummyToken:
    def __init__(self, kind):
        self.kind = kind


def test_scope_stack_initialization():
    err = Error()
    stack = ScopeStack(err)

    assert stack.error is err
    assert stack.stack == []


def test_push_scope():
    err = Error()
    stack = ScopeStack(err)

    scope = Scope("IF", DummyToken("IF"))
    stack.append(scope)

    assert stack.stack[-1] == scope
    assert len(stack.stack) == 1


def test_multiple_push():
    err = Error()
    stack = ScopeStack(err)

    s1 = Scope("IF", DummyToken("IF"))
    s2 = Scope("WHILE", DummyToken("WHILE"))

    stack.append(s1)
    stack.append(s2)

    assert stack.stack[-1] == s2
    assert stack.stack[0] == s1
    assert len(stack.stack) == 2 


def test_expect_pop_correct_scope():
    err = Error()
    stack = ScopeStack(err)

    scope = Scope("WHILE", DummyToken("WHILE"))
    stack.append(scope)

    result = stack.expect_pop(scope)

    assert result is True
    assert stack.stack == []
    assert err.stack == []


def test_expect_pop_wrong_scope():
    err = Error()
    stack = ScopeStack(err)

    stack.append(Scope("IF", DummyToken("IF")))
    print("Before Stack Change (IF):", stack.stack)

    wrong_scope = Scope("WHILE", DummyToken("END_LOOP"))

    result = stack.expect_pop(wrong_scope)

    print("After Stack Pop (WHILE):", stack.stack)
    print("Error Stack:", err.stack)

    assert result is False
    assert len(err.stack) == 1


def test_pop_in_nested_scopes():
    err = Error()
    stack = ScopeStack(err)

    # Push nested scopes
    stack.append(Scope("IF", DummyToken("IF")))
    stack.append(Scope("LOOP", DummyToken("WHILE")))
    stack.append(Scope("LOOP", DummyToken("FOR")))
    stack.append(Scope("START_LOOP", DummyToken("STAR_LOOP")))

    print("Before Pops:", stack.stack)

    # Close FOR
    result1 = stack.expect_pop(Scope("START_LOOP", DummyToken("UNTIL")))
    print("After START_LOOP Pop:", stack.stack)

    # Close FOR
    result1 = stack.expect_pop(Scope("LOOP", DummyToken("END_LOOP")))
    print("After FOR Pop:", stack.stack)

    # Close WHILE
    result2 = stack.expect_pop(Scope("LOOP", DummyToken("END_LOOP")))
    print("After WHILE Pop:", stack.stack)

    # Close IF
    result3 = stack.expect_pop(Scope("IF", DummyToken("END_IF")))
    print("After IF Pop:", stack.stack)

    print("Error Stack:", err.stack)
    stack.expect_empty(DummyToken("EMPTY"))

    assert result1 is True
    assert result2 is True
    assert result3 is True

    assert stack.stack == []
    assert len(err.stack) == 0


def test_error_pop_in_nested_scopes():
    err = Error()
    stack = ScopeStack(err)

    # Push nested scopes
    stack.append(Scope("PROGRAM", DummyToken("PROGRAM")))
    stack.append(Scope("IF", DummyToken("IF")))
    stack.append(Scope("LOOP", DummyToken("WHILE")))
    stack.append(Scope("LOOP", DummyToken("FOR")))

    print("Before Pops:", stack.stack)

    stack.expect_empty(DummyToken("EMPTY"))

    print("Error Stack:", err.stack)

    assert len(err.stack) == 4
    # assert 


def test_nested_not_closing_properly():
    log(f"Testing test_nested_not_closing now.", tags=["pytest"])
    err = Error()
    stack = ScopeStack(err)

    stack.append(Scope("PROGRAM", DummyToken("PROGRAM")))
    stack.append(Scope("IF", DummyToken("IF")))
    stack.append(Scope("LOOP", DummyToken("WHILE")))

    # Attempt to close IF before WHILE
    result = stack.expect_pop(Scope("IF", DummyToken("END_IF")))

    assert result is False
    assert len(stack.stack) == 2 # We did only one expect_pop
    assert len(err.stack) == 1
    log(f"Finished testing test_nested_not_closing.", tags=["pytest"])


def test_early_program_close():
    log(f"Testing test_early_program_close now.", tags=["pytest"])
    err = Error()
    stack = ScopeStack(err)

    stack.append(Scope("PROGRAM", DummyToken("PROGRAM")))
    stack.append(Scope("IF", DummyToken("IF")))
    stack.append(Scope("LOOP", DummyToken("WHILE")))

    # Simulating that it found the token END_PROGRAM
    result = stack.expect_pop(Scope("PROGRAM", DummyToken("END_PROGRAM"))) 

    assert result is False
    assert len(stack.stack) == 0
    assert len(err.stack) == 2
    log(f"Finished testing test_early_program_close.", tags=["pytest"])


def test_program_wrong_nested_close():
    log(f"Testing test_program_wrong_nested_close now.", tags=["pytest"])
    # Simulating the below code scopes
    # ΠΡΟΓΡΑΜΜΑ ΘΕΜΑ_Δ
    # ΑΡΧΗ
    #     ΟΣΟ ν ΕΠΑΝΑΛΑΒΕ
    #         ΑΝ Α ΤΟΤΕ
    #             ΓΙΑ Α ΑΠΟ Α ΜΕΧΡΙ Π
    #             ΤΕΛΟΣ_ΕΠΑΝΑΛΗΨΗΣ
    #         ΤΕΛΟΣ_ΕΠΑΝΑΛΗΨΗΣ

    err = Error()
    stack = ScopeStack(err)

    stack.append(Scope("PROGRAM", DummyToken("PROGRAM")))
    stack.append(Scope("LOOP", DummyToken("WHILE")))
    stack.append(Scope("IF", DummyToken("IF")))
    stack.append(Scope("LOOP", DummyToken("FOR")))

    result1 = stack.expect_pop(Scope("LOOP", DummyToken("END_LOOP")))
    result2 = stack.expect_pop(Scope("LOOP", DummyToken("END_LOOP")))

    stack.expect_empty(DummyToken("EMPTY"))

    assert result1 is True
    assert result2 is False
    assert len(stack.stack) == 0
    print("The error stack:", err.stack)
    assert len(err.stack) == 3
    log(f"Finished testing test_program_wrong_nested_close.")

# def test_expect_pop_empty_stack():
#     err = Error()
#     stack = ScopeStack(err)

#     scope = Scope("IF", DummyToken("IF"))

#     with pytest.raises(IndexError):
#         stack.expect_pop(scope)


