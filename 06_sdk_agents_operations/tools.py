from pathlib import Path
from typing import List, Dict, Any, Optional
import json



def fetch_courses() -> List[Dict[str, Any]]:
	"""
	Load courses from the local `courses.json` and return a flat list of course dictionaries.
	Each returned dict contains the original course fields plus the semester information under
	`semester_number` and `semester_name`.

	Returns
	-------
	List[Dict[str, Any]]
		A list of course dictionaries. Each dictionary will include the keys:
		- code (str)
		- title (str)
		- ects (number)
		- type (str)
		- semester_number (int)
		- semester_name (str)
	"""

	path = Path(__file__).resolve().parent / "courses.json"
	if not path.exists():
		raise FileNotFoundError(f"courses.json not found at: {path}")

	with path.open("r", encoding="utf-8") as fh:
		doc = json.load(fh)

	out: List[Dict[str, Any]] = []
	for sem in doc.get("semesters", []):
		sem_num = sem.get("number")
		sem_name = sem.get("name")
		for c in sem.get("courses", []):
			course = dict(c)
			course["semester_number"] = sem_num
			course["semester_name"] = sem_name
			out.append(course)

	return out

