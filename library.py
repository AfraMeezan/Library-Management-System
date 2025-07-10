class Book:
    def __init__(self, title, author, copies):
        self.title = title
        self.author = author
        self.available_copies = copies

    def __str__(self):
        return f"{self.title} by {self.author} (Available: {self.available_copies})"

class Member:
    def __init__(self, member_id, name):
        self.member_id = member_id
        self.name = name
        self.borrowed_books = []

    def borrow_book(self, book):
        if len(self.borrowed_books) < self.borrow_limit:
            if book.available_copies > 0:
                self.borrowed_books.append(book)
                book.available_copies -= 1
                print(f"{self.name} borrowed '{book.title}'")
            else:
                print("Book not available!")
        else:
            print(f"{self.name} has reached the borrow limit!")

    def return_book(self, book):
        if book in self.borrowed_books:
            self.borrowed_books.remove(book)
            book.available_copies += 1
            print(f"{self.name} returned '{book.title}'")
        else:
            print("This book was not borrowed by this member.")

    def display_borrowed_books(self):
        if not self.borrowed_books:
            print(f"{self.name} has no borrowed books.")
        else:
            print(f"{self.name}'s borrowed books:")
            for book in self.borrowed_books:
                print(f" - {book.title}")

class Student(Member):
    borrow_limit = 3

class Faculty(Member):
    borrow_limit = 5

class Library:
    def __init__(self):
        self.books = []
        self.members = {}

    def add_book(self):
        title = input("Enter book title: ")
        author = input("Enter author name: ")
        try:
            copies = int(input("Enter number of copies: "))
            self.books.append(Book(title, author, copies))
            print("Book added successfully.\n")
        except ValueError:
            print("Invalid number of copies.\n")

    def register_member(self):
        member_type = input("Enter member type (student/faculty): ").lower()
        member_id = input("Enter member ID: ")
        name = input("Enter member name: ")
        if member_id in self.members:
            print("Member ID already exists.\n")
            return
        if member_type == 'student':
            self.members[member_id] = Student(member_id, name)
        elif member_type == 'faculty':
            self.members[member_id] = Faculty(member_id, name)
        else:
            print("Invalid member type.\n")
            return
        print(f"{member_type.title()} '{name}' registered with ID {member_id}.\n")

    def search_books(self):
        keyword = input("Enter title or author keyword: ")
        print(f"\nSearch results for '{keyword}':")
        found = False
        for book in self.books:
            if keyword.lower() in book.title.lower() or keyword.lower() in book.author.lower():
                print(book)
                found = True
        if not found:
            print("No matching books found.\n")

    def borrow_book(self):
        member_id = input("Enter member ID: ")
        member = self.members.get(member_id)
        if not member:
            print("Member not found.\n")
            return
        title = input("Enter book title to borrow: ")
        for book in self.books:
            if book.title.lower() == title.lower():
                member.borrow_book(book)
                return
        print("Book not found.\n")

    def return_book(self):
        member_id = input("Enter member ID: ")
        member = self.members.get(member_id)
        if not member:
            print("Member not found.\n")
            return
        title = input("Enter book title to return: ")
        for book in self.books:
            if book.title.lower() == title.lower():
                member.return_book(book)
                return
        print("Book not found.\n")

    def show_member_info(self):
        member_id = input("Enter member ID: ")
        member = self.members.get(member_id)
        if member:
            print(f"\nMember ID: {member.member_id}")
            print(f"Name: {member.name}")
            member.display_borrowed_books()
        else:
            print("Member not found.\n")

def main():
    library = Library()
    while True:
        print("\n--- Smart Library Menu ---")
        print("1. Add Book")
        print("2. Register Member")
        print("3. Search Books")
        print("4. Borrow Book")
        print("5. Return Book")
        print("6. Show Member Info")
        print("7. Exit")
        choice = input("Enter your choice (1-7): ")

        if choice == '1':
            library.add_book()
        elif choice == '2':
            library.register_member()
        elif choice == '3':
            library.search_books()
        elif choice == '4':
            library.borrow_book()
        elif choice == '5':
            library.return_book()
        elif choice == '6':
            library.show_member_info()
        elif choice == '7':
            print("Thank you")
            break
        else:
            print("Invalid choice. Try again.\n")

if __name__ == "__main__":
    main()
