JSON_COLON = ": ";
JSON_COMMA_SEPERATOR = ", ";
JSON_NEWLINE_CHARACTER = "\n";
JSON_NEWLINE_SEPERATOR = "," + JSON_NEWLINE_CHARACTER;
JSON_TAB_CHARACTER = "\t";



def writeJson(object, indent = 1):
	json = "";

	objectType = type(object);
	tabs = JSON_TAB_CHARACTER * indent;
	oneLessTabs = JSON_TAB_CHARACTER * (indent - 1);

	if (objectType == dict):
		json = "{" \
			+ JSON_NEWLINE_CHARACTER \
			+ JSON_NEWLINE_SEPERATOR.join([tabs + "\"" + str(key) + "\"" + JSON_COLON + writeJson(value, indent = indent + 1) for key, value in object.iteritems()]) \
			+ JSON_NEWLINE_CHARACTER \
			+ oneLessTabs \
			+ "}";

	elif ((objectType == tuple) or (objectType == list)):
		isSingleLine = True;
		for i in object:
			if (type(i) == dict):
				isSingleLine = False;
				break;

		if (isSingleLine):
			json = "[" \
				+ JSON_COMMA_SEPERATOR.join([writeJson(i) for i in object]) \
				+ "]";
		else:
			json = "[" \
				+ JSON_NEWLINE_CHARACTER \
				+ tabs \
				+ JSON_COMMA_SEPERATOR.join([writeJson(i, indent = indent + 1) for i in object]) \
				+ JSON_NEWLINE_CHARACTER \
				+ oneLessTabs \
				+ "]";

	elif ((objectType == str) or (objectType == unicode)):
		json = "\"" + object.replace("\n", " ").replace("\r", " ") + "\"";

	elif (objectType == bool):
		json = "true" if object else "false";

	else:
		json = str(object);

	json = str(json);
	return json;