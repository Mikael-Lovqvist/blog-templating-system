from efforting.mvp2.re_tokenizer import simple_re_tokenizer2
from efforting.mvp2.types import symbol
import re
from collections import deque

class token_type:
	class identifier:
		def __init__(self, id):
			self.id = id

		def __repr__(self):
			return f'<{self.__class__.__qualname__} {self.id!r}>'

	class string:
		def __init__(self, value):
			self.value = value

		def __repr__(self):
			return f'<{self.__class__.__qualname__} {self.value!r}>'

	class punctuation:
		def __init__(self, value):
			self.value = value

		def __repr__(self):
			return f'<{self.__class__.__qualname__} {self.value!r}>'

	ws = symbol()


class advanced_iterator:
	def __init__(self, source):
		self.source = source

	def __next__(self):
		return next(self.source)

	def __iter__(self):
		return self

	def switch_source(self, new_source):
		self.source = new_source


class TOKEN:
	SINGLE_QUOTE = symbol()
	WHITESPACE = symbol()
	IDENTIFIER = symbol()
	ESCAPED_SINGLE_QUOTE = symbol()
	from efforting.mvp2.re_tokenizer import UNMATCHED

class string_tokenizer:
	RULES = {
		re.compile(r"\\'"):		TOKEN.ESCAPED_SINGLE_QUOTE,
		re.compile(r"'"):		TOKEN.SINGLE_QUOTE,
	}

	@classmethod
	def tokenize(cls, text, start=0):
		result = ''
		for token, match in simple_re_tokenizer2(text, cls.RULES, start=start):
			if token is TOKEN.SINGLE_QUOTE:
				return result, match.end()
			elif token is TOKEN.ESCAPED_SINGLE_QUOTE:
				result += "'"

			elif token is TOKEN.UNMATCHED:
				result += match

			else:
				raise ValueError(token)

class common_generic_tokenizer:

	RULES = {
		re.compile(r'\s+'):		TOKEN.WHITESPACE,
		re.compile(r"\'"):		TOKEN.SINGLE_QUOTE,
		re.compile(r'\w+'):		TOKEN.IDENTIFIER,
	}



	@classmethod
	def tokenize(cls, text, start=0):
		iterator = advanced_iterator(simple_re_tokenizer2(text, cls.RULES, start=start))
		for token, match in iterator:
			if token is TOKEN.IDENTIFIER:
				yield token_type.identifier(match.group())
			elif token is TOKEN.WHITESPACE:
				yield token_type.ws
			elif token is TOKEN.UNMATCHED:
				yield token_type.punctuation(match)
			elif token is TOKEN.SINGLE_QUOTE:
				string, end = string_tokenizer.tokenize(text, match.end())
				yield token_type.string(string)
				iterator.switch_source(simple_re_tokenizer2(text, cls.RULES, start=end))
			else:
				raise ValueError(token)

test = "define pattern: 'get \\'vector\\' direction' components"

for token in common_generic_tokenizer.tokenize(test):
	print(token)