import argparse

from scratchattach import cli

def main():
    parser = argparse.ArgumentParser(
        prog="scratch",
        description="Scratchattach CLI",
        epilog=f"Running scratchattach CLI version {cli.VERSION}",
    )

    args = parser.parse_args(namespace=cli.ArgSpace())

if __name__ == '__main__':
    main()
