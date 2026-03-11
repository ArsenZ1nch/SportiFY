import sqlite3
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Student:
    id: int
    first_name: str
    last_name: str
    preferences: List[int]  # List of course IDs in order of preference (1-6)

@dataclass
class Course:
    id: int
    name: str
    location: str
    teacher: str
    theme: str
    weekday: str
    min_participants: int
    max_capacity: int

@dataclass
class Assignment:
    student_id: int
    course_id: int
    semester: int

class SportCourseSorter:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.students: List[Student] = []
        self.courses: List[Course] = []
        self.assignments: List[Assignment] = []
    
    def connect_to_database(self) -> sqlite3.Connection:
        """Establish connection to the SQLite database"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn
    
    def load_students(self) -> List[Student]:
        """Load all students from the database"""
        conn = self.connect_to_database()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ID, VorName, NachName, 
                   Wunsch1_ID, Wunsch2_ID, Wunsch3_ID, 
                   Wunsch4_ID, Wunsch5_ID, Wunsch6_ID
            FROM schueler
            ORDER BY NachName, VorName
        """)
        
        rows = cursor.fetchall()
        self.students = []
        
        for row in rows:
            student_id, first_name, last_name = row[0], row[1], row[2]
            preferences = [row[i] for i in range(3, 9) if row[i] is not None]
            
            student = Student(
                id=student_id,
                first_name=first_name,
                last_name=last_name,
                preferences=preferences
            )
            self.students.append(student)
        
        conn.close()
        print(f"Loaded {len(self.students)} students")
        return self.students
    
    def load_courses(self) -> List[Course]:
        """Load all available courses from the database"""
        conn = self.connect_to_database()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ID, KursName, Sporthalle, Lehrkraft, 
                   Themenfeld, Wochentag, ifMinAnzahlVorhanden, PlatzanzahlMAX
            FROM sportkurs
            ORDER BY KursName
        """)
        
        rows = cursor.fetchall()
        self.courses = []
        
        for row in rows:
            course = Course(
                id=row[0],
                name=row[1],
                location=row[2],
                teacher=row[3],
                theme=row[4],
                weekday=row[5],
                min_participants=row[6],
                max_capacity=row[7]
            )
            self.courses.append(course)
        
        conn.close()
        print(f"Loaded {len(self.courses)} courses")
        return self.courses
    
    def load_existing_assignments(self, semester: int) -> List[Assignment]:
        """Load existing assignments for a given semester"""
        conn = self.connect_to_database()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT schueler_ID, sportkurs_ID, Semester
            FROM sportkurse_zuteilung
            WHERE Semester = ?
        """, (semester,))
        
        rows = cursor.fetchall()
        self.assignments = []
        
        for row in rows:
            assignment = Assignment(
                student_id=row[0],
                course_id=row[1],
                semester=row[2]
            )
            self.assignments.append(assignment)
        
        conn.close()
        print(f"Loaded {len(self.assignments)} existing assignments for semester {semester}")
        return self.assignments
    
    def get_course_by_id(self, course_id: int) -> Optional[Course]:
        """Get course object by ID"""
        for course in self.courses:
            if course.id == course_id:
                return course
        return None
    
    def count_assigned_students(self, course_id: int, current_assignments: Dict[int, int]) -> int:
        """Count how many students are currently assigned to a course"""
        return sum(1 for assigned_course_id in current_assignments.values() 
                  if assigned_course_id == course_id)
    
    def is_course_available(self, course_id: int, current_assignments: Dict[int, int]) -> bool:
        """Check if a course has available capacity"""
        course = self.get_course_by_id(course_id)
        if not course:
            return False
        
        current_count = self.count_assigned_students(course_id, current_assignments)
        return current_count < course.max_capacity
    
    def calculate_preference_score(self, student: Student, course_id: int) -> int:
        """Calculate preference score (lower is better - 1 is highest preference)"""
        try:
            preference_index = student.preferences.index(course_id)
            return preference_index + 1  # 1-based scoring (1 = first choice, 2 = second, etc.)
        except ValueError:
            return 999  # Course not in student's preferences
    
    def sort_courses_for_semester(self, semester: int) -> Dict[int, int]:
        """
        Main algorithm to sort students into courses for a semester
        Returns a dictionary mapping student_id to course_id
        """
        print(f"Starting course sorting for semester {semester}")
        
        # Load data
        self.load_students()
        self.load_courses()
        
        # Initialize assignments dictionary
        assignments = {}  # student_id -> course_id
        unassigned_students = list(self.students)
        
        # Sort students by some priority criteria (e.g., name for consistency)
        unassigned_students.sort(key=lambda s: (s.last_name, s.first_name))
        
        # Iterative assignment process
        iteration = 0
        max_iterations = 10  # Prevent infinite loops
        
        while unassigned_students and iteration < max_iterations:
            iteration += 1
            print(f"Iteration {iteration}: {len(unassigned_students)} students remaining")
            
            students_to_remove = []
            
            for student in unassigned_students:
                # Try to assign student to their highest preference available
                best_course_id = None
                best_score = 999
                
                for course_id in student.preferences:
                    if self.is_course_available(course_id, assignments):
                        score = self.calculate_preference_score(student, course_id)
                        if score < best_score:
                            best_score = score
                            best_course_id = course_id
                
                # If found an available course, assign the student
                if best_course_id is not None:
                    assignments[student.id] = best_course_id
                    students_to_remove.append(student)
                    print(f"  Assigned {student.first_name} {student.last_name} to {self.get_course_by_id(best_course_id).name} (Preference {best_score})")
            
            # Remove successfully assigned students
            for student in students_to_remove:
                unassigned_students.remove(student)
            
            # If no students were assigned in this iteration, break to avoid infinite loop
            if not students_to_remove:
                print("No more assignments possible in this iteration")
                break
        
        # Handle remaining unassigned students (assign to any available course)
        if unassigned_students:
            print(f"Handling {len(unassigned_students)} remaining unassigned students")
            for student in unassigned_students:
                for course in self.courses:
                    if self.is_course_available(course.id, assignments):
                        assignments[student.id] = course.id
                        print(f"  Assigned {student.first_name} {student.last_name} to {course.name} (No preference available)")
                        break
        
        print(f"Sorting complete. Assigned {len(assignments)} students")
        return assignments
    
    def save_assignments_to_database(self, assignments: Dict[int, int], semester: int) -> bool:
        """Save assignments to the sportkurse_zuteilung table"""
        conn = self.connect_to_database()
        cursor = conn.cursor()
        
        try:
            # Clear existing assignments for this semester
            cursor.execute("DELETE FROM sportkurse_zuteilung WHERE Semester = ?", (semester,))
            
            # Insert new assignments
            for student_id, course_id in assignments.items():
                cursor.execute("""
                    INSERT INTO sportkurse_zuteilung (Semester, schueler_ID, sportkurs_ID)
                    VALUES (?, ?, ?)
                """, (semester, student_id, course_id))
            
            conn.commit()
            print(f"Successfully saved {len(assignments)} assignments for semester {semester}")
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Error saving assignments: {e}")
            return False
        finally:
            conn.close()
    
    def generate_assignment_report(self, assignments: Dict[int, int]) -> Dict:
        """Generate a report about the assignment results"""
        report = {
            'total_students': len(self.students),
            'assigned_students': len(assignments),
            'courses': {}
        }
        
        # Count assignments per course
        course_counts = {}
        preference_scores = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 'none': 0}
        
        for student_id, course_id in assignments.items():
            # Count per course
            if course_id not in course_counts:
                course_counts[course_id] = 0
            course_counts[course_id] += 1
            
            # Calculate preference score
            student = next((s for s in self.students if s.id == student_id), None)
            if student:
                score = self.calculate_preference_score(student, course_id)
                if score <= 6:
                    preference_scores[score] += 1
                else:
                    preference_scores['none'] += 1
        
        # Build course details
        for course in self.courses:
            assigned_count = course_counts.get(course.id, 0)
            report['courses'][course.id] = {
                'name': course.name,
                'assigned': assigned_count,
                'capacity': course.max_capacity,
                'utilization': (assigned_count / course.max_capacity * 100) if course.max_capacity > 0 else 0,
                'meets_minimum': assigned_count >= course.min_participants if course.min_participants > 0 else True
            }
        
        report['preference_distribution'] = preference_scores
        report['average_preference'] = sum(score * count for score, count in preference_scores.items() 
                                         if isinstance(score, int)) / len(assignments) if assignments else 0
        
        return report
    
    def print_report(self, report: Dict):
        """Print a formatted assignment report"""
        print("\n" + "="*60)
        print("COURSE ASSIGNMENT REPORT")
        print("="*60)
        print(f"Total students: {report['total_students']}")
        print(f"Assigned students: {report['assigned_students']}")
        print(f"Average preference score: {report['average_preference']:.2f}")
        print("\nPreference Distribution:")
        for score in range(1, 7):
            print(f"  Preference {score}: {report['preference_distribution'].get(score, 0)} students")
        print(f"  No preference: {report['preference_distribution'].get('none', 0)} students")
        
        print("\nCourse Details:")
        for course_id, details in report['courses'].items():
            status = "✓" if details['meets_minimum'] else "✗"
            print(f"  {details['name']}: {details['assigned']}/{details['capacity']} "
                  f"({details['utilization']:.1f}%) {status}")
        print("="*60)

def main():
    """Main function to run the course sorting algorithm"""
    # Get the database path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'database', 'database.db')
    
    if not os.path.exists(db_path):
        print(f"Database not found at: {db_path}")
        return
    
    # Create sorter instance
    sorter = SportCourseSorter(db_path)
    
    # Get semester from user input
    try:
        semester = int(input("Enter semester number (e.g., 1, 2, 3, 4): "))
    except ValueError:
        print("Invalid semester number. Using default semester 1.")
        semester = 1
    
    print(f"\nSorting courses for semester {semester}...")
    
    # Run the sorting algorithm
    assignments = sorter.sort_courses_for_semester(semester)
    
    # Save results to database
    if sorter.save_assignments_to_database(assignments, semester):
        print("Assignments saved successfully!")
    else:
        print("Failed to save assignments.")
    
    # Generate and print report
    report = sorter.generate_assignment_report(assignments)
    sorter.print_report(report)

if __name__ == "__main__":
    main()