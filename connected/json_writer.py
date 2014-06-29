JSON_COLON = ": ";
JSON_COMMA_SEPERATOR = ", ";
JSON_NEWLINE_CHARACTER = "\n";
JSON_NEWLINE_SEPERATOR = "," + JSON_NEWLINE_CHARACTER;
JSON_TAB_CHARACTER = "\t";



condenseJson = False;
if (condenseJson):
	JSON_COLON = ":";
	JSON_COMMA_SEPERATOR = ",";
	JSON_NEWLINE_CHARACTER = "";
	JSON_NEWLINE_SEPERATOR = ",";
	JSON_TAB_CHARACTER = "";



def isSingleLineList(object):
	isSingleLine = True;
	for i in object:
		if (type(i) == dict):
			isSingleLine = False;
			break;
		elif ((type(i) == list) or (type(i) == tuple)):
			if (not isSingleLineList(i)):
				isSingleLine = False;
				break;

	return isSingleLine;



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
		isSingleLine = isSingleLineList(object);

		if (isSingleLine):
			json = "[" \
				+ JSON_COMMA_SEPERATOR.join([writeJson(i) for i in object]) \
				+ "]";
		else:
			json = "[" \
				+ JSON_NEWLINE_CHARACTER \
				+ JSON_NEWLINE_SEPERATOR.join([tabs + writeJson(i, indent = indent + 1) for i in object]) \
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


if (__name__ == "__main__"):
	tests = [
		{
			"name": "Number",
			"object": 2,
			"expected": "2"
		},
		{
			"name": "String",
			"object": "Hello",
			"expected": "\"Hello\""
		},
		{
			"name": "Boolean",
			"object": True,
			"expected": "true"
		},
		{
			"name": "List of number/string/boolean",
			"object": [1, 2, "hello", False, "world"],
			"expected": "[1, 2, \"hello\", false, \"world\"]"
		},
		{
			"name": "Tuple",
			"object": (1, 2),
			"expected": "[1, 2]"
		},
		{							
			"name": "List of list of number/string/boolean",
			"object": [[1, 2, True], ["Hello"], "No", [5, 8]],
			"expected": "[[1, 2, true], [\"Hello\"], \"No\", [5, 8]]"
		},
		{
			"name": "Dictionary with number/string/boolean values",
			"object": {
				"key": "value",
				"another": False,
				"number": 2
			},
			"expected": """{
	"another": false,
	"key": "value",
	"number": 2
}"""
		},
		{
			"name": "Dictionary with list of number/string/boolean values",
			"object": {
				"list": [1, 2, 3],
				"another": ["hello", "world", False]
			},
			"expected": """{
	"list": [1, 2, 3],
	"another": ["hello", "world", false]
}"""
		},
		{
			"name": "List with dictionary elements",
			"object": [1, 2, [3, 4, 5], {"hello": "world", "example": True}, 7, [8, 9]],
			"expected": """[
	1,
	2,
	[3, 4, 5],
	{
		"hello": "world",
		"example": true
	},
	7,
	[8, 9]
]"""
	},
	{
		"name": "Lots of nesting",
		"object": {"level1": [1, [2, {"more": {"etc": [3, 4]}}]]},
		"expected": """{
	"level1": [
		1,
		[
			2,
			{
				"more": {
					"etc": [3, 4]
				}
			}
		]
	]
}"""
		}
	];

	for i in range(len(tests)):
		test = tests[i];
		print("Doing test #%d: \"%s\"" % (i + 1, test["name"]));
		print("Expect");
		print(test["object"]);
		print("in JSON to be");
		print(test["expected"]);
		print("Actual output");
		output = writeJson(test["object"]);
		print(output);
		match = (test["expected"] == output);
		print("Is a match: %s" % match);
		print("");
		print("");