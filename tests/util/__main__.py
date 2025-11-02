# allows you to generate encrypted data

import argparse

import secrets

try:
    from .keyhandler import FERNET
    from .vercelauth import vercel_auth
except ImportError as excp:
    from keyhandler import FERNET
    from vercelauth import vercel_auth


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
        if vercelauth := command.add_parser("vercel", help="Output the vercel auth data."):
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
            
        case "vercel":
            print(
                "\n".join(vercel_auth())
            )


if __name__ == "__main__":
    main()
