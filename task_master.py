# Task Manager

class Task:
    def __init__(self, title, description, deadline, priority):
        self.title = title
        self.description = description
        self.deadline = deadline
        self.priority = priority
        self.status = "Not Started"

    def start_task(self):
        self.status = "In Progress"

    def complete_task(self):
        self.status = "Completed"

    def put_on_hold(self):
        self.status = "On Hold"

    def view_task(self):
        return {
            "Title": self.title,
            "Description": self.description,
            "Deadline": self.deadline,
            "Priority": self.priority,
            "Status": self.status
        }


class TaskManager:
    def __init__(self):
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def view_all_tasks(self):
        for i, task in enumerate(self.tasks, start=1):
            print(f"Task {i}:")
            for key, value in task.view_task().items():
                print(f"{key}: {value}")
            print()

    def view_specific_task(self, task_number):
        try:
            task = self.tasks[task_number - 1]
            for key, value in task.view_task().items():
                print(f"{key}: {value}")
        except IndexError:
            print("Task not found.")

    def delete_task(self, task_number):
        try:
            del self.tasks[task_number - 1]
            print("Task deleted successfully.")
        except IndexError:
            print("Task not found.")


def main():
    task_manager = TaskManager()

    while True:
        print("\nTask Manager")
        print("1. Add Task")
        print("2. View All Tasks")
        print("3. View Specific Task")
        print("4. Delete Task")
        print("5. Exit")

        choice = input("Enter your choice: ")

        if choice == "1":
            title = input("Enter task title: ")
            description = input("Enter task description: ")
            deadline = input("Enter task deadline: ")
            priority = input("Enter task priority: ")
            task = Task(title, description, deadline, priority)
            task_manager.add_task(task)
            print("Task added successfully.")
        elif choice == "2":
            task_manager.view_all_tasks()
        elif choice == "3":
            task_number = int(input("Enter task number: "))
            task_manager.view_specific_task(task_number)
        elif choice == "4":
            task_number = int(input("Enter task number: "))
            task_manager.delete_task(task_number)
        elif choice == "5":
            break
        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    main()