#Jill Wesley
#CIS216
#WEEK 10 VIBE CODING

import os
import sys
from statistics import mean


FILE_NAME = "student_grades.txt"


class Student:
	"""Store one student's identity, test scores, average, and letter grade."""

	def __init__(self, name: str, student_id: str, scores: list[float]) -> None:
		if len(scores) != 3:
			raise ValueError("Exactly three test scores are required.")
		if any(score < 0 or score > 100 for score in scores):
			raise ValueError("Scores must be between 0 and 100.")
		self.name = name.strip()
		self.id = student_id.strip()
		self.test_scores = scores
		self.average = mean(scores)
		self.grade = self.calculate_grade()

	def calculate_grade(self) -> str:
		if self.average >= 90:
			return "A"
		if self.average >= 80:
			return "B"
		if self.average >= 70:
			return "C"
		if self.average >= 60:
			return "D"
		return "F"

	def to_file_line(self) -> str:
		values = [self.name, self.id]
		values.extend(f"{score:.2f}" for score in self.test_scores)
		values.extend((f"{self.average:.2f}", self.grade))
		return "|".join(values)

	@classmethod
	def from_file_line(cls, line: str) -> "Student":
		fields = line.strip().split("|")
		if len(fields) != 7:
			raise ValueError("A record must contain seven pipe-delimited fields.")
		name, student_id = fields[:2]
		scores = [float(value) for value in fields[2:5]]
		return cls(name, student_id, scores)


class StudentRecordManager:
	"""Manage student records and their file representation."""

	def __init__(self, file_name: str = FILE_NAME) -> None:
		self.file_name = file_name
		self.students: list[Student] = []
		self.load_records()

	def add_student(self, student: Student) -> None:
		if any(existing.id.lower() == student.id.lower() for existing in self.students):
			raise ValueError("A student with that ID already exists.")
		self.students.append(student)

	def load_records(self) -> None:
		if not os.path.exists(self.file_name):
			return
		try:
			with open(self.file_name, "r", encoding="utf-8") as file:
				for line_number, line in enumerate(file, start=1):
					if not line.strip():
						continue
					try:
						self.add_student(Student.from_file_line(line))
					except ValueError as error:
						print(f"Skipped invalid record on line {line_number}: {error}")
		except OSError as error:
			print(f"Could not load {self.file_name}: {error}")

	def save_records(self) -> bool:
		try:
			with open(self.file_name, "w", encoding="utf-8") as file:
				for student in self.students:
					file.write(student.to_file_line() + "\n")
		except OSError as error:
			print(f"Could not save {self.file_name}: {error}")
			return False
		return True

	def search_by_name(self, name: str) -> list[Student]:
		search_text = name.strip().casefold()
		return [student for student in self.students if search_text in student.name.casefold()]

	def class_statistics(self) -> tuple[float, float, float] | None:
		if not self.students:
			return None
		averages = [student.average for student in self.students]
		return max(averages), min(averages), mean(averages)


def read_score(test_number: int) -> float:
	while True:
		try:
			score = float(input(f"Test {test_number} score (0-100): "))
			if 0 <= score <= 100:
				return score
			print("Please enter a score from 0 to 100.")
		except ValueError:
			print("Please enter a valid number.")


def get_menu_choice() -> str:
	"""Read one menu choice, returning ESC immediately on an interactive terminal."""
	if not sys.stdin.isatty():
		return input("Choose an option (ESC to exit): ").strip()
	if os.name == "nt":
		import msvcrt

		key = msvcrt.getwch()
		print(key)
		return "\x1b" if key == "\x1b" else key

	import termios
	import tty

	file_descriptor = sys.stdin.fileno()
	old_settings = termios.tcgetattr(file_descriptor)
	try:
		tty.setraw(file_descriptor)
		key = sys.stdin.read(1)
		print(key if key != "\x1b" else "ESC")
		return key
	finally:
		termios.tcsetattr(file_descriptor, termios.TCSADRAIN, old_settings)


def display_table(students: list[Student]) -> None:
	if not students:
		print("No student records found.")
		return
	print("\nName                 ID          Test 1   Test 2   Test 3   Average  Grade")
	print("-" * 78)
	for student in students:
		print(
			f"{student.name[:20]:<20} {student.id[:10]:<10} "
			f"{student.test_scores[0]:>7.2f}  {student.test_scores[1]:>7.2f}  "
			f"{student.test_scores[2]:>7.2f}  {student.average:>7.2f}  {student.grade:>5}"
		)


def add_student_from_input(manager: StudentRecordManager) -> None:
	name = input("Student name: ").strip()
	student_id = input("Student ID: ").strip()
	if not name or not student_id:
		raise ValueError("Name and ID are required.")
	scores = [read_score(number) for number in range(1, 4)]
	manager.add_student(Student(name, student_id, scores))
	print(f"Added {name}.")


def run() -> None:
	manager = StudentRecordManager()
	if manager.students:
		print(f"Loaded {len(manager.students)} student record(s) from {FILE_NAME}.")

	while True:
		print("\nStudent Record Manager")
		print("1. Add student")
		print("2. Display all students")
		print("3. Display class statistics")
		print("4. Search by student name")
		print("5. Exit or press ESC to save and exit")
		try:
			choice = get_menu_choice()
			if choice in ("5", "\x1b"):
				if manager.save_records():
					print(f"Saved records to {FILE_NAME}. Goodbye!")
				break
			if choice == "1":
				add_student_from_input(manager)
			elif choice == "2":
				display_table(manager.students)
			elif choice == "3":
				statistics = manager.class_statistics()
				if statistics is None:
					print("Add students before calculating class statistics.")
				else:
					highest, lowest, class_average = statistics
					print(f"Highest average: {highest:.2f}")
					print(f"Lowest average:  {lowest:.2f}")
					print(f"Class average:   {class_average:.2f}")
			elif choice == "4":
				matches = manager.search_by_name(input("Enter name to search: "))
				display_table(matches)
			else:
				print("Please choose 1, 2, 3, 4, 5, or press ESC to exit.")
		except ValueError as error:
			print(f"Error: {error}")
		except (EOFError, KeyboardInterrupt):
			print("\nInput ended. Saving records before exit.")
			manager.save_records()
			break


if __name__ == "__main__":
	run()

