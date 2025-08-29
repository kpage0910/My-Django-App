from django.db import models

# Create your models here.
class Course:
    """
    Non-database model for course (for use in views)
    A simple class with attributes that represent a course with a name and title.
    """

    def __init__(self, course_name, course_title):
        """
                    The "__init__" method is a special method that is automatically called when a new instance of the class is created.
        It is also called a constructor.
        Here, we initialize a new Course instance.
        Note the two underscores before and after the "init" method name.
        This is a convention in Python to indicate that this method is special.
        "self" refers to the instance of the class that is being created.
        In this course, we are setting the values of the "course_name" and "course_title" attributes of the Course instance.
        """
        self.course_name = f"Course: {course_name}"
        self.course_title = f"Title: {course_title}"

    def __str__(self):
        """
        The "__str__" method is a special method that is called when we want to represent the Course instance as a string.
        This is useful for defining a default way to display the contents of any class instance.
        The "f-string" syntax is used here to format the string output.
        f-string is a way to embed expressions inside string literals, using curly braces {}.
        """
        return f"{self.course_name}: {self.course_title}"