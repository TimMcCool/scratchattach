# allows you to generate encrypted data

import argparse

import secrets

try:
    from .keyhandler import FERNET
except ImportError:
    from keyhandler import FERNET


def gen_keystr():
    return secrets.token_urlsafe(32)


def main():
    class Args(argparse.Namespace):
        command: str
        content: str

    parser = argparse.ArgumentParser()

    if command := parser.add_subparsers(dest="command"):
        if encrypt := command.add_parser("e", help="Encrypt content"):
            encrypt.add_argument("content", nargs="?")
        if decrypt := command.add_parser("d", help="Decrypt content"):
            decrypt.add_argument("content", nargs="?")
        if keygen := command.add_parser("keygen", help="Generate a key. You could set this to $FERNET_KEY if you want"):
            ...

    args = parser.parse_args(namespace=Args())

    match args.command:
        case "e":
            if not args.content:
                args.content = input("content: ")
            print(FERNET.encrypt(args.content.encode()).decode())

        case "d":
            if not args.content:
                args.content = input("content: ")
            print(FERNET.decrypt(args.content.encode()).decode())

        case "keygen":
            print(gen_keystr())


if __name__ == "__main__":
    main()
