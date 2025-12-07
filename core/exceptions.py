# Exceptions
class ApplicationError(Exception):
    """Base class for errors defined by the Study Suite."""
    pass

class DataManagementError(ApplicationError):
    """Raised when data management (saving/loading) fails."""
    pass

class DeckError(ApplicationError):
    """Raised when an error occurs relating to decks."""
    pass

class SaveError(DataManagementError): pass
class LoadError(DataManagementError): pass
class DeckNotFoundError(DeckError): pass
class DeckExistsError(DeckError): pass