# Copyright 2025-2026 Louis Masarei-Boulton
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.

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
