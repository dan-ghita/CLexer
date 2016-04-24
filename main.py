class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def append_character(self, c):
        self.value += c

    def set_type(self, type):
        self.type = type

    def __str__(self):
        return self.type + ': ' + self.value


class Parser:
    def __init__(self, dfa, source_file, final_states, key_words):
        self.dfa = dfa
        self.source_file = source_file
        self.final_states = final_states
        self.key_words = key_words
        self.index = 0
        self.error = ''
        self.line_number = 1
        self.initial_state = 'init'

    @property
    def current_symbol(self):
        return self.source_file[self.index]

    @property
    def valid_index(self):
        return self.index < len(self.source_file)

    @property
    def has_error(self):
        return self.error != ''

    @property
    def has_next(self):
        while self.valid_index and self.is_whitespace(self.current_symbol):
            if self.current_symbol == '\n':
                self.line_number += 1
            self.index += 1

        return self.valid_index

    @staticmethod
    def is_whitespace(symbol):
        return symbol in [' ', '\t', '\n']

    def is_final_state(self, state):
        return state in self.final_states

    def get_token(self):
        token = ''
        current_state = self.initial_state
        line_count = self.line_number

        final_state = None
        final_state_index = None
        final_token = None
        final_line_count = None

        while self.valid_index:
            if self.is_final_state(current_state):
                final_state = current_state
                final_state_index = self.index
                final_token = token
                final_line_count = line_count

            symbol = self.current_symbol
            if symbol == '\n':
                line_count += 1

            transition = (current_state, symbol)
            if transition not in self.dfa:
                break

            token += symbol
            current_state = self.dfa[transition]
            self.index += 1

        if not final_state:
            self.error = 'Error at line: ' + str(
                line_count) + ' Character: ' + symbol
        else:
            self.line_number = final_line_count
            self.index = final_state_index
            state = 'key_word' if final_token in self.key_words else final_state
            return Token(state, final_token)


def char_range(c1, c2):
    for c in range(ord(c1), ord(c2) + 1):
        yield chr(c)


anything_else = "\'\"_\\/.*-;,!@#+-()[]{}~`:?^&%$#"


# {(state1, symbol): state2}
def read_dfa():
    dfa = {}

    with open('dfa.in', 'r') as f:
        final_states = f.readline().rstrip('\n').split(' ')
        key_words = f.readline().rstrip('\n').split(' ')

        for transition in f:
            if transition[0] == '#':
                continue

            transition = transition.rstrip('\n')
            transition = transition.split(' ')

            state1 = transition[0]
            symbol = transition[1]
            state2 = transition[2]

            if symbol == 'any_char':
                for c in char_range('a', 'z'):
                    dfa[(state1, c)] = state2
                for c in char_range('A', 'Z'):
                    dfa[(state1, c)] = state2
            elif symbol == 'any_digit':
                for i in range(0, 10):
                    dfa[(state1, str(i))] = state2
            elif symbol == 'whitespace':
                dfa[(state1, ' ')] = state2
                dfa[(state1, '\t')] = state2
                dfa[(state1, '\n')] = state2
            elif symbol == 'whitespace_no_endl':
                dfa[(state1, ' ')] = state2
                dfa[(state1, '\t')] = state2
            elif symbol == 'anything_else':
                for c in anything_else:
                    dfa[(state1, c)] = state2
            elif symbol == 'endl':
                dfa[(state1, '\n')] = state2
            else:
                dfa[(state1, symbol)] = state2

        print(dfa)

    return dfa, final_states, key_words


def read_source_file():
    with open('main.cpp', 'r') as f:
        return f.read()


def main():
    dfa, final_states, key_words = read_dfa()
    source_file = read_source_file()
    # in case of no new line at EOF
    source_file += ' '

    parser = Parser(dfa, source_file, final_states, key_words)

    while parser.has_next:
        token = parser.get_token()
        if parser.has_error:
            print(parser.error)
            break
        else:
            print(token)

    print(parser.line_number)


main()
