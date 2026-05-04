# allows you to generate encrypted data

import argparse

import secrets

try:
    from .keyhandler import FERNET, mask_all
    from .vercelauth import vercel_auth
except ImportError as excp:
    from keyhandler import FERNET, mask_all
    from vercelauth import vercel_auth


def gen_keystr():
    return secrets.token_urlsafe(32)


class Args(argparse.Namespace):
    command: str
    content: str


def main():
    parser = argparse.ArgumentParser()

    # using if statements here for indentation to help organise subcommands/arguments
    if command := parser.add_subparsers(dest="command"):
        if encrypt := command.add_parser("e", help="Encrypt content"):
            encrypt.add_argument("content", nargs="?")
        if decrypt := command.add_parser("d", help="Decrypt content"):
            decrypt.add_argument("content", nargs="?")

        command.add_parser("keygen", help="Generate a key. You could set this to $FERNET_KEY if you want")
        command.add_parser("vercel", help="Output the vercel auth data.")
        command.add_parser("addmask", help="Mask all secrets.")

    cmd(parser.parse_args(namespace=Args()))


def cmd(args: Args):
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
            print("\n".join(vercel_auth()))

        case "addmask":
            mask_all()


if __name__ == "__main__":
    main()
