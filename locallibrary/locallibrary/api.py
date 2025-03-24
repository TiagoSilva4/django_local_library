from ninja import NinjaAPI, Schema, ModelSchema
from ninja.pagination import paginate
from ninja.security import django_auth
from typing import List, Optional, Any
from datetime import date
import uuid
from catalog.models import Author, Genre, Language, Book, BookInstance
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

User = get_user_model()

# Initialize the API with Django's authentication
api = NinjaAPI(auth=django_auth)

# Schemas for Author
class AuthorSchema(Schema):
    id: int
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    date_of_death: Optional[date] = None

class AuthorCreateSchema(Schema):
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    date_of_death: Optional[date] = None

class AuthorUpdateSchema(Schema):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[date] = None
    date_of_death: Optional[date] = None

# Schemas for Genre
class GenreSchema(Schema):
    id: int
    name: str

class GenreCreateSchema(Schema):
    name: str

class GenreUpdateSchema(Schema):
    name: Optional[str] = None

# Schemas for Language
class LanguageSchema(Schema):
    id: int
    name: str

class LanguageCreateSchema(Schema):
    name: str

class LanguageUpdateSchema(Schema):
    name: Optional[str] = None

# Book Schemas
class BookGenreSchema(Schema):
    id: int

class BookAuthorSchema(Schema):
    id: int

class BookLanguageSchema(Schema):
    id: int

class BookSchema(Schema):
    id: int
    title: str
    summary: str
    isbn: str
    author: Optional[AuthorSchema] = None
    language: Optional[LanguageSchema] = None
    genre: List[GenreSchema] = []

class BookCreateSchema(Schema):
    title: str
    summary: str
    isbn: str
    author_id: Optional[int] = None
    language_id: Optional[int] = None
    genre_ids: List[int] = []

class BookUpdateSchema(Schema):
    title: Optional[str] = None
    summary: Optional[str] = None
    isbn: Optional[str] = None
    author_id: Optional[int] = None
    language_id: Optional[int] = None
    genre_ids: Optional[List[int]] = None

# BookInstance Schemas
class UUIDSchema(Schema):
    uuid_string: str

    @staticmethod
    def resolve_uuid_string(uuid_obj):
        return str(uuid_obj)

class BookInstanceSchema(Schema):
    id: UUIDSchema
    book: BookSchema
    imprint: str
    due_back: Optional[date] = None
    borrower: Optional[int] = None  # User ID
    status: str

class BookInstanceCreateSchema(Schema):
    book_id: int
    imprint: str
    due_back: Optional[date] = None
    borrower_id: Optional[int] = None
    status: str = 'a'  # Default to 'available'

class BookInstanceUpdateSchema(Schema):
    book_id: Optional[int] = None
    imprint: Optional[str] = None
    due_back: Optional[date] = None
    borrower_id: Optional[int] = None
    status: Optional[str] = None

# Error responses
class ErrorSchema(Schema):
    message: str

# Authentication endpoint for API
class LoginInput(Schema):
    username: str
    password: str

class TokenOutput(Schema):
    access_token: str

# Author API Routes
@api.get("/authors", response=List[AuthorSchema], tags=["authors"])
@paginate
def list_authors(request):
    return Author.objects.all()

@api.get("/authors/{author_id}", response={200: AuthorSchema, 404: ErrorSchema}, tags=["authors"])
def get_author(request, author_id: int):
    try:
        return 200, Author.objects.get(id=author_id)
    except Author.DoesNotExist:
        return 404, {"message": "Author not found"}

@api.post("/authors", response={201: AuthorSchema, 400: ErrorSchema, 401: ErrorSchema}, tags=["authors"], auth=django_auth)
def create_author(request, payload: AuthorCreateSchema):
    try:
        author = Author.objects.create(
            first_name=payload.first_name,
            last_name=payload.last_name,
            date_of_birth=payload.date_of_birth,
            date_of_death=payload.date_of_death
        )
        return 201, author
    except Exception as e:
        return 400, {"message": str(e)}

@api.put("/authors/{author_id}", response={200: AuthorSchema, 404: ErrorSchema, 400: ErrorSchema, 401: ErrorSchema}, tags=["authors"], auth=django_auth)
def update_author(request, author_id: int, payload: AuthorUpdateSchema):
    try:
        author = Author.objects.get(id=author_id)
        
        if payload.first_name is not None:
            author.first_name = payload.first_name
        if payload.last_name is not None:
            author.last_name = payload.last_name
        if payload.date_of_birth is not None:
            author.date_of_birth = payload.date_of_birth
        if payload.date_of_death is not None:
            author.date_of_death = payload.date_of_death
            
        author.save()
        return 200, author
    except Author.DoesNotExist:
        return 404, {"message": "Author not found"}
    except Exception as e:
        return 400, {"message": str(e)}

@api.delete("/authors/{author_id}", response={204: None, 404: ErrorSchema, 401: ErrorSchema}, tags=["authors"], auth=django_auth)
def delete_author(request, author_id: int):
    try:
        author = Author.objects.get(id=author_id)
        author.delete()
        return 204, None
    except Author.DoesNotExist:
        return 404, {"message": "Author not found"}

# Genre API Routes
@api.get("/genres", response=List[GenreSchema], tags=["genres"])
@paginate
def list_genres(request):
    return Genre.objects.all()

@api.get("/genres/{genre_id}", response={200: GenreSchema, 404: ErrorSchema}, tags=["genres"])
def get_genre(request, genre_id: int):
    try:
        return 200, Genre.objects.get(id=genre_id)
    except Genre.DoesNotExist:
        return 404, {"message": "Genre not found"}

@api.post("/genres", response={201: GenreSchema, 400: ErrorSchema, 401: ErrorSchema}, tags=["genres"], auth=django_auth)
def create_genre(request, payload: GenreCreateSchema):
    try:
        genre = Genre.objects.create(name=payload.name)
        return 201, genre
    except Exception as e:
        return 400, {"message": str(e)}

@api.put("/genres/{genre_id}", response={200: GenreSchema, 404: ErrorSchema, 400: ErrorSchema, 401: ErrorSchema}, tags=["genres"], auth=django_auth)
def update_genre(request, genre_id: int, payload: GenreUpdateSchema):
    try:
        genre = Genre.objects.get(id=genre_id)
        
        if payload.name is not None:
            genre.name = payload.name
            
        genre.save()
        return 200, genre
    except Genre.DoesNotExist:
        return 404, {"message": "Genre not found"}
    except Exception as e:
        return 400, {"message": str(e)}

@api.delete("/genres/{genre_id}", response={204: None, 404: ErrorSchema, 401: ErrorSchema}, tags=["genres"], auth=django_auth)
def delete_genre(request, genre_id: int):
    try:
        genre = Genre.objects.get(id=genre_id)
        genre.delete()
        return 204, None
    except Genre.DoesNotExist:
        return 404, {"message": "Genre not found"}

# Language API Routes
@api.get("/languages", response=List[LanguageSchema], tags=["languages"])
@paginate
def list_languages(request):
    return Language.objects.all()

@api.get("/languages/{language_id}", response={200: LanguageSchema, 404: ErrorSchema}, tags=["languages"])
def get_language(request, language_id: int):
    try:
        return 200, Language.objects.get(id=language_id)
    except Language.DoesNotExist:
        return 404, {"message": "Language not found"}

@api.post("/languages", response={201: LanguageSchema, 400: ErrorSchema, 401: ErrorSchema}, tags=["languages"], auth=django_auth)
def create_language(request, payload: LanguageCreateSchema):
    try:
        language = Language.objects.create(name=payload.name)
        return 201, language
    except Exception as e:
        return 400, {"message": str(e)}

@api.put("/languages/{language_id}", response={200: LanguageSchema, 404: ErrorSchema, 400: ErrorSchema, 401: ErrorSchema}, tags=["languages"], auth=django_auth)
def update_language(request, language_id: int, payload: LanguageUpdateSchema):
    try:
        language = Language.objects.get(id=language_id)
        
        if payload.name is not None:
            language.name = payload.name
            
        language.save()
        return 200, language
    except Language.DoesNotExist:
        return 404, {"message": "Language not found"}
    except Exception as e:
        return 400, {"message": str(e)}

@api.delete("/languages/{language_id}", response={204: None, 404: ErrorSchema, 401: ErrorSchema}, tags=["languages"], auth=django_auth)
def delete_language(request, language_id: int):
    try:
        language = Language.objects.get(id=language_id)
        language.delete()
        return 204, None
    except Language.DoesNotExist:
        return 404, {"message": "Language not found"}

# Book API Routes
@api.get("/books", response=List[BookSchema], tags=["books"])
@paginate
def list_books(request):
    return Book.objects.all()

@api.get("/books/{book_id}", response={200: BookSchema, 404: ErrorSchema}, tags=["books"])
def get_book(request, book_id: int):
    try:
        return 200, Book.objects.get(id=book_id)
    except Book.DoesNotExist:
        return 404, {"message": "Book not found"}

@api.post("/books", response={201: BookSchema, 400: ErrorSchema, 401: ErrorSchema}, tags=["books"], auth=django_auth)
def create_book(request, payload: BookCreateSchema):
    try:
        # Create the book without many-to-many relationships first
        book = Book(
            title=payload.title,
            summary=payload.summary,
            isbn=payload.isbn,
        )
        
        # Set foreign key relationships
        if payload.author_id:
            try:
                book.author = Author.objects.get(id=payload.author_id)
            except Author.DoesNotExist:
                return 400, {"message": f"Author with ID {payload.author_id} not found"}
                
        if payload.language_id:
            try:
                book.language = Language.objects.get(id=payload.language_id)
            except Language.DoesNotExist:
                return 400, {"message": f"Language with ID {payload.language_id} not found"}
        
        book.save()
        
        # Set many-to-many relationships after saving
        if payload.genre_ids:
            for genre_id in payload.genre_ids:
                try:
                    genre = Genre.objects.get(id=genre_id)
                    book.genre.add(genre)
                except Genre.DoesNotExist:
                    return 400, {"message": f"Genre with ID {genre_id} not found"}
        
        return 201, book
    except Exception as e:
        return 400, {"message": str(e)}

@api.put("/books/{book_id}", response={200: BookSchema, 404: ErrorSchema, 400: ErrorSchema, 401: ErrorSchema}, tags=["books"], auth=django_auth)
def update_book(request, book_id: int, payload: BookUpdateSchema):
    try:
        book = Book.objects.get(id=book_id)
        
        # Update scalar fields
        if payload.title is not None:
            book.title = payload.title
        if payload.summary is not None:
            book.summary = payload.summary
        if payload.isbn is not None:
            book.isbn = payload.isbn
            
        # Update foreign key relationships
        if payload.author_id is not None:
            try:
                book.author = Author.objects.get(id=payload.author_id)
            except Author.DoesNotExist:
                return 400, {"message": f"Author with ID {payload.author_id} not found"}
                
        if payload.language_id is not None:
            try:
                book.language = Language.objects.get(id=payload.language_id)
            except Language.DoesNotExist:
                return 400, {"message": f"Language with ID {payload.language_id} not found"}
        
        # Save before handling many-to-many relationships
        book.save()
        
        # Update many-to-many relationships
        if payload.genre_ids is not None:
            # Clear existing genres and add new ones
            book.genre.clear()
            for genre_id in payload.genre_ids:
                try:
                    genre = Genre.objects.get(id=genre_id)
                    book.genre.add(genre)
                except Genre.DoesNotExist:
                    return 400, {"message": f"Genre with ID {genre_id} not found"}
        
        return 200, book
    except Book.DoesNotExist:
        return 404, {"message": "Book not found"}
    except Exception as e:
        return 400, {"message": str(e)}

@api.delete("/books/{book_id}", response={204: None, 404: ErrorSchema, 401: ErrorSchema}, tags=["books"], auth=django_auth)
def delete_book(request, book_id: int):
    try:
        book = Book.objects.get(id=book_id)
        book.delete()
        return 204, None
    except Book.DoesNotExist:
        return 404, {"message": "Book not found"}

# BookInstance API Routes
@api.get("/bookinstances", response=List[BookInstanceSchema], tags=["bookinstances"])
@paginate
def list_bookinstances(request):
    return BookInstance.objects.all()

@api.get("/bookinstances/{instance_id}", response={200: BookInstanceSchema, 404: ErrorSchema}, tags=["bookinstances"])
def get_bookinstance(request, instance_id: str):
    try:
        instance_uuid = uuid.UUID(instance_id)
        return 200, BookInstance.objects.get(id=instance_uuid)
    except (ValueError, TypeError):
        return 404, {"message": "Invalid UUID format"}
    except BookInstance.DoesNotExist:
        return 404, {"message": "Book instance not found"}

@api.post("/bookinstances", response={201: BookInstanceSchema, 400: ErrorSchema, 401: ErrorSchema}, tags=["bookinstances"], auth=django_auth)
def create_bookinstance(request, payload: BookInstanceCreateSchema):
    try:
        # Check if book exists
        try:
            book = Book.objects.get(id=payload.book_id)
        except Book.DoesNotExist:
            return 400, {"message": f"Book with ID {payload.book_id} not found"}
        
        # Create book instance
        bookinstance = BookInstance(
            book=book,
            imprint=payload.imprint,
            due_back=payload.due_back,
            status=payload.status
        )
        
        # Set borrower if provided
        if payload.borrower_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                borrower = User.objects.get(id=payload.borrower_id)
                bookinstance.borrower = borrower
            except User.DoesNotExist:
                return 400, {"message": f"User with ID {payload.borrower_id} not found"}
        
        bookinstance.save()
        return 201, bookinstance
    except Exception as e:
        return 400, {"message": str(e)}

@api.put("/bookinstances/{instance_id}", response={200: BookInstanceSchema, 404: ErrorSchema, 400: ErrorSchema, 401: ErrorSchema}, tags=["bookinstances"], auth=django_auth)
def update_bookinstance(request, instance_id: str, payload: BookInstanceUpdateSchema):
    try:
        # Validate UUID format
        try:
            instance_uuid = uuid.UUID(instance_id)
        except (ValueError, TypeError):
            return 404, {"message": "Invalid UUID format"}
        
        # Get book instance
        try:
            bookinstance = BookInstance.objects.get(id=instance_uuid)
        except BookInstance.DoesNotExist:
            return 404, {"message": "Book instance not found"}
        
        # Update book reference if provided
        if payload.book_id is not None:
            try:
                book = Book.objects.get(id=payload.book_id)
                bookinstance.book = book
            except Book.DoesNotExist:
                return 400, {"message": f"Book with ID {payload.book_id} not found"}
        
        # Update scalar fields
        if payload.imprint is not None:
            bookinstance.imprint = payload.imprint
        if payload.due_back is not None:
            bookinstance.due_back = payload.due_back
        if payload.status is not None:
            bookinstance.status = payload.status
        
        # Update borrower if provided
        if payload.borrower_id is not None:
            if payload.borrower_id == 0:  # Special case to remove borrower
                bookinstance.borrower = None
            else:
                from django.contrib.auth import get_user_model
                User = get_user_model()
                try:
                    borrower = User.objects.get(id=payload.borrower_id)
                    bookinstance.borrower = borrower
                except User.DoesNotExist:
                    return 400, {"message": f"User with ID {payload.borrower_id} not found"}
        
        bookinstance.save()
        return 200, bookinstance
    except Exception as e:
        return 400, {"message": str(e)}

@api.delete("/bookinstances/{instance_id}", response={204: None, 404: ErrorSchema, 401: ErrorSchema}, tags=["bookinstances"], auth=django_auth)
def delete_bookinstance(request, instance_id: str):
    try:
        # Validate UUID format
        try:
            instance_uuid = uuid.UUID(instance_id)
        except (ValueError, TypeError):
            return 404, {"message": "Invalid UUID format"}
        
        # Delete book instance
        try:
            bookinstance = BookInstance.objects.get(id=instance_uuid)
            bookinstance.delete()
            return 204, None
        except BookInstance.DoesNotExist:
            return 404, {"message": "Book instance not found"}
    except Exception as e:
        return 404, {"message": str(e)}

# Special endpoint for marking a book as returned (requires special permission)
@api.post("/bookinstances/{instance_id}/return", response={200: BookInstanceSchema, 404: ErrorSchema, 400: ErrorSchema, 401: ErrorSchema, 403: ErrorSchema}, tags=["bookinstances"], auth=django_auth)
def mark_returned(request, instance_id: str):
    # Check if the user has the can_mark_returned permission
    if not request.user.has_perm('catalog.can_mark_returned'):
        return 403, {"message": "You don't have permission to mark books as returned"}
    
    try:
        # Validate UUID format
        try:
            instance_uuid = uuid.UUID(instance_id)
        except (ValueError, TypeError):
            return 404, {"message": "Invalid UUID format"}
        
        # Get book instance
        try:
            bookinstance = BookInstance.objects.get(id=instance_uuid)
        except BookInstance.DoesNotExist:
            return 404, {"message": "Book instance not found"}
        
        # Mark as available and clear the borrower
        bookinstance.status = 'a'  # 'a' is for 'available'
        bookinstance.due_back = None
        bookinstance.borrower = None
        bookinstance.save()
        
        return 200, bookinstance
    except Exception as e:
        return 400, {"message": str(e)}

@api.post("/auth/token", response={200: TokenOutput, 401: ErrorSchema}, tags=["auth"], auth=None)
def get_token(request, data: LoginInput):
    from django.contrib.auth import authenticate
    from django.middleware.csrf import get_token
    from ninja.security import create_token
    
    user = authenticate(username=data.username, password=data.password)
    if user is None:
        return 401, {"message": "Invalid username or password"}
    
    token = create_token(user)
    return 200, {"access_token": token}