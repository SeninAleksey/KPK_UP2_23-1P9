"""
Модели для базы данных сервиса рабочих программ (Work Program Service)
Вариант 13, оценка 3

Используемые технологии:
- peewee ORM
- sqlite3
"""

import os
from datetime import datetime
from peewee import (
    SqliteDatabase,
    Model,
    AutoField,
    CharField,
    IntegerField,
    BooleanField,
    ForeignKeyField,
    DateField,
    DateTimeField,
)

# Путь к файлу базы данных
DB_PATH = os.path.join(os.path.dirname(__file__), "work_program_service.db")

# Инициализация базы данных SQLite
database = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    """Базовый класс для всех моделей"""
    class Meta:
        database = database


class Discipline(BaseModel):
    """
    Модель дисциплины (внешняя сущность)
    Хранится в Discipline Service, здесь представлена для связи
    """
    id = AutoField(primary_key=True, verbose_name="ID дисциплины")
    name = CharField(max_length=200, unique=True, verbose_name="Название дисциплины")
    code = CharField(max_length=20, unique=True, verbose_name="Код дисциплины")
    is_active = BooleanField(default=True, verbose_name="Активна")

    class Meta:
        table_name = "discipline"
        verbose_name = "Дисциплина"
        verbose_name_plural = "Дисциплины"


class Specialty(BaseModel):
    """
    Модель специальности (внешняя сущность)
    Хранится в Specialty Service, здесь представлена для связи
    """
    id = AutoField(primary_key=True, verbose_name="ID специальности")
    name = CharField(max_length=200, unique=True, verbose_name="Название специальности")
    code = CharField(max_length=20, unique=True, verbose_name="Код специальности")
    is_active = BooleanField(default=True, verbose_name="Активна")

    class Meta:
        table_name = "specialty"
        verbose_name = "Специальность"
        verbose_name_plural = "Специальности"


class WorkProgram(BaseModel):
    """
    Модель рабочей программы (основная сущность сервиса)
    Связывает дисциплину и специальность (реализация many-to-many)
    """
    id = AutoField(primary_key=True, verbose_name="ID рабочей программы")
    
    # Внешние ключи (NOT NULL)
    discipline = ForeignKeyField(
        Discipline,
        backref="work_programs",
        on_delete="CASCADE",
        verbose_name="Дисциплина"
    )
    specialty = ForeignKeyField(
        Specialty,
        backref="work_programs",
        on_delete="CASCADE",
        verbose_name="Специальность"
    )
    
    # Файловые атрибуты
    file_url = CharField(max_length=500, verbose_name="URL файла")
    file_name = CharField(max_length=200, verbose_name="Имя файла")
    file_size = IntegerField(default=0, verbose_name="Размер в КБ")
    
    # Версионирование
    version = CharField(max_length=20, default="1.0", verbose_name="Версия")
    
    # Метаданные утверждения
    approved_by = CharField(max_length=200, null=True, verbose_name="Утвердивший")
    approval_date = DateField(null=True, verbose_name="Дата утверждения")
    description = CharField(max_length=1000, default="", verbose_name="Описание")
    
    # Системные поля
    is_active = BooleanField(default=True, verbose_name="Активна")
    created_at = DateTimeField(default=datetime.now, verbose_name="Дата создания")
    updated_at = DateTimeField(default=datetime.now, verbose_name="Дата обновления")

    def save(self, *args, **kwargs):
<<<<<<< HEAD
        # updated_at обновляется только при изменении существующей записи
        if self.id is not None:
            self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def soft_delete(cls, work_program_id):
        """Мягкое удаление: is_active = False.
        Возвращает True если деактивировано, иначе False."""
        try:
            updated = cls.update(is_active=False).where(
                (cls.id == work_program_id) & (cls.is_active == True)
            ).execute()
            return bool(updated > 0)
        except Exception:
            return False

    def get_specialties(self):
        """Получить список специальностей привязанных к программе."""
        return list(
            WorkProgramSpecialty.select()
            .where(WorkProgramSpecialty.work_program == self)
        )

    @classmethod
    def get_list(cls, discipline_id=None, specialty_id=None, approved_year=None,
                 is_active=None, search=None, limit=100, offset=0):
        """Получить список рабочих программ с фильтрацией по параметрам."""
        query = cls.select()
        if discipline_id is not None:
            query = query.where(cls.discipline_id == discipline_id)
        if approved_year is not None:
            query = query.where(cls.approved_year == approved_year)
        if is_active is not None:
            query = query.where(cls.is_active == is_active)
        if search is not None:
            query = query.where(cls.title.contains(search))
        if specialty_id is not None:
            query = query.join(WorkProgramSpecialty).where(
                WorkProgramSpecialty.specialty_id == specialty_id
            )
        limit = max(1, min(100, limit))
        offset = max(0, offset)
        return list(query.limit(limit).offset(offset))


class WorkProgramSpecialty(BaseModel):
    """Транзитивная таблица: связь многие ко многим между WorkProgram и Specialty.
    specialty_id — внешний ID из Specialty Service, не хранится локально.
    Валидация существования specialty_id выполняется на уровне сервиса."""
    id = AutoField(primary_key=True)
    work_program = ForeignKeyField(WorkProgram, backref='wp_specialties', on_delete='CASCADE')
    specialty_id = IntegerField()
=======
        """Переопределение save для автоматического обновления updated_at"""
        self.updated_at = datetime.now()
        super().save(*args, **kwargs)
>>>>>>> 5486e8542a3944295f8981f3d5a82c5edc054449

    class Meta:
        table_name = "work_program"
        verbose_name = "Рабочая программа"
        verbose_name_plural = "Рабочие программы"
        # Уникальная комбинация: дисциплина + специальность + версия
        indexes = (
<<<<<<< HEAD
            (('work_program', 'specialty_id'), True),
        )

    @classmethod
    def attach(cls, work_program_id: int, specialty_id: int):
        """Привязать специальность к рабочей программе.
        Возвращает созданную запись."""
        try:
            return cls.create(
                work_program_id=work_program_id,
                specialty_id=specialty_id
            )
        except Exception:
            return None

    @classmethod
    def detach(cls, record_id: int):
        """Отвязать специальность по ID записи о связи.
        Возвращает True если запись удалена, иначе False."""
        try:
            deleted = cls.delete().where(cls.id == record_id).execute()
            return bool(deleted > 0)
        except Exception:
            return False

    @classmethod
    def get_by_program(cls, work_program_id: int):
        """Получить список специальностей рабочей программы по ID рабочей программы."""
        return list(
            cls.select().where(cls.work_program_id == work_program_id)
=======
            (("discipline", "specialty", "version"), True),
>>>>>>> 5486e8542a3944295f8981f3d5a82c5edc054449
        )


def init_db():
    """
    Функция инициализации базы данных
    Создает все таблицы, если они не существуют
    """
    try:
        database.connect()
        # Создание таблиц в правильном порядке (с учетом внешних ключей)
        database.create_tables([Discipline, Specialty, WorkProgram], safe=True)
        print("База данных успешно инициализирована")
        print(f"Файл БД: {DB_PATH}")
        print("Созданные таблицы: discipline, specialty, work_program")
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
    finally:
        database.close()


# Точка входа для инициализации БД
if __name__ == "__main__":
    init_db()