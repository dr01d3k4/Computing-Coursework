import re;



protocol = "(http|https)://";

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

urlPattern = re.compile(urlPattern);