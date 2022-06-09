import template.word as wt
from copy import deepcopy
import json

url_vocabulary = "https://www.vocabulary.com/dictionary/"
url_cambridge = "https://dictionary.cambridge.org/dictionary/english/"
url_powerthesaurus = "https://www.powerthesaurus.org/"

def make_word_msg(query):
	'''
	Parameters
	----------
	query : string
	msg : dict 
	'''
	texts = query.split("\n")
	word = texts[0]
	details = texts[1] if len(texts) > 1 else None

	# main msg
	msg = deepcopy(wt.word_t)
	msg["body"]["contents"][0]["text"] = word

	# details msg
	if details:
		details_msg = deepcopy(wt.details_t)
		details_msg["text"] = details
		msg["body"]["contents"].append(details_msg)

	# vocabulary.com, dictionary.cambridge.org, powerthesaurus
	if ' ' not in word:
		vocabulary_msg = deepcopy(wt.vocabulary_t)
		vocabulary_msg["action"]["uri"] = url_vocabulary+word+""
		msg["body"]["contents"].append(vocabulary_msg)

		cambridge_msg = deepcopy(wt.cambridge_t)
		cambridge_msg["action"]["uri"] = url_cambridge+word+""
		msg["body"]["contents"].append(cambridge_msg)

		powerthesaurus_msg = deepcopy(wt.powerthesaurus_t)
		powerthesaurus_msg["action"]["uri"] = url_powerthesaurus+word+""
		msg["body"]["contents"].append(powerthesaurus_msg)
	else:
		word = "_".join(word.split(" "))
		powerthesaurus_msg = deepcopy(wt.powerthesaurus_t)
		powerthesaurus_msg["action"]["uri"] = url_powerthesaurus+word+""
		msg["body"]["contents"].append(powerthesaurus_msg)
	msg["body"]["contents"].append(deepcopy(wt.next_t))

	return msg

def set_progress(msg_str, idx, percentage):
	msg = json.loads(msg_str)
	msg["contents"][idx]["footer"]["contents"][0]["text"] = str(percentage)+"%"
	msg["contents"][idx]["footer"]["contents"][1]["contents"][0]["width"] = str(percentage)+"%"
	return msg