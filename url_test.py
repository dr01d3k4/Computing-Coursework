import re;


protocol = "https?://";

validLetter = "[\w\-_]";

ipDigit = "(" \
	+ "(0|1)?\d?\d" \
	+ "|" \
	+ "(" \
		+ "2[0-4]\d"\
		+ "|" \
		+ "25[0-5]" \
	+ ")" \
	+ ")";
ip = "(" + ipDigit + "\.){3}" + ipDigit;
port = "(:\d{4})?"

domain = "(" + validLetter + "+\.)*";
lastDomain = "(" + validLetter + "+)";

folder = "(/" + validLetter + "+)*";

parameter = validLetter + "+=" + validLetter + "+";

parameterList = "\?" + parameter + "(&" + parameter + ")*";

parameters = "(/" + validLetter + "*" + parameterList + ")?"

urlPattern = r"^" \
	+ protocol \
	+ "(" \
		+ ip \
		+ port \
	+ "|" \
		+ domain \
		+ lastDomain \
	+ ")" \
	+ folder \
	+ parameters \
	+ "/?" \
	+ "$";


print("Matching pattern: " + urlPattern);
print("");

urlPattern = re.compile(urlPattern);

def testUrl(url):
	if (urlPattern.match(url)):
		return True;
	else:
		return False;



urls = [
	"lala",
	"http://www.google.co.uk/",
	"http://24.24.24.24",
	"http://127.0.0.1:8080",
	"http://127.0.0.1:8000/social/Ben/",
	"http://www.google.co.uk/search?q=hello",
	"http://a/?b=c",
	"http://example.site.test.com/folder/another-folder_with/underscores/and?parameters=true&test=extremely",
	"ftp://yep/"
];

for url in urls:
	if (testUrl(url)):
		print("\"%s\" matches" % url);
	else:
		print("\"%s\" doesn't match" % url);