import json
import os
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import filedialog

class ExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("Expense Tracker - Трекер расходов")
        self.root.geometry("800x600")
        
        # Данные
        self.expenses = []
        self.data_file = "expenses.json"
        
        # Загрузка данных из файла
        self.load_data()
        
        # Создание интерфейса
        self.create_widgets()
        
        # Обновление таблицы
        self.refresh_table()
        
    def create_widgets(self):
        # Рамка для ввода данных
        input_frame = ttk.LabelFrame(self.root, text="Добавление расхода", padding=10)
        input_frame.pack(fill="x", padx=10, pady=5)
        
        # Поле Сумма
        ttk.Label(input_frame, text="Сумма:").grid(row=0, column=0, padx=5, pady=5)
        self.amount_entry = ttk.Entry(input_frame, width=20)
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5)
        
        # Поле Категория
        ttk.Label(input_frame, text="Категория:").grid(row=0, column=2, padx=5, pady=5)
        self.category_var = tk.StringVar()
        categories = ["Еда", "Транспорт", "Развлечения", "Здоровье", "Жилье", "Другое"]
        self.category_combo = ttk.Combobox(input_frame, textvariable=self.category_var, 
                                           values=categories, width=18)
        self.category_combo.grid(row=0, column=3, padx=5, pady=5)
        self.category_combo.set("Еда")
        
        # Поле Дата
        ttk.Label(input_frame, text="Дата (ГГГГ-ММ-ДД):").grid(row=0, column=4, padx=5, pady=5)
        self.date_entry = ttk.Entry(input_frame, width=15)
        self.date_entry.grid(row=0, column=5, padx=5, pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Кнопка Добавить
        self.add_btn = ttk.Button(input_frame, text="Добавить расход", command=self.add_expense)
        self.add_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # Рамка для фильтрации
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)
        
        # Фильтр по категории
        ttk.Label(filter_frame, text="Категория:").grid(row=0, column=0, padx=5, pady=5)
        self.filter_category_var = tk.StringVar()
        self.filter_category_combo = ttk.Combobox(filter_frame, textvariable=self.filter_category_var,
                                                  values=["Все"] + categories, width=18)
        self.filter_category_combo.grid(row=0, column=1, padx=5, pady=5)
        self.filter_category_combo.set("Все")
        
        # Фильтр по дате
        ttk.Label(filter_frame, text="Дата от (ГГГГ-ММ-ДД):").grid(row=0, column=2, padx=5, pady=5)
        self.date_from_entry = ttk.Entry(filter_frame, width=12)
        self.date_from_entry.grid(row=0, column=3, padx=5, pady=5)
        
        ttk.Label(filter_frame, text="до:").grid(row=0, column=4, padx=5, pady=5)
        self.date_to_entry = ttk.Entry(filter_frame, width=12)
        self.date_to_entry.grid(row=0, column=5, padx=5, pady=5)
        
        # Кнопка Применить фильтр
        self.filter_btn = ttk.Button(filter_frame, text="Применить фильтр", command=self.apply_filter)
        self.filter_btn.grid(row=0, column=6, padx=10, pady=5)
        
        # Кнопка Сбросить фильтр
        self.reset_btn = ttk.Button(filter_frame, text="Сбросить", command=self.reset_filter)
        self.reset_btn.grid(row=0, column=7, padx=5, pady=5)
        
        # Рамка для таблицы и суммы
        table_frame = ttk.Frame(self.root)
        table_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Таблица расходов
        columns = ("ID", "Сумма", "Категория", "Дата")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings")
self.tree.heading("ID", text="ID")
        self.tree.heading("Сумма", text="Сумма (₽)")
        self.tree.heading("Категория", text="Категория")
        self.tree.heading("Дата", text="Дата")
        
        self.tree.column("ID", width=50)
        self.tree.column("Сумма", width=100)
        self.tree.column("Категория", width=150)
        self.tree.column("Дата", width=120)
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Кнопки удаления и редактирования
        button_frame = ttk.Frame(self.root)
        button_frame.pack(fill="x", padx=10, pady=5)
        
        self.delete_btn = ttk.Button(button_frame, text="Удалить выбранный расход", command=self.delete_expense)
        self.delete_btn.pack(side="left", padx=5)
        
        self.edit_btn = ttk.Button(button_frame, text="Редактировать выбранный расход", command=self.edit_expense)
        self.edit_btn.pack(side="left", padx=5)
        
        # Рамка для отображения суммы
        sum_frame = ttk.LabelFrame(self.root, text="Статистика", padding=10)
        sum_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(sum_frame, text="Сумма расходов за выбранный период:").pack(side="left", padx=5)
        self.sum_label = ttk.Label(sum_frame, text="0.00 ₽", font=("Arial", 12, "bold"))
        self.sum_label.pack(side="left", padx=10)
        
    def validate_amount(self, amount_str):
        try:
            amount = float(amount_str)
            if amount <= 0:
                return False, "Сумма должна быть положительным числом"
            return True, amount
        except ValueError:
            return False, "Сумма должна быть числом"
    
    def validate_date(self, date_str):
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return True, date_str
        except ValueError:
            return False, "Дата должна быть в формате ГГГГ-ММ-ДД"
    
    def add_expense(self):
        # Валидация суммы
        amount_valid, amount_result = self.validate_amount(self.amount_entry.get())
        if not amount_valid:
            messagebox.showerror("Ошибка", amount_result)
            return
        amount = amount_result
        
        # Валидация даты
        date_valid, date_result = self.validate_date(self.date_entry.get())
        if not date_valid:
            messagebox.showerror("Ошибка", date_result)
            return
        date = date_result
        
        category = self.category_var.get()
        
        # Создание новой записи
        expense = {
            "id": len(self.expenses) + 1 if self.expenses else 1,
            "amount": amount,
            "category": category,
            "date": date
        }
        
        self.expenses.append(expense)
        self.save_data()
        self.refresh_table()
        
        # Очистка полей
        self.amount_entry.delete(0, tk.END)
        self.category_combo.set("Еда")
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        messagebox.showinfo("Успех", "Расход успешно добавлен!")
    
    def refresh_table(self):
        # Очистка таблицы
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        # Получение отфильтрованных данных
        filtered_expenses = self.get_filtered_expenses()
        
        # Заполнение таблицы
        for expense in filtered_expenses:
            self.tree.insert("", "end", values=(
                expense["id"],
                f"{expense['amount']:.2f}",
                expense["category"],
                expense["date"]
            ))
        
        # Подсчет суммы за период
        self.calculate_sum()
    
    def get_filtered_expenses(self):


filtered = self.expenses.copy()
        
        # Фильтр по категории
        category_filter = self.filter_category_var.get()
        if category_filter != "Все":
            filtered = [e for e in filtered if e["category"] == category_filter]
        
        # Фильтр по дате
        date_from = self.date_from_entry.get()
        date_to = self.date_to_entry.get()
        
        if date_from:
            try:
                date_from_obj = datetime.strptime(date_from, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") >= date_from_obj]
            except ValueError:
                pass
        
        if date_to:
            try:
                date_to_obj = datetime.strptime(date_to, "%Y-%m-%d")
                filtered = [e for e in filtered if datetime.strptime(e["date"], "%Y-%m-%d") <= date_to_obj]
            except ValueError:
                pass
        
        return filtered
    
    def calculate_sum(self):
        filtered = self.get_filtered_expenses()
        total = sum(expense["amount"] for expense in filtered)
        self.sum_label.config(text=f"{total:.2f} ₽")
    
    def apply_filter(self):
        self.refresh_table()
    
    def reset_filter(self):
        self.filter_category_var.set("Все")
        self.date_from_entry.delete(0, tk.END)
        self.date_to_entry.delete(0, tk.END)
        self.refresh_table()
    
    def delete_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите расход для удаления")
            return
        
        # Получение ID выбранной записи
        item = self.tree.item(selected[0])
        expense_id = int(item['values'][0])
        
        # Удаление из списка
        self.expenses = [e for e in self.expenses if e["id"] != expense_id]
        
        # Перенумерация ID
        for i, expense in enumerate(self.expenses, 1):
            expense["id"] = i
        
        self.save_data()
        self.refresh_table()
        messagebox.showinfo("Успех", "Расход удален")
    
    def edit_expense(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Предупреждение", "Выберите расход для редактирования")
            return
        
        item = self.tree.item(selected[0])
        expense_id = int(item['values'][0])
        
        # Поиск записи для редактирования
        expense_to_edit = None
        for expense in self.expenses:
            if expense["id"] == expense_id:
                expense_to_edit = expense
                break
        
        if expense_to_edit:
            # Создание окна редактирования
            edit_window = tk.Toplevel(self.root)
            edit_window.title("Редактирование расхода")
            edit_window.geometry("300x200")
            
            ttk.Label(edit_window, text="Сумма:").pack(pady=5)
            amount_edit = ttk.Entry(edit_window)
            amount_edit.insert(0, str(expense_to_edit["amount"]))
            amount_edit.pack(pady=5)
            
            ttk.Label(edit_window, text="Категория:").pack(pady=5)
            category_edit = ttk.Combobox(edit_window, values=["Еда", "Транспорт", "Развлечения", "Здоровье", "Жилье", "Другое"])
            category_edit.set(expense_to_edit["category"])
            category_edit.pack(pady=5)
            
            ttk.Label(edit_window, text="Дата (ГГГГ-ММ-ДД):").pack(pady=5)
            date_edit = ttk.Entry(edit_window)
            date_edit.insert(0, expense_to_edit["date"])
            date_edit.pack(pady=5)
            
            def save_edit():
                # Валидация
                valid, amount = self.validate_amount(amount_edit.get())
                if not valid:
                    messagebox.showerror("Ошибка", amount)
                    return
                
                valid, date = self.validate_date(date_edit.get())


if not valid:
                    messagebox.showerror("Ошибка", date)
                    return
                
                expense_to_edit["amount"] = amount
                expense_to_edit["category"] = category_edit.get()
                expense_to_edit["date"] = date
                
                self.save_data()
                self.refresh_table()
                edit_window.destroy()
                messagebox.showinfo("Успех", "Расход обновлен")
            
            ttk.Button(edit_window, text="Сохранить", command=save_edit).pack(pady=10)
    
    def save_data(self):
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.expenses, f, ensure_ascii=False, indent=4)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные: {e}")
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.expenses = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить данные: {e}")
                self.expenses = []

def main():
    root = tk.Tk()
    app = ExpenseTracker(root)
    root.mainloop()

if __name__ == "__main__":
    main()