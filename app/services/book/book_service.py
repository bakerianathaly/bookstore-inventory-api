from app.repositories.book_repository import BookRepository
from app.services.book.calculate_price import CalculatePrice
from app.services.book.create_book import CreateBook
from app.services.book.delete_book import DeleteBook
from app.services.book.get_book import GetBook
from app.services.book.update_book import UpdateBook


class BookUseCase:
    def __init__(self, repository: BookRepository):
        self.create = CreateBook(repository)
        self.get = GetBook(repository)
        self.update = UpdateBook(repository)
        self.delete = DeleteBook(repository)
        self.calculate_price = CalculatePrice(repository)
