from flask import flash
from typing import Literal


###################确定项目通知类型######################
def my_flash(message:str, category:Literal['success','danger','warning','primary'] = 'primary'):
    return flash(message, category)
