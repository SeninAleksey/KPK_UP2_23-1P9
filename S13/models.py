import os
import re
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
    Check,
)

DB_PATH = os.path.join(os.path.dirname(__file__), "work_program_service.db")

database = SqliteDatabase(DB_PATH)


class BaseModel(Model):
    class Meta:
        database = database


class Discipline(BaseModel):
    """Внешняя сущность — дисциплина из Discipline Service."""
    id = AutoField(primary_key=True)
    name = CharField(max_length=200, unique=True)
    code = CharField(max_length=20, unique=True)
    is_active = BooleanField(default=True)

    class Meta:
        table_name = "discipline"


class Specialty(BaseModel):
    """Внешняя сущность — специальность из Specialty Service."""
    id = AutoField(primary_key=True)
    name = CharField(max_length=200, unique=True)
    code = CharField(max_length=20, unique=True)
    is_active = BooleanField(default=True)

    class Meta:
        table_name = "specialty"


class WorkProgram(BaseModel):
    """Рабочая программа дисциплины.
    Реализует связь многие-ко-многим между дисциплиной и специальностью."""
    id = AutoField(primary_key=True)

    discipline = ForeignKeyField(
        Discipline, backref="work_programs", on_delete="CASCADE", column_name="discipline_id"
    )
    specialty = ForeignKeyField(
        Specialty, backref="work_programs", on_delete="CASCADE", column_name="specialty_id"
    )

    file_url = CharField(max_length=500)
    file_name = CharField(max_length=200, constraints=[Check("length(file_name) >= 1")])
    file_size = IntegerField(default=0, constraints=[Check("file_size >= 0")])

    version = CharField(max_length=20, default="1.0", constraints=[Check("length(version) >= 1")])

    approved_by = CharField(max_length=200, null=True)
    approval_date = DateField(null=True)
    description = CharField(max_length=1000, default="")

    is_active = BooleanField(default=True)
    created_at = DateTimeField(default=datetime.now)
    updated_at = DateTimeField(default=datetime.now)

    class Meta:
        table_name = "work_program"
        indexes = (
            (("discipline", "specialty", "version"), True),
        )

    def save(self, *args, **kwargs):
        # updated_at обновляется только при изменении существующей записи
        if self.id is not None:
            self.updated_at = datetime.now()
        return super().save(*args, **kwargs)

    @classmethod
    def soft_delete(cls, work_program_id: int) -> bool:
        """Мягкое удаление: is_active = False.
        Возвращает True если деактивировано, иначе False."""
        try:
            updated = cls.update(is_active=False).where(
                (cls.id == work_program_id) & (cls.is_active == True)
            ).execute()
            return updated > 0
        except Exception:
            return False

    @classmethod
    def get_list(cls, discipline_id=None, specialty_id=None, version=None,
                 is_active=None, approved_by=None, limit=100, offset=0):
        """Получить список рабочих программ с фильтрацией по параметрам из doc.md."""
        query = cls.select()
        if discipline_id is not None:
            query = query.where(cls.discipline_id == discipline_id)
        if specialty_id is not None:
            query = query.where(cls.specialty_id == specialty_id)
        if version is not None:
            query = query.where(cls.version == version)
        if is_active is not None:
            query = query.where(cls.is_active == is_active)
        if approved_by is not None:
            query = query.where(cls.approved_by.contains(approved_by))
        limit = max(1, min(100, limit))
        offset = max(0, offset)
        return list(query.limit(limit).offset(offset))

    @staticmethod
    def validate_version(version: str) -> bool:
        """Проверить формат версии X.Y."""
        return bool(re.match(r'^\d+\.\d+$', version))

    @staticmethod
    def validate_url(url: str) -> bool:
        """Проверить что строка является валидным URL."""
        return url.startswith("http://") or url.startswith("https://")


def init_db():
    """Инициализация базы данных: создаёт таблицы и тестовые данные."""
    try:
        database.connect()
        database.create_tables([Discipline, Specialty, WorkProgram], safe=True)

        if not Discipline.select().exists():
            d1 = Discipline.create(name="Математика", code="MATH")
            d2 = Discipline.create(name="МДК 01.01", code="MDK0101")

            s1 = Specialty.create(name="Информационные системы и программирование", code="09.02.07")
            s2 = Specialty.create(name="Программирование в компьютерных системах", code="09.02.03")

            WorkProgram.create(
                discipline=d1,
                specialty=s1,
                file_url="https://example.com/programs/math_wp_v1.pdf",
                file_name="math_wp_v1.pdf",
                file_size=1024,
                version="1.0",
                description="Рабочая программа дисциплины Математика для СПО",
            )
            WorkProgram.create(
                discipline=d2,
                specialty=s1,
                file_url="https://example.com/programs/mdk0101_wp_v2.pdf",
                file_name="mdk0101_wp_v2.pdf",
                file_size=2048,
                version="2.0",
            )
            WorkProgram.create(
                discipline=d1,
                specialty=s2,
                file_url="https://example.com/programs/math_wp_v1_s2.pdf",
                file_name="math_wp_v1_s2.pdf",
                version="1.0",
            )

        print("База данных успешно инициализирована")
        print(f"Файл БД: {DB_PATH}")
        print("Созданные таблицы: discipline, specialty, work_program")
    except Exception as e:
        print(f"Ошибка при инициализации базы данных: {e}")
    finally:
        database.close()


if __name__ == "__main__":
    init_db()
