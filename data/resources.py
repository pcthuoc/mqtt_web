# datas/resources.py

from import_export import resources
from .models import Data

class DataResource(resources.ModelResource):
    class Meta:
        model = Data