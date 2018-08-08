from django import template
import mistune
from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatters import HtmlFormatter
register = template.Library()

class HighlightRenderer(mistune.Renderer):
	def block_code(self,code,lang):
		if not lang:
			return '\n<div class="codehilite"><pre><code>%s</code></pre></div>\n' % \
				   mistune.escape(code)
		lexer = get_lexer_by_name(lang, stripall=True)
		formatter = HtmlFormatter()
		return highlight(code, lexer, formatter)

@register.filter
def markdown(value):
	renderer = HighlightRenderer()
	markdown = mistune.Markdown(renderer=renderer)
	return markdown(value)

@register.filter#文章摘要过滤器
def paragraph(value):
	if value.find("```") > -1 and value.find("```")< 150:
		return value.split("```")[0]
	elif value.find("\n") > -1 and value.find("\n") < 150:
		return value.split("\n")[0]
	elif value.find("。") > -1 and value.find("。") < 150:
		return value.split("。")[0]
	else:
		return value[0:150]

@register.filter#首页上方滚动条摘要过滤器
def tagse(value):
	if value.find("```") > -1 and value.find("```") < 30:
		return value.split("```")[0]
	elif value.find("\n") > -1 and value.find("\n") < 30:
		return value.split("\n")[0]
	elif value.find("。") > -1 and value.find("。") < 30:
		return value.split("。")[0]
	else:
		return value[0:30]