def main() -> None:
    print_it("in main()")


def print_it(message: str) -> None:
    print(message)


if __name__ == "__main__":
    print_it("in module")
    main()
