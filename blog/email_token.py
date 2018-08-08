from itsdangerous import URLSafeTimedSerializer as utsr
import base64
import re
from django.conf import settings

class Token:
	def __init__(self,security_key):
		self.security_key = security_key
		self.salt = base64.b64encode(security_key.encode())
	"""生成验证令牌"""
	def generate_validate_token(self,username):
		serializer = utsr(self.security_key)
		return serializer.dumps(username,self.salt)
	"""确认验证令牌"""
	def confirm_validate_token(self,token,expiration=3600):
		serializer = utsr(self.security_key)
		return serializer.loads(token,salt=self.salt,max_age=expiration)
	"""删除验证令牌"""
	def remove_validate_token(self,token):
		serializer = utsr(self.security_key)
		print(serializer.loads(token,salt=self.salt))
		return serializer.loads(token,salt=self.salt)
token_confirm = Token(settings.SECRET_KEY)