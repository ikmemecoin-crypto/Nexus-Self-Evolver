# Task Manager Code Block

# Import necessary libraries
import datetime
import time

# Define a Task class
class Task:
    def __init__(self, name, priority, deadline):
        """
        Initialize a Task object.

        Args:
            name (str): Task name.
            priority (int): Task priority (1-5).
            deadline (datetime.date): Task deadline.
        """
        self.name = name
        self.priority = priority
        self.deadline = deadline

    def __str__(self):
        """
        Return a string representation of the Task object.
        """
        return f"Task: {self.name}, Priority: {self.priority}, Deadline: {self.deadline}"

# Define a TaskManager class
class TaskManager:
    def __init__(self):
        """
        Initialize a TaskManager object.
        """
        self.tasks = []

    def add_task(self, task):
        """
        Add a task to the task list.

        Args:
            task (Task): Task object to add.
        """
        self.tasks.append(task)

    def remove_task(self, task_name):
        """
        Remove a task from the task list.

        Args:
            task_name (str): Name of the task to remove.
        """
        self.tasks = [task for task in self.tasks if task.name != task_name]

    def view_tasks(self):
        """
        Print all tasks in the task list.
        """
        for task in self.tasks:
            print(task)

    def sort_tasks(self):
        """
        Sort tasks by deadline and priority.
        """
        self.tasks.sort(key=lambda task: (task.deadline, task.priority))

# Example usage:
if __name__ == "__main__":
    # Create a TaskManager object
    task_manager = TaskManager()

    # Create Task objects
    task1 = Task("Task 1", 3, datetime.date(2024, 9, 20))
    task2 = Task("Task 2", 2, datetime.date(2024, 9, 15))
    task3 = Task("Task 3", 1, datetime.date(2024, 9, 25))

    # Add tasks to the task list
    task_manager.add_task(task1)
    task_manager.add_task(task2)
    task_manager.add_task(task3)

    # View tasks
    print("Tasks:")
    task_manager.view_tasks()

    # Sort tasks
    task_manager.sort_tasks()

    # View sorted tasks
    print("\nSorted Tasks:")
    task_manager.view_tasks()

    # Remove a task
    task_manager.remove_task("Task 2")

    # View tasks after removal
    print("\nTasks after removal:")
    task_manager.view_tasks()