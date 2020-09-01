#!/usr/bin/python3
from string import ascii_letters
from random import randint, seed
from os import system, path, get_terminal_size
from sys import argv
from json import load, dump


class Hangman:
    from hangman_art import BANNER, STAGES

    def __init__(self):
        with open(
            path.dirname(path.abspath(__file__)) + "/hangman_wordlist.json", "r"
        ) as wordlist_file:
            self.WORDLIST = load(wordlist_file)

        # Ugly ANSI color encoding + whitespace to correct for offset caused in .center() function
        self.header_commands = "                           \x1b[35m###\x1b[0m \x1b[32mCOMMANDS\x1b[0m \x1b[35m###\x1b[0m\n"
        self.header_available_lists = "                            \x1b[35m###\x1b[0m \x1b[32mAVAILABLE WORDLISTS\x1b[0m \x1b[35m###\x1b[0m\n"
        self.header_add_list = "                            \x1b[35m###\x1b[0m \x1b[32mADD WORDLIST\x1b[0m \x1b[35m###\x1b[0m\n"

        self.text_add_format = "                                    \x1b[33mcategory\x1b[0m,\x1b[93mentry\x1b[0m,\x1b[93mentry\x1b[0m,\x1b[93mentry\x1b[0m"
        self.text_return = "          '\x1b[31mback\x1b[0m' to return to the game."
        self.text_commands = [
            "                           \x1b[35m###\x1b[0m \x1b[32mCOMMANDS\x1b[0m \x1b[35m###\x1b[0m\n",
            "       '\x1b[33mname-of-list\x1b[0m' to start a new game",
            "       '\x1b[31mrandom\x1b[0m' to start a game using a random list",
            "           '\x1b[31mshow\x1b[0m \x1b[33mname-of-list\x1b[0m' to show items in that list",
            "       '\x1b[31madd\x1b[0m' to add to / create a list",
            "       '\x1b[31mexit\x1b[0m' to quit the game",
        ]

    @staticmethod
    def get_random_word(wordlist):
        """ Returns a random word from a list of strings.   """
        seed()
        return list(wordlist[randint(0, len(wordlist) - 1)])

    @staticmethod
    def print_centered(string):
        """ Takes a string or list of strings and outputs them centered based on terminal window size. """
        if type(string) == list:
            for line in string:
                print(str(line).center(get_terminal_size()[0]))
        else:
            print(str(string).center(get_terminal_size()[0]))
        return ""

    @staticmethod
    def get_wordlist(dict_key, dict_source):
        """ Returns a tuple containing 2 variables. First the string name of the list, second the list object itself. """
        if dict_key == "random":
            random_list = list(dict_source.keys())[randint(0, len(dict_source) - 1)]
            return random_list, dict_source[random_list]
        else:
            return dict_key, dict_source[dict_key]

    @staticmethod
    def contains_empty_string(strings_list):
        """ Returns True if the provided list contains an empty string. """
        for string in strings_list:
            if str(string) == "":
                return True
        return False

    @staticmethod
    def append_wordlist(new_dict, json_file="/hangman_wordlist.json"):
        """ Overwrites the .json file with the provided dictionary. Please use a (modified) copy of the original dictionary. """
        with open(
            path.dirname(path.abspath(__file__)) + json_file, "w"
        ) as wordlist_file:
            dump(new_dict, wordlist_file)

    @classmethod
    def get_stage(cls, number, art_list=STAGES):
        """ Returns the ASCII stages art. Changes depending on the 'number' argument (attempts/lives remaining). """
        if number > 7:
            return art_list[7]
        elif number < 0:
            return art_list[0]
        return art_list[number]

    @classmethod
    def get_banner(cls, banner=BANNER):
        """ Returns the ASCII banner art for Hangman. """
        return banner

    def show_wordlist(self, wordlist_name):
        """ Prints all items in the wordlist using print_centered(). """
        self.header_show_list = f"                                   \x1b[35m###\x1b[0m \x1b[32mITEMS IN\x1b[0m \x1b[33m{wordlist_name.upper()}\x1b[0m \x1b[35m###\x1b[0m"

        Hangman.print_centered(["", self.header_show_list, ""])

        for item in self.WORDLIST[wordlist_name]:
            Hangman.print_centered(item)

        input(Hangman.print_centered(["\n", "press any button to clear screen"]))

    def add_wordlist(self, save_permanently=False):
        """ Prompts for a string input with the format; 'category,entry,entry,entry'. Updates the hangman_wordlist.json file if 'save_permanently' argument is True. """
        Hangman.print_centered(
            [
                "",
                self.header_add_list,
                "the program is ready to receive your input",
                "use the following format to add to/create a wordlist:",
                self.text_add_format,
                "\n",
                "(input must contain a category and at least 1 entry)",
                "\n",
                "if you create a new category it will show up in the list above",
                "to see entries you have added, use the 'show' command",
            ]
        )

        additions_list = [entry for entry in input().split(",")]

        # Check whether the user has input a valid list.
        if len(additions_list) < 2 or Hangman.contains_empty_string(additions_list):
            return False

        else:
            try:
                updated = False

                # Append an already existing wordlist.
                if additions_list[0] in self.WORDLIST:
                    for entry in additions_list[1:]:

                        # Only insert if the word isn't already in the wordlist
                        # and flag that the wordlist has been updated.
                        if entry not in self.WORDLIST[additions_list[0]]:
                            updated = True
                            self.WORDLIST[additions_list[0]].append(entry)

                # Create a key/value dictionary pair for the new wordlist.
                else:
                    updated = True
                    self.WORDLIST[additions_list[0]] = additions_list[1:]

                # Update the hangman_wordlist.json file
                if updated and save_permanently:
                    Hangman.append_wordlist(new_dict=self.WORDLIST)

            except:
                return False
        return True

    def handle_gamestate(self):
        """ Print the current game state to the terminal. Depends on play() to function. """
        if not hasattr(self, "show_options"):
            print(
                "ERROR: handle_gamestate() called before play() has been instantiated."
            )
            exit()

        # Clear terminal for updated information
        system("clear")

        # Show ASCII banner art
        print("\n\n")
        Hangman.print_centered(Hangman.get_banner())
        print("\n")

        # Show the options menu
        if self.show_options:

            # Show available options
            Hangman.print_centered(self.text_commands)

            if hasattr(self, "wordlist") and not self.game_ended:
                Hangman.print_centered(["", self.text_return])

            # Show available lists
            Hangman.print_centered(["\n", self.header_available_lists])
            for key in self.WORDLIST:
                Hangman.print_centered(key)

            # Prompt input
            command = input().lower()

            # Go back to the game scene if there is an active game state
            if command == "back" and hasattr(self, "wordlist"):
                if not self.game_ended:
                    self.show_options = False
                self.handle_gamestate()

            # Attempt to add to / create a wordlist
            elif command == "add":
                self.add_wordlist(save_permanently=True)
                self.handle_gamestate()

            # Show items in desired wordlist
            elif command.startswith("show "):
                if command[5:] in self.WORDLIST:
                    self.show_wordlist(command[5:])
                self.handle_gamestate()

            # Quit the game and clear the terminal
            elif command == "exit":
                system("clear")
                exit()

            # Initiate a new game with random wordlist
            elif command == "random":
                hangman.play(wordlist="random")
                system("clear")
                exit()

            # Initiate a new game with the desired wordlist
            elif command in self.WORDLIST:
                hangman.play(wordlist=command)
                system("clear")
                exit()

            # Return to the top of the function if there were no valid inputs.
            else:
                self.handle_gamestate()

        # Show the game state scene
        else:
            # Show ASCII art of the Hangman game stages
            Hangman.print_centered(Hangman.get_stage(self.num_attempts))
            print("\n")

            # Player wins
            if self.hangman_word == self.secret_word:
                Hangman.print_centered(self.text_win)
                print("\n")
                Hangman.print_centered(self.text_replay)

            # Player loses
            elif self.num_attempts == 0 and self.hangman_word != self.secret_word:
                Hangman.print_centered(self.text_loss)
                print("\n")
                Hangman.print_centered(self.text_replay)

            # Show the Hangman word & attempts left
            else:
                Hangman.print_centered(
                    [
                        " ".join(self.hangman_word),
                        "",
                        f"You have {self.num_attempts} attempts left",
                    ]
                )

    def play(self, num_attempts=7, wordlist=""):
        """ Start the Hangman game. Required for the handle_gamestage() function to work. """

        # Go to options menu?
        if wordlist == "":
            self.show_options = True
            self.handle_gamestate()
        else:
            self.show_options = False

        # Instantiate game variables
        self.game_ended = False
        self.num_attempts = num_attempts
        self.wordlist = Hangman.get_wordlist(wordlist, self.WORDLIST)
        self.secret_word = Hangman.get_random_word(self.wordlist[1])
        self.hangman_word = [
            "_" if letter != " " else " " for letter in self.secret_word
        ]
        self.text_answer = (
            f"       The answer was '\x1b[93m{''.join(self.secret_word)}\x1b[0m'"
        )
        self.text_win = [
            f"YOU SURVIVED! \U0001F600",
            self.text_answer,
        ]
        self.text_loss = [
            f"YOU DIED! \U0001F61E",
            self.text_answer,
        ]
        self.text_replay = [
            "       press '\x1b[32menter\x1b[0m' to play again",
            "       enter '\x1b[31mexit\x1b[0m' to quit the game",
            "       enter '\x1b[31m#\x1b[0m' to go to the options menu",
        ]
        self.text_greeting = [
            "\n",
            "           Enter '\x1b[31m#\x1b[0m' at any time to go to the options menu",
            f"(current wordlist: {self.wordlist[0]})",
        ]

        # Greet the player and show the gameboard
        self.handle_gamestate()
        Hangman.print_centered(self.text_greeting)

        # Game logic loop
        while self.num_attempts > 0 and self.hangman_word != self.secret_word:

            guess = input()

            if guess == "exit":
                system("clear")
                exit()

            elif guess == "#":
                self.show_options = True
                self.handle_gamestate()

            if len(guess) != 1 or guess not in ascii_letters:
                self.handle_gamestate()
                continue

            for index in range(len(self.secret_word)):
                if guess.lower() == self.secret_word[index]:
                    self.hangman_word[index] = guess.lower()

            if guess.lower() not in self.secret_word:
                self.num_attempts -= 1

            self.handle_gamestate()

        # Game end options
        self.game_ended = True

        command = input()
        if command.lower() == "exit":
            system("clear")
            exit()

        elif command == "#":
            self.show_options = True
            self.handle_gamestate()

        else:
            hangman.play(wordlist=self.wordlist[0])


# Hangman game init
hangman = Hangman()
hangman.play(wordlist=argv[1] if len(argv) > 1 else "")
system("clear")
exit()
